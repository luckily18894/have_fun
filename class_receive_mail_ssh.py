# -*- coding=utf-8 -*-

import poplib
import socket
import email
import base64
import paramiko
import time
import re
import ipaddress
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Autossh:
    def __init__(self):
        # 初始化各参数，尽量集中在这里，方便修改
        self.mail_number = 0
        self.try_number = 0
        self.mail_start_number = 130
        self.addr = ''

        self.file_dict = {
                          'mail_log': '/root/ssh_mail_log.txt',
                          'saved_addr': '/root/saved_addr.txt',
                          'zmcc_add': '/root/zmcc_add.txt',
                          'black_white_list': '/root/black_white_list.txt'
                          }

        self.mail_info = {
                          'mailserver_smtp': 'smtp.js-datacraft.com',
                          'mailserver_pop3': 'pop3.js-datacraft.com',
                          'mailuser': 'jj.wu@datatech-info.com',
                          'mailpasswd': 'luCKi1y18894',
                          'mailfrom': '=?GB2312?B?zuK80r3cLbTvv8Y=?= <jj.wu@datatech-info.com>',
                          'mailcc': '=?GB2312?B?zuK80r3cLUND?= <185686792@qq.com>',
                          'ssh_mail_log': '/root/ssh_mail_log.txt'
                          }

        self.reset_cmd_list = [
                               'sys',
                               'policy interzone local untrust inbound',
                               'policy 9',
                               'undo policy source all',
                               'policy interzone local untrust outbound',
                               'policy 5',
                               'undo policy destination all',
                               '\n'
                               ]

        self.ssh_dict = {
                         'ip': '112.17.12.29',
                         'username': 'wujiajie',
                         'password': 'wujiajie@zmcc123'
                         }

        self.respond_dict = {
                             'good': ['[自动回复] 石桥VPN添加地址成功!', '成功添加!'],
                             'exists': ['[自动回复] 石桥VPN添加地址异常!', '已存在，无需添加!'],
                             'deny': ['[自动回复] 石桥VPN拒绝添加地址!', '就是浙江移动地址，不用添加！\n 就不能先试一下吗'],
                             'reset_successfully': ['自动重置策略成功!', '检测到策略已满，自动重置成功!']
                             }

    def update_add_cmd_list(self):
        self.add_cmd_list = [
                             'sys',
                             'policy interzone local untrust inbound',
                             'policy 9',
                             'action permit',
                             'policy source ' + self.addr + ' mask 24',
                             'policy interzone local untrust outbound',
                             'policy 5',
                             'action permit',
                             'policy destination ' + self.addr + ' mask 24',
                             '\n'
                             ]

    @staticmethod
    def decode_subject_base64(stre):
        # 解码如下内容
        # =?utf-8?b?6ZmE5Lu25rWL6K+VX+S4u+mimA==?=
        #   utf-8   6ZmE5Lu25rWL6K+VX+S4u+mimA==   (转码后为:附件测试_主题)
        # ['=?UTF-8?B?5pys5py6SVA6MTExLjIzLjE=?=\n =?UTF-8?B?NS4xMjPmuZbljZfnnIHplb/mspnluIIg56e75Yqo?=']  (怎么会有\n分段的)
        try:
            decoded_stre = ''
            for sss in stre.split('\n'):  # 解决有\n分段的问题
                re_result = re.match('=\?(.*)\?\w\?(.*)\?=', sss.strip()).groups()
                # re_result[0] 为编码方式
                middle = re_result[1]  # 提取base64的内容 6ZmE5Lu25rWL6K+VX+S4u+mimA==
                decoded = base64.b64decode(middle)  # 对内容进行base64解码
                decoded_stre += decoded.decode(re_result[0])  # 再对base64解码后内容,进行utf-8解码,转换为中文内容
        except Exception:
            decoded_stre = stre
        return decoded_stre

    # 检查需求地址是否 是浙江移动地址
    def check_ip_zmcc(self):
        with open(self.file_dict['zmcc_add'], 'r') as fff:
            for ev_added in fff.readlines():
                if re.search('mask', ev_added):
                    if ipaddress.ip_address(self.addr) in ipaddress.ip_network(ev_added.strip('\n').replace(' mask ', '/').strip()):
                        self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + self.addr + '  是浙江移动地址，无需添加')
                        fff.close()
                        return 'include zmcc'

                else:
                    if ipaddress.ip_address(self.addr) in ipaddress.ip_network(ev_added.strip('\n').replace(' 0', '/32').strip()):
                        self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + self.addr + '  是浙江移动地址，无需添加')
                        fff.close()
                        return 'include zmcc'
        return 'need to be added'

    def send_mail(self, mailto, subj, main_body, send_try=0):
        msg = MIMEMultipart()  # 产生MIME多部分的邮件信息
        msg["Subject"] = subj  # 标题
        msg["From"] = self.mail_info['mailfrom']  # 发件人
        msg["To"] = mailto  # 收件人
        msg["Cc"] = self.mail_info['mailcc']  # 抄送人 肯定要抄送我，所以固定
        msg["Date"] = email.utils.formatdate()  # 发件时间，格式化邮件时间
        part = MIMEText(main_body)
        msg.attach(part)  # 添加正文

        # 只为表明能执行到这一行,定位log
        self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  发送中...", time.localtime()))

        try:
            server_send = smtplib.SMTP_SSL(self.mail_info['mailserver_smtp'], 465)  # 连接邮件服务器
            server_send.login(self.mail_info['mailuser'], self.mail_info['mailpasswd'])  # 通过用户名和密码登录邮件服务器

            # To.split(';') 把多个邮件接受者通过';'分开, Cc.split(';') 把多个邮件抄送者通过';'分开
            failed = server_send.sendmail(self.mail_info['mailfrom'], mailto.split(';') + self.mail_info['mailcc'].split(';'), msg.as_string())  # 发送邮件
            server_send.quit()  # 退出会话

            if failed:
                # 如果出现故障，写入故障原因！
                self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  Falied recipients: ", time.localtime()) + failed)
                return
            else:
                # 如果没有故障发生
                self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  回信已经成功发出! TO: ", time.localtime()) + msg["To"])
                return

        except Exception as _ex:
            # 发信时会话会被服务器干掉，原因不明，重试3次，还不行就跳过，继续下一封
            if re.search('Connection unexpectedly closed', str(_ex)):
                self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + '  模块内部二次发送失败，waiting 15s' + '  send_try=' + str(send_try))
                send_try += 1
                # 重试3次
                if send_try >= 3:
                    self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + '  模块内部二次发送失败 超过3次！')
                    return
                else:
                    time.sleep(15)
                    self.send_mail(mailto, subj, main_body, send_try=send_try)  # 递归调用 用 send_try 来解决死循环
                    return
            else:
                self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + str(_ex) + '  发信时有其他错误！')
                raise _ex

    def server_connect(self):
        server = poplib.POP3_SSL(self.mail_info['mailserver_pop3'], 995)  # 连接到邮件服务器
        server.user(self.mail_info['mailuser'])  # 邮件服务器用户名
        server.pass_(self.mail_info['mailpasswd'])  # 邮件服务器密码
        # POP3对行长度做了限制，默认为_MAXLINE = 2048，故若是邮件超过此长度就会提示“poplib.error_proto: line too long”。解决方案：在读取邮件代码中重新定义最大行长度，即给poplib._MAXLINE设置新值。
        poplib._MAXLINE = 20480
        return server

    # 对每封邮件进行分值，做成dict
    def split_mail(self, server):
        hdr, message, octets = server.retr(self.mail_start_number + self.mail_number)  # 读取邮件（从最早的第一封开始的第几封）
        str_message = email.message_from_bytes(b'\n'.join(message))  # 把邮件内容拼接到大字符串
        part_list = [part for part in str_message.walk()]  # 把邮件的多个部分添加到part_list

        self.mail_dict = {}  # 报错为init未定义，但并不影响执行
        # 把邮件的第一个[0]部分内容提取出来写入字典mail_dict
        # 注意第一部分,所有邮件都会存在,是邮件的头部信息
        for header_name, header_content in part_list[0].items():
            if header_name == 'Subject':
                self.mail_dict[header_name] = self.decode_subject_base64(header_content)  # base64解码Subject
            elif header_name == 'From':
                self.mail_dict[header_name] = header_content  # base64解码Subject
                # 如果发件人没改显示名称或名称不为中文，则mail_dict['fro'] = "lee--jie@139.com" <lee--jie@139.com>(样例)
                # 将发件人名称手动抓取出来，mail_dict['fro']在回信中调用了，新建mail_dict['fr']，用于代码log 和 回信内的显示
                if re.match('".*" <.*>', header_content):
                    self.mail_dict['fro'] = re.match('"(.*)" <.*>', header_content).groups()[0]  # 把带有双引号 ".*" 的去掉引号
                elif re.match('.*<.*>', header_content):
                    self.mail_dict['fro'] = re.match('(.*)<.*>', header_content).groups()[0]  # 提取 <> 前面的:样例15103220375<15103220375@139.com>
                else:
                    self.mail_dict['fro'] = header_content
                self.mail_dict['fr'] = self.decode_subject_base64(self.mail_dict['fro'])  # 添加解码后的发件人名，方便后面读取
                self.mail_dict['mail_address'] = re.match('.*<(.*)>', header_content).groups()[0]  # 添加发件人邮箱地址，方便限制发件人
            else:
                self.mail_dict[header_name] = header_content

    # ssh登陆敲命令
    def multicmd_ssh(self, cmd_list, reset=False, verbose=True):
        ssh = paramiko.SSHClient()  # 创建SSH Client
        ssh.load_system_host_keys()  # 加载系统SSH密钥
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 添加新的SSH密钥
        # 修改 allow_agent=False, look_for_keys=False ，默认为true 可能会在某些服务器上导致 AuthenticationException: Authentication failed.
        ssh.connect(self.ssh_dict['ip'], port=22, username=self.ssh_dict['username'], password=self.ssh_dict['password'], timeout=10, compress=True, allow_agent=False, look_for_keys=False)  # SSH连接

        chan = ssh.invoke_shell()  # 激活交互式shell
        x = chan.recv(40960).decode()  # 先读一次回显，不然回显会累计
        time.sleep(2)

        for cmd in cmd_list:  # 读取命令
            chan.send(cmd.encode())  # 执行命令，注意字串都需要编码为二进制字串
            chan.send(b'\n')  # 一定要注意输入回车
            x = chan.recv(40960).decode()  # 读取回显，有些回显可能过长，请把接收缓存调大
            self.tx.write(x)  # 将回显写入
            time.sleep(1)  # 由于有些回显可能过长，所以可以考虑等待更长一些时间

            # 如果检测到已存在，就停止 并回信已存在
            if re.search('Error: Address item conflicts', x):
                chan.close()  # 退出交互式shell
                ssh.close()  # 退出ssh会话
                return 'exists'

            # 如果检测到策略已满，就停止 并自动重置策略
            if re.search('Error: The address items are full', x):
                chan.close()  # 退出交互式shell
                ssh.close()  # 退出ssh会话
                self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]   检测到策略已满，开始重置!", time.localtime()))
                # 执行重置，递归调用
                self.multicmd_ssh(self.reset_cmd_list, reset=True)
                # self.handle_full()  # 执行重置
                reset = True  # 不清楚上面调用完后 reset的状态，手动设定一下
                # return 'full'

        chan.close()  # 退出交互式shell
        ssh.close()  # 退出ssh会话

        if reset:  # 判断是否在重置策略
            return 'reset_successfully'
        else:
            return 'good'

    # 开始操作添加ip
    def start_kaifang(self):
        self.update_add_cmd_list()
        # ssh登陆设备 敲命令
        ret = self.multicmd_ssh(self.add_cmd_list)

        # 发送邮件告知添加成功
        if ret == 'reset_successfully':  # 自动重置策略
            try:
                self.send_mail(
                               '=?GB2312?B?zuK80r3c?= <18368868186@139.com>',  # 收信人
                               self.respond_dict[ret][0],
                               time.strftime("[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + self.respond_dict[ret][1],
                               )

            # Connection unexpectedly closed 连不上邮箱smtp??  10秒后再重试一次(但不论最终成功否，都会继续读下一封)
            except Exception as _ex:
                if re.match('Connection unexpectedly closed', str(_ex)) or re.match('Name or service not known', str(_ex)):
                    time.sleep(15)
                    self.send_mail(
                                   '=?GB2312?B?zuK80r3c?= <18368868186@139.com>',  # 收信人
                                   self.respond_dict[ret][0],
                                   time.strftime("[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + self.respond_dict[ret][1],
                                   )
                else:
                    self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  回复邮件发送失败，reason= ", time.localtime()) + str(_ex))
            return 'reset'

        else:  # 其他正常情况
            self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + self.addr + '   compelete!!')
            # 如果是已存在的情况，就不在 saved_addr.txt 中写入
            if ret != 'exists':
                self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + self.addr + '   已存在!')
                with open(self.file_dict['saved_addr'], 'a') as f:
                    # 对齐下格式
                    f.write('\n{}  {:<15}  From: {}'.format(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), self.addr, self.mail_dict['fr']))
            try:
                self.send_mail(
                               self.mail_dict['From'],  # 收信人
                               self.respond_dict[ret][0],
                               '您好 ' + self.mail_dict['fr'] + time.strftime(":\n     [%Y-%m-%d %H:%M:%S]  您的地址", time.localtime()) + self.addr + self.respond_dict[ret][1],
                               )

            # Connection unexpectedly closed 连不上邮箱smtp??  10秒后再重试一次(但不论最终成功否，都会继续读下一封)
            except Exception as _ex:
                if re.match('Connection unexpectedly closed', str(_ex)) or re.match('Name or service not known', str(_ex)):
                    time.sleep(10)
                    self.send_mail(
                                   self.mail_dict['From'],  # 收信人
                                   self.respond_dict[ret][0],
                                   '您好 ' + self.mail_dict['fr'] + time.strftime(":\n     [%Y-%m-%d %H:%M:%S]  您的地址", time.localtime()) + self.addr + self.respond_dict[ret][1],
                                   )
                else:
                    self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  回复邮件发送失败，reason= ", time.localtime()) + str(_ex))

            # 删除邮件(预留)False  应该可以使用(并不行..)
            # if delete_email:
            #     server.dele(49 + mail_number)
            #     return

            return 'normal'

    # 核心控制
    def controll_mail(self, delete_email=False):
        with open(self.file_dict['mail_log'], 'a') as self.tx:
            try:
                server = self.server_connect()
                # server = poplib.POP3_SSL(self.mail_info['mailserver_pop3'], 995)  # 连接到邮件服务器
                # server.user(self.mail_info['mailuser'])  # 邮件服务器用户名
                # server.pass_(self.mail_info['mailpasswd'])  # 邮件服务器密码
                # # POP3对行长度做了限制，默认为_MAXLINE = 2048，故若是邮件超过此长度就会提示“poplib.error_proto: line too long”。解决方案：在读取邮件代码中重新定义最大行长度，即给poplib._MAXLINE设置新值。
                # poplib._MAXLINE = 20480

                # 打印服务器欢迎信息
                self.tx.write(time.strftime("\n\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + str(server.getwelcome()))
                while 1:
                    try:
                        # 对原始邮件做分值，提取感兴趣内容，做成mail_dict
                        self.split_mail(server)
                        # 写入 谁发的邮件，标题
                        self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  From: ", time.localtime()) + self.mail_dict['fr'] + '  标题: ' + self.mail_dict['Subject'])

                        # 黑名单/白名单 限制加至此，读取txt内的黑/白名单数据，与信中的发件人邮箱<.*>匹配，命中则做相应操作。
                        # 黑/白名单：所有人的139、达科邮箱。
                        # 发邮件：请求添加执行白名单 ，回信：已添加，可以进行增加拨vpn地址操作。
                        # 写入 谁发的邮件，拒绝/允许
                        with open(self.file_dict['black_white_list'], 'r') as ff:
                            permit_list = [person.strip('\n') for person in ff.readlines()]

                        # # =================新增操作===================后续都在此按这个模板增加吧
                        # self.mac_addr = choose_action(mail_dict, tx)
                        # if mac_addr:
                        #     try:
                        #         #  先判断是否在白名单中
                        #         if mail_dict['mail_address'] in permit_list:
                        #             # 若在白名单里的人，可执行操作
                        #             self.mail_number = ...  # 添加 SW62 acl4000 mac 的操作，考虑单独起函数操作
                        #         else:
                        #             # 不在白名单里的人，不给加
                        #             self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + mail_dict['mail_address'] + '  不在白名单中!')
                        #             self.mail_number += 1
                        #             return self.mail_number
                        #     except Exception:
                        #         ...
                        # # =================新增操作===================后续都在此按这个模板增加吧

                        # ==============添加VPN地址 块================如有需要，直接单独做函数
                        # 获取邮件标题中的 ip:xxx.xxx.xxx.xxx 读出需求的地址
                        self.addr = str(ipaddress.ip_address(re.search('((\d{1,3}\.){3}\d{1,3})', self.mail_dict['Subject']).groups()[0]))

                        if self.mail_dict['mail_address'] in permit_list:
                            # 若就是浙江移动地址，怼！
                            if self.check_ip_zmcc() == 'include zmcc':
                                self.mail_number += 1
                                self.send_mail(
                                               self.mail_dict['From'],  # 收信人
                                               self.respond_dict['deny'][0],
                                               '您好 ' + self.mail_dict['fr'] + time.strftime(":\n     [%Y-%m-%d %H:%M:%S]  您的地址", time.localtime()) + self.addr + self.respond_dict['deny'][1],
                                               )
                            else:  # check_ip_zmcc() == 'need to be added'
                                # 若在白名单里的人，可执行操作，已添加命令act per
                                try:
                                    # 开始ssh执行命令，并且发回信
                                    # 根据是否有重置策略，决定读不读下一封
                                    if self.start_kaifang() == 'reset':
                                        # 已重置策略，继续执行本封邮件
                                        continue
                                    else:
                                        # 下一封
                                        self.mail_number += 1
                                        self.try_number = 0  # 重置超时尝试次数

                                    # server.dele(103 + mail_number)  # 操作完成，删除本封邮件(省的我手动删除)

                                # ssh连接超时第一次
                                except socket.timeout:
                                    self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + self.addr + '  失败 ssh连接超时1次')
                                    time.sleep(15)
                                    try:
                                        # 开始ssh执行命令，并且发回信
                                        # 根据是否有重置策略，决定读不读下一封
                                        if self.start_kaifang() == 'reset':
                                            # 已重置策略，继续执行本封邮件
                                            continue
                                        else:
                                            # 下一封
                                            self.mail_number += 1
                                            self.try_number = 0  # 重置超时尝试次数

                                        # server.dele(103 + mail_number)  # 操作完成，删除本封邮件(省的我手动删除)

                                    # ssh连接超时（第二次）退出
                                    except socket.timeout:
                                        self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + self.addr + '  失败 ssh连接超时2次')
                                        # 发邮件告知我 ssh连不上2次了，下一封
                                        self.mail_number += 1
                                        self.send_mail(
                                                       '=?GB2312?B?zuK80r3c?= <18368868186@139.com>',  # 收信人
                                                       '代码捕获其他错误!',
                                                       time.strftime("\n     [%Y-%m-%d %H:%M:%S]  ", time.localtime()) + '  ssh连接超时2次'
                                                       )

                                # 用户名密码错误
                                except paramiko.ssh_exception.AuthenticationException:
                                    self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + self.addr + '  失败 ssh用户名密码错误')
                                    # 发邮件告知我 用户名密码错误，下一封
                                    self.mail_number += 1
                                    self.send_mail(
                                                   '=?GB2312?B?zuK80r3c?= <18368868186@139.com>',  # 收信人
                                                   '代码捕获其他错误!',
                                                   time.strftime("\n     [%Y-%m-%d %H:%M:%S]  ", time.localtime()) + '  ssh用户名密码错误'
                                                   )

                                return self.mail_number

                        else:
                            # 不在白名单里的人，不给加
                            self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + self.mail_dict['mail_address'] + '  不在白名单中!')
                            self.mail_number += 1
                            return self.mail_number

                    # IP地址格式有误 298.1.1.1 (样例)
                    except ValueError as _ex:
                        if re.findall('does not appear to be an IPv4 or IPv6 address', str(_ex)):
                            self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  地址有误!", time.localtime()))
                            self.mail_number += 1
                    # 标题不能匹配，下一个
                    except AttributeError:
                        time.sleep(2)
                        self.mail_number += 1
                    # ==============添加VPN地址 块================如有需要，直接单独做函数

                    # 这一轮已经读完，退出等下一轮
                    except poplib.error_proto:
                        server.quit()  # 退出服务器
                        break

                return self.mail_number

            # 连接邮件服务器超时 重试3次
            except socket.gaierror:
                if self.try_number < 3:
                    self.tx.close()  # 先关了，不然又重复打开
                    time.sleep(5)
                    self.try_number += 1
                    self.mail_number = self.controll_mail(delete_email=False)
                    return self.mail_number
                else:
                    self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  本轮连接服务器已超时3次", time.localtime()))
                    return self.mail_number

            # ----------------------------------------需测试就把下面的注释掉----------------------------------------------------
            # 其他错误，防崩(此处重要，尽量别崩在这！)  但不会读下一封(更新标题为空，下一封。为什么有SB这么发！)
            except Exception as _ex:
                if re.match('\'Subject\'', str(_ex)):
                    self.mail_number += 1
                    self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  标题为空!", time.localtime()))
                    return self.mail_number

                # 这个问题的原因暂不明 连接邮箱服务器时偶尔会有此报错
                elif re.search('Connection reset by peer', str(_ex)):
                    self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + str(_ex) + ' mail_number=' + str(self.mail_number))
                    return self.mail_number

                # 发送的时候会有超时后30s模块内部重试？？第二次发送时，可能会产生此报错；本次回复邮件发不出就算了，继续下一封
                elif re.search('Connection unexpectedly closed', str(_ex)):
                    self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + str(_ex) + ' mail_number=' + str(self.mail_number) + '  模块内部二次发送失败，waiting 15s')
                    self.mail_number += 1
                    return self.mail_number

                # 其他问题，发邮件通知我
                else:
                    self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + str(_ex) + ' mail_number=' + str(self.mail_number))
                    self.mail_number += 1
                    try:
                        self.send_mail(
                                       '=?GB2312?B?zuK80r3c?= <18368868186@139.com>',  # 收信人
                                       '代码捕获其他错误!',
                                       time.strftime("\n     [%Y-%m-%d %H:%M:%S]  ", time.localtime()) + str(_ex)
                                       )
                    except Exception as _ex:
                        if re.search('Connection unexpectedly closed', str(_ex)):
                            time.sleep(10)
                            self.send_mail(
                                           '=?GB2312?B?zuK80r3c?= <18368868186@139.com>',  # 收信人
                                           '代码捕获其他错误!',
                                           time.strftime("\n     [%Y-%m-%d %H:%M:%S]  ", time.localtime()) + str(_ex)
                                           )
                    return self.mail_number
            # ----------------------------------------需测试就把上面的注释掉----------------------------------------------------

            # 手动 退出文件编辑，防止日志丢失
            finally:
                self.tx.close()

    def keep_running(self):
        while 1:
            # 一次执行只用一个时间，传入init调用，不再每次
            self.controll_mail(delete_email=False)
            with open(self.mail_info['ssh_mail_log'], 'a') as self.tx:
                self.tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  next round and wait 150s   mail_number=", time.localtime()) + str(self.mail_number))
            time.sleep(90)  # 每1分半 重新查看一遍邮箱


if __name__ == '__main__':
    autossh = Autossh()
    autossh.keep_running()
    # autossh.mail_start_number = 196
    # autossh.split_mail(autossh.server_connect())
    # for k, v in autossh.mail_dict.items():
    #     print(k, v)
