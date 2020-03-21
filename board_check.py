# -*- coding=utf-8 -*-

import paramiko
import datetime
import time
import re


# 支持读取多页回显（仅华为可用，思科暂不能用），已解决空行问题，就和CRT显示的一样~
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

    # for cmd in cmd_list:  # 逐个读取命令
    chan.send(cmd_list.encode())  # 执行命令，注意字串都需要编码为二进制字串
    chan.send(b'\n')  # 一定要注意输入回车
    time.sleep(2)  # 由于有些回显可能过长，所以可以考虑等待更长一些时间
    x = chan.recv(40960).decode()  # 读取回显，有些回显可能过长，请把接收缓存调大

    # o = re.sub('\s+----\sMore\s----', '', x)
    o = re.sub('\r\n', '\n', re.sub('\s+----\sMore\s----', '', x), re.S | re.M)
    resul += re.sub('\r\n', '\n', o, re.S | re.M)

    # 一直空格 直到回显完
    while 1:
        # 如果 本次回显为 <sysname> 就退出循环 否则 继续发送空格 读取命令剩余的回显
            if re.match('^<.+>', x.strip()):  # strip 很重要！！！
                sysname = re.match('^<(.+)>', x.strip()).groups()[0]
                print(2)
                break
            else:
                chan.send(space.encode())
                chan.send(b'\n')
                time.sleep(2)
                x = chan.recv(40960).decode()
                # abc = re.sub('\s+----\sMore\s----', '', x)
                o = re.sub('\x1b\[\d{2}D[\s]+\x1b\[\d{2}D', '\r\n', re.sub('\s+----\sMore\s----', '', x))
                # \x1b[42D                                          \x1b[42D
                resul += re.sub('\r\n', '\n', o, re.S | re.M)
                print(ip, 1)
                # 空格后回显会有上面这类字符，需要干掉

    chan.close()  # 退出交互式shell
    ssh.close()  # 退出ssh会话
    # print([resul])
    return resul, sysname


if __name__ == '__main__':
    ippp = [
            '192.168.100.4',
            ]

    for iii in ippp:
        resul, sysname = ssh_cmd(iii, 'wujiajie', '1ffw#1*dF', 'display device')  # 取得回显
        # 以'-----------'为分界，去掉上半部分无用信息，下半部分就为板卡信息，结果为列表
        board_info = resul.split('-----------')

        # 去除列表内空值
        while '' in board_info:
            board_info.remove('')
        # 此时列表内有2个东西，第一个是上半部分，第二个是下半部分，所以取第二个 并以\n分界 结果为单板的列表
        new_board_info = board_info[1].split('\n')

        # 对每块单板分值
        for single_board in new_board_info:

            try:
                # 分值
                single_info = single_board.split(' ')
                while '' in single_info:
                    single_info.remove('')  # 去除列表内空值

                # 第4个值为当前状态， 如果不为Present则视为不正常，打开文件写入异常板卡信息
                if single_info[3] != 'Present':
                    with open('C:\\Users\\18568\\Desktop\\2.txt', 'a') as f:
                        f.write(sysname + '    ' + single_info[0] + ' 槽位   状态  ' + single_info[3] + '\n')

            # 这处理方式应该要改改
            except Exception:
                continue


# if re.match('^<.+>', x.strip()) or re.match('.*#', x.strip()):
# 此为93系列版本！！！！
# 堆叠 需分2块 / 40e '------' 的中间有空格 / 128 5000e 有2条 '--------' / 125 没有 '-------'
# 如何 准确区分 状态    不同型号设备 考虑用字典{'ip': 型号}
