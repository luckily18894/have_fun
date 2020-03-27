# -*- coding=utf-8 -*-

import poplib
import socket
import email
import base64
import paramiko
import time
import re
# import smtplib
# import email.utils
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.application import MIMEApplication


def decode_subject_base64(str):
    # 解码如下内容
    # =?utf-8?b?6ZmE5Lu25rWL6K+VX+S4u+mimA==?=
    #   utf-8   6ZmE5Lu25rWL6K+VX+S4u+mimA== (转码后为:附件测试_主题)
    try:
        re_result = re.match('=\?(.*)\?\w\?(.*)\?=', str).groups()
        # re_result[0] 为编码方式
        middle = re_result[1]  # 提取base64的内容 6ZmE5Lu25rWL6K+VX+S4u+mimA==
        decoded = base64.b64decode(middle)  # 对内容进行base64解码
        decoded_str = decoded.decode(re_result[0])  # 再对base64解码后内容,进行utf-8解码,转换为中文内容
    except Exception:
        decoded_str = str
    return decoded_str


# def send_mail(mailserver, username, password, From, To, Cc, Subj, Main_Body, files=None):
#     # 使用SSL加密SMTP发送邮件, 此函数发送的邮件有主题,有正文,还可以发送附件
#     Tos = To.split(';')  # 把多个邮件接受者通过';'分开
#     Ccs = Cc.split(';')  # 把多个邮件抄送者通过';'分开
#     Date = email.utils.formatdate()  # 格式化邮件时间
#     msg = MIMEMultipart()  # 产生MIME多部分的邮件信息
#     msg["Subject"] = Subj  # 主题
#     msg["From"] = From  # 发件人
#     msg["To"] = To  # 收件人
#     msg["Cc"] = Cc  # 抄送人
#     msg["Date"] = Date  # 发件日期
#
#     part = MIMEText(Main_Body)
#     msg.attach(part)  # 添加正文
#
#     # if files:  # 如果存在附件文件
#     for file in files:  # 逐个读取文件,并添加到附件
#         real_filename = re.findall('.*\\\\(.*\.xls.*)', file)[0]  # 取得真实的文件名，不然就是文件路径，很难看
#         # print(real_filename)
#         part = MIMEApplication(open(file, 'rb').read())
#         part.add_header('Content-Disposition', 'attachment', filename=real_filename)
#         msg.attach(part)
#
#     print('发送中...', '\n')
#     server = smtplib.SMTP_SSL(mailserver, 465)  # 连接邮件服务器
#     server.login(username, password)  # 通过用户名和密码登录邮件服务器
#     failed = server.sendmail(From, Tos + Ccs, msg.as_string())  # 发送邮件
#     server.quit()  # 退出会话
#     if failed:
#         print('Falied recipients:', failed)  # 如果出现故障，打印故障原因！
#         return
#     else:
#         print('邮件已经成功发出！！！', files[0][-22:], '\n')  # 如果没有故障发生
#         return


def multicmd_ssh(ip, username, password, cmd_list, fil, verbose=True):
    ssh = paramiko.SSHClient()  # 创建SSH Client
    ssh.load_system_host_keys()  # 加载系统SSH密钥
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 添加新的SSH密钥
    # 修改 allow_agent=False, look_for_keys=False ，默认为true 可能会在某些服务器上导致 AuthenticationException: Authentication failed.
    ssh.connect(ip, port=22, username=username, password=password, timeout=10, compress=True, allow_agent=False, look_for_keys=False)  # SSH连接

    chan = ssh.invoke_shell()  # 激活交互式shell
    x = chan.recv(40960).decode()  # 先读一次回显，不然回显会累计
    time.sleep(2)

    for cmd in cmd_list:  # 读取命令
        chan.send(cmd.encode())  # 执行命令，注意字串都需要编码为二进制字串
        chan.send(b'\n')  # 一定要注意输入回车
        x = chan.recv(40960).decode()  # 读取回显，有些回显可能过长，请把接收缓存调大
        fil.write(x)  # 将回显写入
        time.sleep(1)  # 由于有些回显可能过长，所以可以考虑等待更长一些时间

    chan.close()  # 退出交互式shell
    ssh.close()  # 退出ssh会话
    return

# def login_mail_server(mailserver, mailuser, mailpasswd):
#     server = poplib.POP3_SSL(mailserver, 995)  # 连接到邮件服务器
#     server.user(mailuser)  # 邮件服务器用户名
#     server.pass_(mailpasswd)
#     return server


