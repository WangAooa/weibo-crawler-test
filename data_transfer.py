import time

import pandas as pd
import os
import datetime
from tqdm import tqdm

file_path = "D:/work/GithubDesktopWork/weibo-crawler/dataset/"

class Weibo:
    def __init__(self, user_id, file_dir):
        self.user_id = user_id

        self.origin_user_list = []
        self.origin_content_list = []
        self.origin_position_list = []
        self.origin_time_list = []
        self.origin_weiboId_list= []

        self.forwarding_user_list = []
        self.forwarding_reason_list = []
        self.forwarding_content_list = []
        self.forwarding_position_list = []
        self.forwarding_time_list = []
        self.forwarding_weiboId_list = []

        self.temp_data_start_index = 0

        self.file_path = file_dir + "{}/{}.txt".format(user_id, user_id)
        self.origin_path = file_dir + "{}/{}_origin.csv".format(user_id, user_id)
        self.forwarding_path = file_dir + "{}/{}_forwarding.csv".format(user_id, user_id)

    #读取txt文件数据
    def read(self):
        f = open(self.file_path, encoding='utf-8')
        self.txt = f.readlines()
        f.close()

    #对于每一条微博，查看是否为原创，赋值到list
    def assign(self, data):
        if(data[0][:4] == '微博内容'):
            self.origin_user_list.append(self.user_id)
            self.origin_content_list.append(data[0].split(':', 2)[1].lstrip().strip())
            self.origin_weiboId_list.append(data[1].split('：', 2)[1].lstrip().strip())
            position = data[5].split('：', 2)[1].lstrip().strip()
            if(len(position) > 0):
                position = position.split(' ', 2)
                if(len(position)) == 1:
                    position = position[0]
                else:
                    position = position[1]

            self.origin_position_list.append(position)

            time = data[6].split('：', 2)[1].lstrip()
            if(len(time) > 0):
                time = time.split(' ', 2)[0]
            self.origin_time_list.append(datetime.datetime.strptime(time, '%Y-%m-%d'))
        else:
            self.forwarding_user_list.append(self.user_id)
            self.forwarding_reason_list.append(data[0].split(':', 2)[1].lstrip().strip())
            self.forwarding_content_list.append(data[1].split(':', 2)[1].lstrip().strip())
            self.forwarding_weiboId_list.append(data[2].split('：', 2)[1].lstrip().strip())
            position = data[6].split('：', 2)[1].lstrip().strip()
            if(len(position) > 0):
                position = position.split(' ', 2)
                #position 可能是”发布于 北京“， 也可能是”北京“
                if(len(position)) == 1:
                    position = position[0]
                else:
                    position = position[1]
            self.forwarding_position_list.append(position)

            time = data[7].split('：', 2)[1].lstrip()
            if(len(time) > 0):
                time = time.split(' ', 2)[0]
            self.forwarding_time_list.append(datetime.datetime.strptime(time, '%Y-%m-%d'))


    #获取下一条微博数据
    def getnext(self):
        if(self.temp_data_start_index >= len(self.txt)):
            return None

        next_end_index = self.temp_data_start_index
        while(next_end_index < len(self.txt) and self.txt[next_end_index].strip() != ''):
            next_end_index+=1
        return_data = self.txt[self.temp_data_start_index: next_end_index]
        self.temp_data_start_index = next_end_index + 1
        return return_data

    #对于txt文件中的所有微博，批量处理，全部添加进入list
    def get_all_content(self):
        self.read()
        temp_data = self.getnext()
        while(temp_data is not None):
            # print(temp_data)
            self.assign(temp_data)
            temp_data = self.getnext()

    #list数据的保存
    def save(self):
        origin_pd_data = pd.DataFrame({
            "user_id": self.origin_user_list,
            "微博_id" : self.origin_weiboId_list,
            "微博内容": self.origin_content_list,
            "微博位置": self.origin_position_list,
            "发布时间": self.origin_time_list,
        })
        origin_pd_data.to_csv(self.origin_path, index=False, encoding='utf-8')


        forward_pd_data = pd.DataFrame({
            "user_id" : self.forwarding_user_list,
            "微博_id" : self.forwarding_weiboId_list,
            "转发理由": self.forwarding_reason_list,
            "转发内容": self.forwarding_content_list,
            "微博位置": self.forwarding_position_list,
            "发布时间" : self.forwarding_time_list
        })
        forward_pd_data.to_csv(self.forwarding_path, index = False, encoding='utf-8')

    #外部调用方法，读数据->对于每条数据的处理->存储
    def get_content_and_save(self):
        self.get_all_content()
        self.save()




#运行方法，对文件夹下所有文件都生成csv文件
path_list = os.listdir(file_path)
for temp_path in tqdm(os.listdir(file_path)):
    if not os.path.exists(file_path + temp_path + "/" + temp_path + "_forwarding.csv"):
        print(temp_path)
        weibo = Weibo(temp_path, file_path)
        weibo.get_content_and_save()
    else:
        print(1)