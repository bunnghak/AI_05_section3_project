import pandas as pd
import sqlite3
import os
import json
import requests
from AI_05_section3_project.LM.learning_machine import  model

#youtube api
api_key = 'AIzaSyD022uHitUxix21wfuhvOHbypjoKsyuOsA'
chart = 'mostPopular'
maxresults = 50
part = 'snippet,statistics'
id='id'
word='asmr'
search_url = f"https://www.googleapis.com/youtube/v3/search?part={id}&maxResults={maxresults}&key={api_key}&q={word}&type=video"

#get id from search word videos
search = requests.get(search_url)
res = json.loads(search.text)
id_list = []
for item in res["items"]:
    id_list.append(item["id"]["videoId"])


#get statistics from id
data_stat = []
for s in id_list:
    video_url = f"https://www.googleapis.com/youtube/v3/videos?part={part}&id={s}&key={api_key}"
    raw_data = requests.get(video_url)
    res1 = json.loads(raw_data.text)
    data_stat.append(res1["items"])

#일단 id를 기반으로 데이터를 뽑아오는 것까지만 완료. 이후 이걸 정제해서 모델에 넣어서 돌려보고 유사값을 가진 영상을 픽업하는 형태로 마무리.
#sqlite 
DB_FILENAME = 'search_keyword.db'
DB_FILEPATH = os.path.join(os.getcwd(), DB_FILENAME)
conn = sqlite3.connect(DB_FILEPATH)
cur = conn.cursor()

#reset table
cur.execute("DROP TABLE IF EXISTS snippet;")
cur.execute("DROP TABLE IF EXISTS statistics;")
conn.commit()
#snippet table set
cur.execute("""
CREATE TABLE snippet(
    id VARCHAR(20) NOT NULL PRIMARY KEY,
    publishedAt VARCHAR(100),
    title VARCHAR(100),
    categoryId INTEGER
    );
""")
#statistic table set
cur.execute("""
CREATE TABLE statistics(
    id VARCHAR(20) NOT NULL PRIMARY KEY,
    viewCount INTEGER,
    likeCount INTEGER,
    dislikeCount INTEGER,
    favoriteCount INTEGER,
    commentCount INTEGER
    );
""")
conn.commit()

#insert sqlite search_keyword

for data in data_stat:
    #각 테이블 별 쿼리 작성.
    snippet = "INSERT INTO snippet(id,publishedAt,title,categoryId) VALUES (?,?,?,?);"
    statistics = "INSERT INTO statistics(id,viewCount,likeCount,dislikeCount,favoriteCount,commentCount) VALUES (?,?,?,?,?,?);"
    
    #라벨 중복 여부 체크 후 커밋
    try:
        snip_list = cur.execute("SELECT id FROM snippet;").fetchall()
        snip_data = data[0]['id'],data[0]['snippet']['publishedAt'],data[0]['snippet']['title'],data[0]['snippet']['categoryId'] #insert data

        if (data[0]['id'],) not in snip_list:
            cur.execute(snippet,snip_data)
            conn.commit()

        #유저 중복 여부 체크 후 커밋
        stat_list = cur.execute("SELECT id FROM statistics;").fetchall()
        stat_data = data[0]['id'],data[0]['statistics']['viewCount'],data[0]['statistics']['likeCount'],data[0]['statistics']['dislikeCount'],data[0]['statistics']['favoriteCount'],data[0]['statistics']['commentCount'] #insert data


        if (data[0]['id'],) not in stat_list:
            cur.execute(statistics,stat_data)
            conn.commit()
    except KeyError:
        continue

conn.commit()


db_list = cur.execute("""
SELECT * FROM snippet s
INNER JOIN statistics st ON s.id  == st.id
""").fetchall()
df = pd.read_sql_query("""
SELECT * FROM snippet s
INNER JOIN statistics st ON s.id  == st.id
""",conn)
y = df['likeCount']
x = df.drop(['publishedAt','likeCount','id','title','favoriteCount'],axis=1)
x_pred = model.predict(x)
num = 0
val = []
for i in x_pred:
    total = i
    val.append(total)
    num+=1
df['total'] = val
df['predict'] = x_pred
top_5 = df.sort_values(by='predict',ascending=False).head()

#get top5 thumbnail_url
img_list= []
id = top_5.iloc[:,0]
for i in id:
    for data in data_stat:
        if i == data[0]['id']:
            img_list.append(data[0]['snippet']['thumbnails']['medium']['url'])

top_5['img'] = img_list
titles = list(top_5['title'])