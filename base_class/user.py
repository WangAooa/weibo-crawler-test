from util.util import *

class User:
    def __init__(self):
        self.id = ''

        self.screen_name = ''

        self.statuses_count = ''
        self.description = ''
        self.gender = ''
        self.svip = ''
        self.follow_count = ''
        self.followers_count = ''

    def fill_data(self, data):
        self.id = data['id']
        self.screen_name = data['screen_name']
        self.statuses_count = data['statuses_count']
        self.description = data['description']
        self.gender = data['gender']
        self.svip = data['svip']
        self.follow_count = data['follow_count']
        self.followers_count = data['followers_count']


    def __str__(self):
        """打印微博用户信息"""
        result = ''
        result += u'用户昵称: %s\n' % self.screen_name
        result += u'用户id: %s\n' % self.id

        result += u'微博数: %s\n' % self.statuses_count
        result += u'简介: %s\n' % self.description
        result += u'性别: %s\n' % self.gender
        result += u'svip: %s\n' % self.svip
        result += u'关注数: %s\n' % self.follow_count

        result += u'粉丝数: %s\n' % self.followers_count
        return result

    def save_info(self,dir):
        dir_path = dir + "data/{}/".format(self.id)
        create_dir(dir_path)
        with open(dir_path + "user_info.txt", "w",encoding='utf-8') as f:
            f.write(self.__str__())
