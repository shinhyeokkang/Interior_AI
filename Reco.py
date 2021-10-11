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
    def reco_items(self,imgOrVal,New):
        client = MongoClient('mongodb://localhost:27017/')
        db = client.ItemDB
        collection = db.ItemCollections
        results = collection.find({},{"_id":0,"0":1, "1":1, "2":1,"3":1,"Item_url":1})
        client.close()
        #수정중 데이터프레임으로바꺼야댐
        total_data = pd.DataFrame(list(results))
        #print(total_data)
        
        #print(total_data.isnull().values.any())
        if New:
            
            data = []
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            Image.MAX_IMAGE_PIXELS = None

            image = imgOrVal
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
            print(pred[0],' Reco.Newimage Predict Complete!')
            return self.cal_distance(pred[0],total_data)
        
        else:
            
            return self.cal_distance(imgOrVal[0],total_data)
    
    
    
    def cal_distance(self,value,data):
        re = data.copy()
        re['Distance'] = 0
        for i in range(0,len(data)):
            re.loc[i,'Distance'] = distance.euclidean(value,re.iloc[i,0:4])*10000
        re.sort_values(by=['Distance'], axis=0, inplace=True)
        print('Reco Distance Calculation Complete!')
        return re