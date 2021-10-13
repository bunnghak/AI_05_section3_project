from flask import Flask,render_template,request
app = Flask(__name__)

@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/result',methods=['GET'])
def result(keyword=None):
    temp = request.args.get('keyword')
    word = str(temp)
    from AI_05_section3_project.LM.api_model import youtube,search_from_api
    url = youtube(word)
    thumbnail,title,id_list= search_from_api(url)
    return render_template('result.html', thumbnail=thumbnail,title=title,id=id_list)