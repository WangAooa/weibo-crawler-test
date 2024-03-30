import random
import logging
import logging.config
import sys
import pandas as pd
import numpy as np
import requests
import time
from util.util import *
# print(sys.path)
from base_class.user import *

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
cookie = "_T_WM=8b231d9b068f232b0192fc8bf7151671; XSRF-TOKEN=0fec27; WEIBOCN_FROM=1110006030; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WW-YeTu-qh4H34TngOL4inC5JpX5K-hUgL.FoMNeh-cSK-ES0q2dJLoI7yPqg4rBgvaqBtt; MLOGIN=1; SCF=ArbxV094DLW9CGAftO3xt8-j4H9zln0zgPLdUdewyyhD3WEy7jaUyJn67vIdKCjag1Cyba8c1DFfjh45LeSAJlM.; SUB=_2A25O_kHTDeRhGeFJ61cX9SvOzDqIHXVqAW-brDV6PUJbktANLVXakW1NfKYuS4XJWM4CchsnVC3HVKWrdnYc_Dqy; SSOLoginState=1677341059; ALF=1679933059; M_WEIBOCN_PARAMS=luicode=20000174&uicode=20000174; mweibo_short_token=aa0e27e503"
# cookie = ""
headers = {"User_Agent": user_agent, "Cookie": cookie}

# id = 6274764018
# id = 7248131858
# id = 1900232583
id_list = [1900232583, 5748512242]
id_list = [1900232583]
sleep_time = 2
expand_num = 10000
expand_continue = True
data_dir = './weiboData_10000/'

create_dir(data_dir)
create_dir(data_dir + "basic_info/")
create_dir(data_dir + "data/")

# logging.basicConfig(filename=data_dir + "basic_info/relation.log", level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
logging.config.fileConfig("./logging.conf")
logger = logging.getLogger('spider')

#获取用户数据的index,若找不到返回-1
def contain_user_info(data):
    return 'card_group' in data and len(data['card_group']) > 0 and 'user' in data['card_group'][0]
def find_user_index(card_info_list):
    index_list = []
    for i in range(len(card_info_list)-1, -1, -1):
        if contain_user_info(card_info_list[i]):
            index_list.append(i)
    return index_list

#判断用户是否发布过微博
def test_have_weibo(id):
    url = "https://m.weibo.cn/api/container/getIndex?containerid=100505{}".format(id)
    data= requests.get(url,  headers=headers)
    if data.status_code == 200:
        json_data = data.json()
        if 'data' in json_data and 'userInfo' in json_data['data'] and 'statuses_count' in json_data['data']['userInfo'] and json_data['data']['userInfo']['statuses_count'] > 0:
            return True
    return False

#获取用户的全部关注
def get_all_follow(id):
    id_list, name_list = [], []
    page = 1
    while(True):
        url = "http://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{}&page={}".format(id, page)
        # print(url)
        data= requests.get(url,  headers=headers)
        if data.status_code != 200:
            logger.error("被ban,需要等待")
            sys.exit()
        data = data.json()

        if not data['ok']:
            break
        card_info_list = data['data']['cards']
        index_list = find_user_index(card_info_list)

        for index in index_list:
            user_info_list = card_info_list[index]['card_group']
            for temp_user_info in user_info_list:

                if "user" not in temp_user_info or temp_user_info["user"] == None:
                    continue
                else:
                    # if temp_user_info['user']['id'] not in id_list:
                    id_list.append(temp_user_info['user']['id'])
                    name_list.append(temp_user_info['user']['screen_name'])

        page += 1
        time.sleep(random.random() * sleep_time)

    return len(id_list), id_list, name_list

#爬取用户的全部粉丝
def get_fans(id):
    id_list, name_list = [], []
    page = 0
    while(True):
        url = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{}&since_id={}".format(id, page)
        # print(url)
        data= requests.get(url,  headers=headers)
        if data.status_code != 200:
            logger.error("被ban,需要等待")
            sys.exit()
        data = data.json()

        if not data['ok']:
            break
        card_info_list = data['data']['cards']
        index_list = find_user_index(card_info_list)

        for index in index_list:
            user_info_list = card_info_list[index]['card_group']
            for temp_user_info in user_info_list:
                if "user" not in temp_user_info or temp_user_info["user"] == None:
                    continue
                else:
                    # if temp_user_info['user']['id'] not in id_list:
                    id_list.append(temp_user_info['user']['id'])
                    name_list.append(temp_user_info['user']['screen_name'])

        page += len(user_info_list)
        time.sleep(random.random()*sleep_time)

    return len(id_list), id_list, name_list

#获取互关列表
def get_co_user(fans_id_list, fans_name_list,follow_id_list ):
    co_id_list, co_name_list = [], []
    for i in range(len(fans_id_list)):
        if (fans_id_list[i] in follow_id_list) and (fans_id_list[i] not in co_id_list):
            if test_have_weibo(fans_id_list[i]):
                co_id_list.append(fans_id_list[i])
                co_name_list.append(fans_name_list[i])
                time.sleep(random.random()*sleep_time)
            else:
                logger.info("get_co_user method, {}---{} no weibo".format(fans_id_list[i], fans_name_list[i]))
    return co_id_list, co_name_list

