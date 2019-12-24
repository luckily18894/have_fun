# -*- coding=utf-8 -*-

import paramiko
import datetime
import time
import re


# 支持读取多页回显（仅华为可用，思科暂不明确），已解决空行问题，就和CRT显示的一样~
def ssh_cmd(ip, username, password, cmd_list, verbose=True):
    ssh = paramiko.SSHClient()  # 创建SSH Client
    ssh.load_system_host_keys()  # 加载系统SSH密钥
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 添加新的SSH密钥
    ssh.connect(ip, port=22, username=username, password=password, timeout=5, compress=True)  # SSH连接

    chan = ssh.invoke_shell()  # 激活交互式shell
    time.sleep(2)
    # x = chan.recv(2048).decode()  # 接收回显信息
    resul = ''
    space = ' '  # 要发送的空格

    for cmd in cmd_list:  # 逐个读取命令
        print(ip, cmd)
        chan.send(cmd.encode())  # 执行命令，注意字串都需要编码为二进制字串
        chan.send(b'\n')  # 一定要注意输入回车
        time.sleep(2)  # 由于有些回显可能过长，所以可以考虑等待更长一些时间
        x = chan.recv(40960).decode()  # 读取回显，有些回显可能过长，请把接收缓存调大

        # o = re.sub('\s+----\sMore\s----', '', x)
        o = re.sub('\r\n', '\n', re.sub('\s+----\sMore\s----', '', x), re.S | re.M)
        resul += re.sub('\r\n', '\n', o, re.S | re.M)

        # 一直空格 直到回显完
        while 1:
            # 如果 本次回显为 <sysname> 就退出循环 否则 继续发送空格 读取命令剩余的回显
            if re.match('.*<.+>', x.strip()):  # strip 很重要！！！
                # print('1')

                break
            else:
                # print('2')
                chan.send(space.encode())
                chan.send(b'\n')
                time.sleep(2)  # 防止有的设备反应慢，还是多等一会儿吧
                x = chan.recv(40960).decode()
                # abc = re.sub('\s+----\sMore\s----', '', x)
                o = re.sub('\x1b\[\d{2}D[\s]+\x1b\[\d{2}D', '\r\n', re.sub('\s+----\sMore\s----', '', x))
                # \x1b[42D                                          \x1b[42D
                resul += re.sub('\r\n', '\n', o, re.S | re.M)
                # 空格后回显会有上面这类字符，需要干掉

    sysname = re.match('.*<(.+)>', x.strip()).groups()[0]

    chan.close()  # 退出交互式shell
    ssh.close()  # 退出ssh会话
    # print([resul])
    return resul, sysname


def resule_to_txt(ipadd, cmd):
    res, sysname = ssh_cmd(ipadd, 'wujiajie', '1ffw#1*dF', cmd)  # ssh登录的 用户名 密码在此
    ti = datetime.datetime.now().strftime('%Y.%m.%d %H.%M.%S')
    with open('{} -- {}.txt'.format(sysname, ipadd), 'w') as f:
        f.write(res)
    print('{} -- {} -- {}'.format(sysname, ipadd, ti) + '  已完成！')


if __name__ == '__main__':
    # print(ssh_cmd('192.168.0.97', 'wujiajie', '1ffw#1*dF', 'dis cu'))
    lis = ['111.1.48.28',
           '111.1.48.126',
           ]

    cm = ['dis acl all',
          'dis policy all',
          ]

    # try:
    for i in lis:
        resule_to_txt(i, cm)  # 设备地址 命令

    # except Exception as ex:
    #     print(ex)

