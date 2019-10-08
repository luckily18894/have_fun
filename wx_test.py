# -*- coding=utf-8 -*-

import json
import requests


# https://www.jb51.net/article/145503.htm
class Almsg:
    # 初始化
    def __init__(self, msg):
        self.appid = 'wx87bfd829ef0e28f5'
        self.appsecret = '7eacf36968a51c58758152c374ab38bb'
        self.template_id = '977vJiTJ7jXwUc3ldDtPTd1ePoLN3B-y3aiMKrzt4NQ'
        self.access_token = ''
        self.msg = msg

    # 获取access_token
    def get_access_token(self, appid, appsecret):
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(str(appid), str(appsecret))
        r = requests.get(url)
        data = json.loads(r.text)
        access_token = data['access_token']
        self.access_token = access_token
        return self.access_token

    # 获取用户列表
    def get_user_list(self):
        if self.access_token == '':
            self.get_access_token(self.appid, self.appsecret)
        access_token = self.access_token
        url = 'https://api.weixin.qq.com/cgi-bin/user/get?access_token={}&next_openid='.format(str(access_token))
        r = requests.get(url)
        return json.loads(r.text)

    # 发送消息
    def send_msg(self, openid, template_id, altmsg):
        msg = {
            'touser': openid,
            'template_id': template_id,
            # 'url': iciba_everyday['fenxiang_img'],
            'data': {
                'device': {
                    'value': altmsg['device'],
                    # 'color': '#ffffCD'  # 好像不好使？？
                },
                'config': {
                    'value': altmsg['config'],
                }
            }
        }

        json_data = json.dumps(msg)
        if self.access_token == '':
            self.get_access_token(self.appid, self.appsecret)
        access_token = self.access_token
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(str(access_token))
        r = requests.post(url, json_data)
        return json.loads(r.text)

    # 为设置的用户列表发送消息
    def send_alert_msg(self, openids):
        for openid in openids:
            result = self.send_msg(openid, self.template_id, self.msg)
            if result['errcode'] == 0:
                print(' [INFO] send to {} is success'.format(openid))
            else:
                print(' [ERROR] send to {} is error'.format(openid))

    # 执行
    def run(self, user_list):
        if user_list == []:
            # 如果openids为空，则遍历用户列表
            result = self.get_user_list()
            user_list = result['data']['openid']

        # 根据openids对用户进行群发
        self.send_alert_msg(user_list)


if __name__ == '__main__':
    # 用户列表
    # sendto_user_list = ['o12yQty7Ra0NkbGwIfXK203hhyVc']

    msg = {'device': 'A01xxxxx',
           'config': '++++++-------'}
    # 执行
    abc = Almsg(msg)

    # run()方法可以传入user_list列表，也可传空参数
    # 传空参数则对微信公众号的所有用户进行群发
    abc.run(user_list=[])

