# file name : index.py
# pwd : /project_name/app/main/index.py
 
from flask import Blueprint, request, render_template, flash, redirect, url_for,Flask, request, jsonify
from flask import current_app as app
# 추가할 모듈이 있다면 추가
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from PIL import Image
from NCF import Ncf
from Reco import Recommendation



# data 로드
ncf = Ncf()
reco = Recommendation()
tmp_list = []
 
main= Blueprint('main', __name__, url_prefix='/')
 
@main.route('/', methods=['GET'])
def index():
    # /main/index.html은 사실 /project_name/app/templates/main/index.html을 가리킵니다.
    return render_template('/main/index.html')


#파일 업로드 처리
@main.route('/fileUpload', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
       
        f = request.files['file']
        #저장할 경로 + 파일명
        f.save(f'uploads/{secure_filename(f.filename)}') # /upload 폴더에 저장
        print(f'uploads/{secure_filename(f.filename)}')
        print(type(f))
        print(f.filename)
        image = Image.open('/home/jmkim/capstone/flask/uploads/'+f.filename)
        #temp = request.form['num']
        #tmp_list = temp.split(",")
        testlist = reco.newimage(image)
        #recolist = ncf.reco_items(tmp_list, 30)
        print(testlist)
    return render_template('/shop/reco.html')#, data=recolist)
    
@main.route('/json', methods = ['GET'])
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

@main.route('/query', methods = ['POST'])
def query():
    #프론트에서 query 할 Auto를 받아오는 코드
    query = request.get_json()
    queryName = query['Auto']
    print(queryName)
    #itemlist 를 MongoDB에서 받아오는 쿼리
    client = MongoClient('mongodb://localhost:27017/')
    db = client.ItemDB
    collection = db.ItemCollections
    results = collection.find({"Auto":queryName},{"_id":0,"Item_url":1, "Title":1, "Company":1,"Auto":1})
    client.close()
    print(results)
    list_results = list(results)
    #for result in results:
    #    list_results.append(result)    
    
   # 사진파일 item_url로 검색해서 같이 보내줘야함 
    #print(list_results[0])
    #NCF 학습용 리스트에 추가
    tmp_list.append(list_results[0]['Item_url'])
    print(tmp_list)
    #print(type(list_results))
    return jsonify(list_results[0])

@main.route('/shop', methods = ['GET'])
def test():
    return render_template('/shop/shop.html')

