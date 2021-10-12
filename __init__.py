from flask import Flask,render_template
from AI_05_section3_project.LM.api_model import titles,img_list
app = Flask(__name__)

@app.route('/',methods=['GET'])
def index():
    thumbnail = img_list
    title = titles
    return render_template('index.html', thumbnail=thumbnail,title=title)