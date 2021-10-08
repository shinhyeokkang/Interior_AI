import tensorflow as tf
import pandas as pd
import numpy as np
from PIL import Image
from PIL import ImageFile
from pymongo import MongoClient
from scipy.spatial import distance
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)


    
    
# 2. 모델 불러오기
model = tf.keras.models.load_model('cnn_model_i0003.h5')

class Recommendation():
    def newimage(self,img):
        client = MongoClient('mongodb://localhost:27017/')
        db = client.ItemDB
        collection = db.ItemCollections
        results = collection.find({},{"_id":0,"0":1, "1":1, "2":1,"3":1,"Item_url":1})
        client.close()
        #수정중 데이터프레임으로바꺼야댐
        total_data = pd.DataFrame(list(results))
        print(total_data)
        
        print(total_data.isnull().values.any())
        data = []
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        Image.MAX_IMAGE_PIXELS = None
        
        image = img#Image.open('/home/jmkim/capstone/flask/uploads/tree.jpg')#받은이미지
        
        
        testi = Image.open('/home/jmkim/capstone/flask/uploads/tree.jpg')
        print(type(testi),"여기")
        
        
        image = image.resize((224,224))
        image = np.array(image, dtype='uint8')
        if image.shape != (224,224,3):
            if image.shape == (224,224,4):
                image = np.delete(image, 3, 2)
                print('before 224,224,4 to ', image.shape)
            elif image.shape == (224,224):
                temp = image[np.newaxis].swapaxes(0,1).swapaxes(1,2)
                image = np.append(temp, temp, axis=2)
                image = np.append(image, temp, axis=2)
                print('before 224,224 to ', image.shape)
        image = image/255
        data.append(image)
        data = np.array(data)
        
        pred = model.predict(data)
        print(pred[0])
        print('Done!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        return self.recommend_items(pred[0],total_data)
    
    
    
    def recommend_items(self,value,data):
        re = data.copy()
        re['Distance'] = 0
        print(value,"벨류야")
        print(data.iloc[0:10,0:4])
        for i in range(0,len(data)):
            re.loc[i,'Distance'] = distance.euclidean(value,re.iloc[i,0:4])
        re.sort_values(by=['Distance'], axis=0, inplace=True)
        return re