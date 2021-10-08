from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from NCF import Ncf
app = Flask(__name__)
# data 로드
ncf = Ncf()

# 업로드 HTML 렌더링
@app.route('/')
@app.route('/upload')
def render_file():
    return render_template('upload.html')

#파일 업로드 처리
@app.route('/fileUpload', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        #저장할 경로 + 파일명
        f.save(f'uploads/{secure_filename(f.filename)}') # /upload 폴더에 저장
        print(f'uploads/{secure_filename(f.filename)}') 
        temp = request.form['num']
        tmp_list = temp.split(",")
        recolist = ncf.reco_items(tmp_list, 30)
        return render_template('reco.html', data=recolist)
    
@app.route('/json', methods = ['GET'])
def json_file():
    #itemlist 를 MongoDB에서 받아오는 쿼리
    client = MongoClient('mongodb://localhost:27017/')
    db = client.ItemDB
    collection = db.ItemCollections
    results = collection.find({},{"_id":0,"Auto":1})
    client.close()
    list_results = []
    for result in results:
        list_results.append(result['Auto'])
    
    #print(list_results)
    #print(type(list_results))
    return jsonify(list_results)
        
if __name__ == '__main__':
    #서버 실행
    app.run(host='0.0.0.0', debug = True)