import requests
import os
import json
import sqlite3
from pymongo import MongoClient
import certifi

#youtube to mongodb

#youtube data api

api_key = 'AIzaSyD022uHitUxix21wfuhvOHbypjoKsyuOsA'
chart = 'mostPopular'
maxresults = 50
part = 'snippet,statistics'
search_url = f"https://www.googleapis.com/youtube/v3/videos?part={part}&maxResults={maxresults}&chart={chart}&regionCode=kr&key={api_key}"

#get data from youtube
def get_youtube_data(search_url):
    item_list= []
    raw_data = requests.get(search_url)
    res = json.loads(raw_data.text)
    try:
        nextPageToken = res['nextPageToken']
    except KeyError:
        nextPageToken = None
    for item in res['items']:
        item_list.append(item)
    while (nextPageToken):
        next_url = f"https://www.googleapis.com/youtube/v3/videos?part={part}&maxResults={maxresults}&chart={chart}&regionCode=kr&key={api_key}&pageToken={nextPageToken}"
        search = requests.get(next_url)
        res1 = json.loads(search.text)
        for item in res1['items']:
            item_list.append(item)
        try:
            nextPageToken = res1['nextPageToken']
        except KeyError:
            break
    return item_list

items = get_youtube_data(search_url)

#mongodb info

HOST = 'cluster0.vfnqr.mongodb.net'
USER = 'bunnghak'
PASSWORD = '1234'
DATABASE_NAME = 'myFirstDatabase'
COLLECTION_NAME = 'youtube_project'
MONGO_URI = f"mongodb+srv://{USER}:{PASSWORD}@{HOST}/{DATABASE_NAME}?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI,tlsCAFile=certifi.where())
database = client[DATABASE_NAME]
collection = database[COLLECTION_NAME]

# insert mongodb
def mongodb_insert(db):
    collection.delete_many({})
    post = collection.insert_many(db)
    return post

mongodb_insert(items)

col_list = {'id':1,'snippet.publishedAt':1,'snippet.title':1,'snippet.categoryId':1,'statistics':1}
doc_1 = collection.find({},col_list)
youtube_list = []
for i in doc_1:
    youtube_list.append(i)

#sqlite

DB_FILENAME = 'youtube_popular.db'
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
#insert sqlite
for data in youtube_list:
    #각 테이블 별 쿼리 작성.
    snippet = "INSERT INTO snippet(id,publishedAt,title,categoryId) VALUES (?,?,?,?);"
    statistics = "INSERT INTO statistics(id,viewCount,likeCount,dislikeCount,favoriteCount,commentCount) VALUES (?,?,?,?,?,?);"
    
    #라벨 중복 여부 체크 후 커밋
    try:
        snip_list = cur.execute("SELECT id FROM snippet;").fetchall()
        snip_data = data['id'],data['snippet']['publishedAt'],data['snippet']['title'],data['snippet']['categoryId'] #insert data

        if (data['id'],) not in snip_list:
            cur.execute(snippet,snip_data)
            conn.commit()

        #유저 중복 여부 체크 후 커밋
        stat_list = cur.execute("SELECT id FROM statistics;").fetchall()
        stat_data = data['id'],data['statistics']['viewCount'],data['statistics']['likeCount'],data['statistics']['dislikeCount'],data['statistics']['favoriteCount'],data['statistics']['commentCount'] #insert data


        if (data['id'],) not in stat_list:
            cur.execute(statistics,stat_data)
            conn.commit()
    except KeyError:
        continue

conn.commit()
