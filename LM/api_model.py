import pandas as pd
import sqlite3
import os
import json
import requests

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
res = json.load(search)
id_list = []
for item in res["items"]:
    id_list.append(item["id"]["videoId"])


#get statistics from id
data_stat = []
for s in id_list:
    video_url = f"https://www.googleapis.com/youtube/v3/videos?part={part}&id={s}&key={api_key}"
    raw_data = requests.get(video_url)
    res1 = json.load(raw_data)
    data_stat.append(res1["items"])

#일단 id를 기반으로 데이터를 뽑아오는 것까지만 완료. 이후 이걸 정제해서 모델에 넣어서 돌려보고 유사값을 가진 영상을 픽업하는 형태로 마무리.
#sqlite 
DB_FILENAME = 'search_keyword.db'
DB_FILEPATH = os.path.join(os.getcwd(), DB_FILENAME)
conn = sqlite3.connect(DB_FILEPATH)
cur = conn.cursor()


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
