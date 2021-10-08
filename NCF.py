# 유사 유저 탐색 코드
from collections import Counter
import numpy as np
import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

# 2. 모델 불러오기
#from tf.keras.models import load_model
model = tf.keras.models.load_model('ncf_model_home1.h5')

# 3. 모델 사용하기

#inputlist = [4398,7631,11383,13123,19865,19866,20530]

class Ncf():
    
    def reco_items(self,inputlist, topnum):
        sumdict = {}

        for initem in inputlist:
            # user 여러명에 대한 한 item prediction 예시
            user_id = np.arange(33044).reshape(-1,1) # 전체 유저의 수
            user_candidate_item = initem # 앞에 8개가 그대로 유지되어야함
            item_input = np.full(len(user_id), user_candidate_item, dtype='int32').reshape(-1,1) #[0,0,0,0,0] 만듬

            predictions = model.predict([user_id, item_input])
            #print(predictions)

            predictions = predictions.flatten().tolist()
            #print(predictions)
            user_to_pre_score = {user[0]: pre for user, pre in zip(user_id, predictions)} # 후보 아이템 별 예측값
            #print(type(user_to_pre_score))
            sumdict = Counter(sumdict)+Counter(user_to_pre_score)

        print()
        print()
        sumdict = dict(sorted(sumdict.items(), key=lambda x: x[1], reverse=True)) #prediction 기준 내림차순
        #print(sumdict)
        matched_user_order = list(sumdict.keys())
        print('similar users:', matched_user_order[:10])

        #유사 유저들의 아이템 추천
        topten_users = matched_user_order[:10]

        sumdict2 = {}
        for inuser in topten_users:
            # user 한 명에 대한 모든 item prediction 예시
            user_id = inuser
            user_candidate_item = np.arange(59594).reshape(-1,1) # 전체 아이템의 수
            user_input = np.full(len(user_candidate_item), user_id, dtype='int32').reshape(-1,1) #[0,0,0,0,0] 만듬

            predictions = model.predict([user_input, user_candidate_item])
            #print(predictions)

            predictions = predictions.flatten().tolist()
            #print(predictions)
            item_to_pre_score = {item[0]: pre for item, pre in zip(user_candidate_item, predictions)} # 후보 아이템 별 예측값
            sumdict2 = Counter(sumdict2)+Counter(item_to_pre_score)

        print()
        print()
        sumdict2 = dict(sorted(sumdict2.items(), key=lambda x: x[1], reverse=True)) #prediction 기준 내림차순
        print(sumdict2)

        recommend_item_lst = list(sumdict2.keys())
        print('recommend:', recommend_item_lst[:topnum])
        
        return recommend_item_lst[:topnum]