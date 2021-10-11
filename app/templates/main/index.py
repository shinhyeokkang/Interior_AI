# file name : index.py
# pwd : /project_name/app/main/index.py
 
from flask import Blueprint, request, render_template, flash, redirect, url_for,Flask, request, jsonify
from flask import current_app as app
# 추가할 모듈이 있다면 추가
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from bson.json_util import dumps, loads
import pandas as pd

from PIL import Image
from NCF import Ncf
from Reco import Recommendation



# data 로드
ncf = Ncf()
cnn = Recommendation()
tmp_list = []
list_results = []
master_dict = {}
df = pd.DataFrame(columns = ['0','1','2','3','Item_id','Item_url', 'Title', 'Company'])
 
main= Blueprint('main', __name__, url_prefix='/')
 
@main.route('/', methods=['GET'])
def index():
    # /main/index.html은 사실 /project_name/app/templates/main/index.html을 가리킵니다.
    return render_template('/shop/shop.html')


#파일 업로드 처리
@main.route('/fileUpload', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        
        global df
        df.drop_duplicates(inplace=True,ignore_index = True)
        
        #방사진 분석
        f = request.files['file']#저장할 경로 + 파일명
        f.save(f'uploads/{secure_filename(f.filename)}') # /upload 폴더에 저장
        image = Image.open('/home/jmkim/capstone/flask/uploads/'+f.filename)
        roomlist = list(cnn.reco_items(image,New=True).loc[:,'Item_url'])#리턴: Item_url
        print(roomlist)
        
        
        #item분석
        item = request.form['itemlist']
        item_id_list = list(map(int, item.split(" ")[1:]))#공백제거
        #ncf
        ncflist = ncf.reco_items(item_id_list, 30)#리턴: Item_id
        #cnn
        predVal = df[df['Item_id'].isin(item_id_list)].iloc[:,:4].values
        cnnlist = list(cnn.reco_items(predVal,New=False).loc[:,'Item_url'])#리턴: Item_url 
        

        
    return render_template('/shop/reco.html')#, ncf=ncflist,room=roomlist)
    
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
    results = collection.find({"Auto":queryName},{'_id':0,'0':1,'1':1,'2':1,'3':1,'Item_id':1,'Item_url':1, 'Title':1, 'Company':1})
    client.close()
    #print(results, "find 결과 출력")
    #NCF 및 CNN 학습용 Dict에 추가 (Json 형식 그대로 유지, 추후 delete시 검색 삭제 용이하게)

    
    list_results = list(results)
    #print(list_results, "리스트 씌운 결과\n")
    '''
    for mongo_doc in results:
        # mongo_doc is a <class 'dict'> returned from the async mongo driver, in this acse motor / pymongo.
        # result of executing a simple find() query.

        json_string = dumps(mongo_doc)
        # serialize the <class 'dict'> into a <class 'str'> 
        back_to_dict = loads(json_string)
        # to unserialize, thus return the string back to a <class 'dict'> with the original 'ObjectID' type.
        master_dict.update(back_to_dict)
        #데이터 프레임 생성

    print(back_to_dict)
    print(master_dict)
    df = pd.DataFrame(back_to_dict)

    '''
    df_new = pd.DataFrame(list_results)
    global df
    df = pd.concat([df,df_new],ignore_index=True)
    #print("DataFrame 입니다\n", df, "DataFrame 입니다\n")
   
   # 사진파일 item_url로 검색해서 같이 보내줘야함 
    
    return jsonify(list_results[0])

@main.route('/shop', methods = ['GET'])
def test():
    return render_template('/shop/shop.html')

