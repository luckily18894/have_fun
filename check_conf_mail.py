# -*- coding=utf-8 -*-

import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import paramiko
import hashlib
import datetime
from difflib import *
import os
import time
import re


# 下面的代码调整了更长的等待时间"time.sleep(5)",用于后面的配置提取操作,并不用于确认可达性
def ssh_multicmd(ip, username, password, cmd_list, verbose=True):
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

    abc = re.sub('---- More ----', '', x)
    resul += abc

    # 一直空格 直到回显完
    while 1:
        # 如果 本次回显为 <sysname> 就退出循环 否则 继续发送空格 读取命令剩余的回显
            if re.match('^<.+>', x.strip()):  # strip 很重要！！！
                break
            else:
                chan.send(space.encode())
                chan.send(b'\n')
                time.sleep(2)
                x = chan.recv(40960).decode()
                abc = re.sub('---- More ----', '', x)
                resul += re.sub('\x1b\[42D[\s]+\x1b\[42D', '\r', abc)
                # \x1b[42D                                          \x1b[42D
                # 空格后回显会有上面这类字符，需要干掉

    chan.close()  # 退出交互式shell
    ssh.close()  # 退出ssh会话

    return resul


def get_config_md5(ip, username, password, cmd):
    run_config_raw = ssh_multicmd(ip, username, password, cmd)
    b = re.findall('.*(sysname.+return).*', run_config_raw, re.S | re.M)
    # re.S是代表 . 可以匹配\n以及 ''   re.M是多行\

    run_config = re.sub('\r\n', '\r\n', b[0])
    # 匹配后输出的结果是列表，里面是匹配中的字符串（单行），其中包含可见的\n，所以就替换回去

    m = hashlib.md5()
    m.update(run_config.encode())
    md5_value = m.hexdigest()

    return run_config, md5_value


def send_mail(mailserver, username, password, From, To, Cc, Subj, Main_Body, files=None):
    # 使用SSL加密SMTP发送邮件, 此函数发送的邮件有主题,有正文,还可以发送附件
    Tos = To.split(';')  # 把多个邮件接受者通过';'分开
    Date = email.utils.formatdate()  # 格式化邮件时间
    msg = MIMEMultipart()  # 产生MIME多部分的邮件信息
    msg["Subject"] = Subj  # 主题
    msg["From"] = From  # 发件人
    msg["To"] = To  # 收件人
    msg["Cc"] = Cc  # 抄送人
    msg["Date"] = Date  # 发件日期

    part = MIMEText(Main_Body)
    msg.attach(part)  # 添加正文

    # if files:  # 如果存在附件文件
    # for file in files:  # 逐个读取文件,并添加到附件
    #     real_filename = re.findall('.*\\\\(.*\.xls.*)', file)[0]  # 取得真实的文件名，不然就是文件路径，很难看
    #     # print(real_filename)
    #     part = MIMEApplication(open(file, 'rb').read())
    #     part.add_header('Content-Disposition', 'attachment', filename=real_filename)
    #     msg.attach(part)

    # print('发送中...', '\n')
    server = smtplib.SMTP_SSL(mailserver, 465)  # 连接邮件服务器
    server.login(username, password)  # 通过用户名和密码登录邮件服务器

    # 判断是否需要抄送，添加空的抄送会报错
    if Cc != '':
        Ccs = Cc.split(';')  # 把多个邮件抄送者通过';'分开
        failed = server.sendmail(From, Tos + Ccs, msg.as_string())  # 发送邮件
    else:
        failed = server.sendmail(From, Tos, msg.as_string())  # 发送邮件

    server.quit()  # 退出会话
    if failed:
        print('Falied recipients:', failed)  # 如果出现故障，打印故障原因！
        return
    else:
        # print('邮件已经成功发出！！！', '\n')  # 如果没有故障发生
        return


def diff_txt(txt1, txt2):
    txt1_list, txt2_list = txt1.splitlines(), txt2.splitlines()
    return_result = '\n'.join(list(Differ().compare(txt1_list, txt2_list)))
    return return_result


def check_conf(device_list, username, password, cmd_list):
    for sdevice in device_list:
        try:
            new, md5_value = get_config_md5(sdevice, username, password, cmd_list)

            # 判断文件是否存在 T/F
            if os.path.isfile('check_{}_md5.txt'.format(sdevice)):

                # 若存在 就读取txt中保存的md5值 与当前值进行比较
                with open('check_{}_md5.txt'.format(sdevice), 'r') as f:
                    # 与之前相同 就略过
                    if md5_value == f.read():
                        print('设备 {:^15} 配置未改变'.format(sdevice))

                    # 与之前不同 发送邮件告知不同 并覆写配置及md5值
                    else:
                        with open('{}_config.txt'.format(sdevice), 'r') as old_conf:
                            old = old_conf.read()
                        with open('{}_config.txt'.format(sdevice), 'w') as new_conf:
                            new_conf.write(new)
                        differences = diff_txt(old, new)
                        # print(differences)

                        with open('check_{}_md5.txt'.format(sdevice), 'w') as md:
                            md.write(md5_value)

                        send_mail('smtp.139.com',  # 邮箱服务器
                                  '18368868186@139.com',  # 用户名
                                  '1231231231231',  # 密码
                                  '18368868186@139.com',  # 发件人邮箱
                                  '185686792@qq.com',  # 收件人邮箱
                                  '',  # 抄送
                                  '设备 {} 配置改变'.format(sdevice),  # 标题
                                  '系统于{0}检测到配置变化\r\n配置比较如下：\r\n\r\n{1}'.format(datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S'), differences),  # 正文
                                  )

                        print('设备 {:^15} 配置改变，已发送邮件通知'.format(sdevice))

                # 若不存在就新建一个txt 并写入当前配置的md5值
            else:
                with open('check_{}_md5.txt'.format(sdevice), 'w') as f:
                    f.write(md5_value)
                with open('{}_config.txt'.format(sdevice), 'w') as conf:
                    conf.write(new)
                print('无   {:^15} 记录，已创建新缓存文件'.format(sdevice))

        except paramiko.ssh_exception.NoValidConnectionsError:
            print('设备 {:^15} 无法连接'.format(sdevice))
            continue
        except Exception as ex:
            print('设备 {0:^15} {1}'.format(sdevice, ex))
            continue


if __name__ == '__main__':
    # 设备及每个设备信息可以做成字典{device： [username, password, cmd_list]}
    # 用户名/密码错误时 在一段时间后会有关闭session的报错，可忽略
    while 1:
        print('\r' + '开始检查             ')
        check_conf(['192.168.1.11', '192.168.122.122'], 'root', 'huawei', 'dis cu')

        # 每隔5分钟检查一次 也可以使用 schedule 模块作定时任务 Linux定时任务 等...
        time_sleep = 300
        # 倒计时
        while time_sleep > 0:
            print('\r' + '倒计时{}秒后再次检查  '.format(time_sleep), end='')
            time_sleep -= 1
            time.sleep(1)

