import pandas as pd
import sqlite3
import os
from AI_05_section3_project.LM.youtube_to_db.youtube_to_mongodb import DB_FILEPATH

#load data
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

#model

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split

pipe = make_pipeline(
    StandardScaler(),
    LinearRegression()
)
model = pipe.fit(x,y)
model_LR = model.named_steps['linearregression']
print(model_LR.intercept_)