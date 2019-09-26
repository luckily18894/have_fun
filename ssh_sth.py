# -*- coding=utf-8 -*-

import paramiko
import time
import re


# 支持读取多页回显（仅华为可用，思科暂不明确），可能有几个空行bug，应该可忽略
def ssh_cmd(ip, username, password, cmd_list, verbose=True):
    ssh = paramiko.SSHClient()  # 创建SSH Client
    ssh.load_system_host_keys()  # 加载系统SSH密钥
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 添加新的SSH密钥
    ssh.connect(ip, port=22, username=username, password=password, timeout=5, compress=True)  # SSH连接

    chan = ssh.invoke_shell()  # 激活交互式shell
    time.sleep(2)
    x = chan.recv(2048).decode()  # 接收回显信息
    resul = ''
    space = ' '  # 要发送的空格

    # for cmd in cmd_list:  # 逐个读取命令
    chan.send(cmd_list.encode())  # 执行命令，注意字串都需要编码为二进制字串
    chan.send(b'\n')  # 一定要注意输入回车
    time.sleep(2)  # 由于有些回显可能过长，所以可以考虑等待更长一些时间
    x = chan.recv(40960).decode()  # 读取回显，有些回显可能过长，请把接收缓存调大

    abc = re.sub('\s+----\sMore\s----', '', x)
    resul += abc

    # 一直空格 直到回显完
    while 1:
        # 如果 本次回显为 <sysname> 就退出循环 否则 继续发送空格 读取命令剩余的回显
            if re.match('^<.+>', x.strip()):  # strip 很重要！！！
                break
            else:
                chan.send(space.encode())
                chan.send(b'\n')
                time.sleep(1)
                x = chan.recv(40960).decode()
                abc = re.sub('\s+----\sMore\s----', '', x)
                resul += re.sub('\x1b\[\d{2}D[\s]+\x1b\[\d{2}D', '', abc)
                # \x1b[42D                                          \x1b[42D
                # 空格后回显会有上面这类字符，需要干掉

    chan.close()  # 退出交互式shell
    ssh.close()  # 退出ssh会话

    return resul


def resule_to_txt(ipadd, cmd):
    res = ssh_cmd(ipadd, 'wujiajie', '1ffw#1*dF', cmd)
    with open('{} - {}.txt'.format(ipadd, cmd), 'w') as f:
        f.write(res)
    print('{} - {}'.format(ipadd, cmd) + '  已完成！')


if __name__ == '__main__':
    # print(ssh_cmd('192.168.0.97', 'wujiajie', '1ffw#1*dF', 'dis cu'))
    resule_to_txt('218.205.112.23', 'dis cu')