def recive_mail(mailserver, mailuser, mailpasswd, mail_number, try_number, delete_email=False):
    with open('/root/ssh_mail_log.txt', 'a') as tx:
        try:
            server = poplib.POP3_SSL(mailserver, 995)  # 连接到邮件服务器
            server.user(mailuser)  # 邮件服务器用户名
            server.pass_(mailpasswd)  # 邮件服务器密码

            # 打印服务器欢迎信息
            tx.write('\n\n' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '  ' + str(server.getwelcome()))

            while 1:
                try:
                    hdr, message, octets = server.retr(49 + mail_number)  # 读取邮件（从最早的第一封开始的第几封）
                    str_message = email.message_from_bytes(b'\n'.join(message))  # 把邮件内容拼接到大字符串
                    part_list = []
                    mail_dict = {}
                    for part in str_message.walk():  # 把邮件的多个部分添加到part_list
                        part_list.append(part)
                    # 把邮件的第一个[0]部分内容提取出来写入字典mail_dict
                    # 注意第一部分,所有邮件都会存在,是邮件的头部信息
                    for header_name, header_content in part_list[0].items():
                        if header_name == 'Subject':
                            mail_dict[header_name] = decode_subject_base64(header_content)  # base64解码Subject
                        else:
                            mail_dict[header_name] = header_content

                    tx.write('\n' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '  ' + mail_dict['Subject'])

                    # 获取邮件标题中的 ip:xxx.xxx.xxx.xxx 读出需求的地址
                    addr = re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', mail_dict['Subject']).groups()[0]
                    # 补全命令（放开一个C）
                    li1 = ['sys',
                           'policy interzone local untrust inbound',
                           'policy 8',
                           'policy source ' + addr + ' mask 24',
                           'policy interzone local untrust outbound',
                           'policy 4',
                           'policy destination ' + addr + ' mask 24']
                    try:
                        # ssh登陆设备 敲命令
                        multicmd_ssh('112.17.', 'wwww', 'w123', li1, tx)

                        tx.write('\n' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '  ' + addr + '   compelete!!')
                        with open('/root/saved_addr.txt', 'a') as f:
                            f.write('\n' + addr)

                        # 下一封
                        mail_number += 1
                        try_number = 0  # 重置超时尝试次数

                        # 删除邮件(预留)False  应该可以使用
                        if delete_email:
                            server.dele(49 + mail_number)
                            return

                    # -----------------------------------------------------------------------
                    # ssh连接超时（第一次）懒的写了，就复制吧
                    except socket.timeout:
                        tx.write('\n' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '  ' + addr + '  失败 ssh连接超时1次')
                        time.sleep(10)
                        try:
                            # ssh登陆设备 敲命令
                            multicmd_ssh('112.17.', 'wwwwww', 'w123', li1, tx)

                            tx.write('\n' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '  ' + addr + '   compelete!!')
                            with open('/root/saved_addr.txt', 'a') as f:
                                f.write('\n' + addr)

                            # 下一封
                            mail_number += 1
                            try_number = 0  # 重置超时尝试次数

                            # 删除邮件(预留)False  应该可以使用
                            if delete_email:
                                server.dele(49 + mail_number)
                                return

                        # ssh连接超时（第二次）退出
                        except socket.timeout:
                            tx.write('\n' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '  ' + addr + '  失败 ssh连接超时2次')
                            return mail_number
                        # 用户名密码错误
                        except paramiko.ssh_exception.AuthenticationException:
                            tx.write('\n' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '  ' + addr + '  失败 ssh用户名密码错误')
                            return mail_number
                    # ----------------------------------------------------------------------

                    # 用户名密码错误
                    except paramiko.ssh_exception.AuthenticationException:
                        tx.write('\n' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '  ' + addr + '  失败 ssh用户名密码错误')
                        return mail_number

                # 标题不能匹配，下一个
                except AttributeError:
                    time.sleep(2)
                    mail_number += 1
                # 这一轮已经读完，退出等下一轮
                except poplib.error_proto:
                    server.quit()  # 退出服务器
                    break
                except KeyboardInterrupt:
                    server.quit()  # 退出服务器
                    break

            return mail_number

        # 连接邮件服务器超时 重试3次
        except socket.gaierror:
            if try_number < 3:
                tx.close()  # 先关了，不然又重复打开
                time.sleep(5)
                try_number += 1
                mail_number = recive_mail('pop3.js-datacraft.com', 'jj.wu@js-datacraft.com', 'luCKi1y18894', mail_number, try_number, delete_email=False)
                return mail_number
            else:
                tx.write('\n' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '  本轮连接服务器已超时3次')
                return mail_number

        # 其他错误，防崩  但不会读下一封
        except Exception as exce:
            tx.write('\n' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '  ' + str(exce) + ' mail_number=' + mail_number)
            return mail_number

        # 手动 退出文件编辑，防止日志丢失
        finally:
            tx.close()


if __name__ == '__main__':
    mail_number = 0
    try_number = 0
    while 1:
        mail_number = recive_mail('pop3.js-datacraft.com', 'jj.wu@js-datacraft.com', 'luCKi1y18894', mail_number, try_number, delete_email=False)
        with open('/root/ssh_mail_log.txt', 'a') as txx:
            txx.write('\n' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '  next round and wait 150s' + '   mail_number=' + str(mail_number))
        time.sleep(150)  # 每2分半 重新查看一遍邮箱

        # 登不上设备发送邮件通知（预留）
        # send_mail('smtp.js-datacraft.com',
        #           'jj.wu@js-datacraft.com',
        #           'luCKi1y18894',
        #           'jj.wu@js-datacraft.com',
        #           '1245912307@qq.com;1075708160@qq.com',  # 收信人
        #           '24801810@qq.com',  # 抄送
        #           title,
        #           '',
        #           [daily_record])

    # ---------------------测试区---------------------------------------
    # 'pop.qq.com', '185686792@qq.com', 'purmejwztybrbifd'

    # a = '本机IP: 120.193.10.242浙江省杭州市 移动'
    # addr = re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', a).groups()[0]
    # print(addr)

    # addr = ['223.104.160.79',
    #         ]
    #
    # for asd in addr:
    #     li1 = ['sys',
    #            'policy interzone local untrust in',
    #            'policy 8',
    #            'policy source ' + asd + ' mask 24',
    #            'policy interzone local untrust out',
    #            'policy 4',
    #            'policy destination ' + asd + ' mask 24',
    #            ]
    #
    #     # ssh登陆设备 敲命令
    #     multicmd_ssh('112.17.', 'wwww', 'w123', li1)
    #     print(asd + '   compelete!!')