#获取互关列表 get_co_user方法的封装
def get_correlations(id):
    follow_lenl, follow_id_list, follow_name_list = get_all_follow(id)
    fan_len, fan_id_list, fan_name_list = get_fans(id)
    co_id_list, co_name_list = get_co_user(fan_id_list, fan_name_list, follow_id_list)
    return co_id_list, co_name_list

#判断是否为链接问题
def test_connection():
    url = "https://m.weibo.cn/api/container/getIndex?containerid=2302836074526225_-_INFO"
    data= requests.get(url,  headers=headers)
    return data.status_code == 200

def get_user(id):
    url = "https://m.weibo.cn/api/container/getIndex?containerid=100505{}".format(id)
    data = requests.get(url, headers=headers)
    if data.status_code != 200:
        logger.error("被ban,需要等待")
        sys.exit()
    data = data.json()
    temp_user = User()
    if 'data' in data and 'userInfo' in data['data']:
        temp_user.fill_data(data['data']['userInfo'])
    else:
        if test_connection():
            logger.error("user : {} is can not get userinfo, but test_connection is OK".format(id))
            return None
        logger.error("{} userinfo not exist".format(id))
        sys.exit()
    return temp_user

def cross_correlation_save(co_id_list, co_name_list, origin_user, save_dir):
    with open(save_dir + "basic_info/user_id_adj.txt", 'a+',encoding='utf-8') as f:
        f.write(str(origin_user.id))
        for temp_id in co_id_list:
            f.write("\t{}".format(temp_id))
        f.write("\n")

    pd_follows_data = {'id': co_id_list, 'name': co_name_list}
    pd_follows_data = pd.DataFrame(pd_follows_data)

    # create_dir(save_dir + "data/{}".format(origin_id))
    pd_follows_data.to_csv(save_dir + "data/{}/co_follows.csv".format(origin_user.id), index=False)

    merge_pd_data = pd.DataFrame({'id': [origin_user.id] + co_id_list,
                                  'name': [origin_user.screen_name] + co_name_list})

    # 原数据加载及合并
    if os.path.exists(save_dir + "basic_info/user_id_name.csv"):
        data = pd.read_csv(save_dir + "basic_info/user_id_name.csv")
        merge_pd_data = pd.concat([data, merge_pd_data], ignore_index=True)
        # drop duplicated
        merge_pd_data.drop_duplicates('id', inplace=True)

    merge_pd_data.to_csv(save_dir + "basic_info/user_id_name.csv", index=False)

    # 返回现有观测用户个数
    return len(merge_pd_data)

# print(get_user(id))
# co_id_list, co_name_list = get_correlations(id)


for id in id_list:
    data_dir = data_dir + "{}/".format(id)

    create_dir(data_dir)
    create_dir(data_dir + "basic_info/")
    create_dir(data_dir + "data/")

    candidate_id_list = [id]
    now_num = 0

    #加载已经扩张的用户
    if expand_continue:
        candidate_id_list = np.load(data_dir + "basic_info/candidate_id_list.npy").tolist()
        now_num, candidate_id_list = candidate_id_list[-1], candidate_id_list[:-1]
        print("now expanded : {}, total candidate sum : {}".format(now_num, len(candidate_id_list)))

    start_time = time.time()
    while now_num < expand_num and len(candidate_id_list) > 0:

        try:
            temp_id = candidate_id_list[0]
            candidate_id_list = candidate_id_list[1:]

            temp_user = get_user(temp_id)
            if temp_user is None:
                continue

            temp_user.save_info(data_dir)
            logger.info("user {}---{}------{}".format(now_num, temp_user.id, temp_user.screen_name))
            logger.info('*' * 100)

            #获取互关用户
            temp_co_id_list, temp_co_name_list = get_correlations(temp_id)
            #日志记录互关用户信息
            for index in range(len(temp_co_id_list)):
                logger.info("co_relation_user : {}-----{}".format(temp_co_id_list[index], temp_co_name_list[index]))

            #互关用户存储
            temp_count = cross_correlation_save(temp_co_id_list, temp_co_name_list, temp_user, data_dir)
            logger.info("cross_correlation_save finished, total_user_num : {}".format(temp_count))

            # 扩张用户添加进入候选队列
            pre_len = len(candidate_id_list)
            for index in range(len(temp_co_id_list)):
                temp_co_id = temp_co_id_list[index]
                if (temp_co_id not in candidate_id_list) and (not os.path.exists(data_dir + "data/{}/co_follows.csv".format(temp_co_id))):
                    candidate_id_list.append(temp_co_id)
                else:
                    logger.info("user {} is filtered".format(temp_co_name_list[index]))
            logger.info("continue expand num : {}, all_coorelation_num : {}".format(len(candidate_id_list) - pre_len, len(temp_co_id_list)))

            now_num += 1

            # 候选id的存储，防止中途停止
            np.save(data_dir + "basic_info/candidate_id_list.npy", np.array(candidate_id_list + [now_num]))
            logger.info("len candidate_id_list : {}".format(len(candidate_id_list)))


            if now_num % 10 == 0:
                logger.info("sleep")
                time.sleep(random.randint(240, 480))

            elif now_num % 100 == 0:
                logger.info("sleep")
                time.sleep(random.randint(600, 1200))

        except Exception as e:
            logger.error(e)
            time.sleep(random.randint(3600, 4000))
            if candidate_id_list[0] != temp_id:
                logger.error("add temp_id {}".format(temp_id))
                candidate_id_list = [temp_id] + candidate_id_list

    # time.sleep(random.randint(1200, 1800))






