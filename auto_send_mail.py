# -*- coding=utf-8 -*-

import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import re


def send_mail(mailserver, username, password, From, To, Cc, Subj, Main_Body, files=None):
    # 使用SSL加密SMTP发送邮件, 此函数发送的邮件有主题,有正文,还可以发送附件
    Tos = To.split(';')  # 把多个邮件接受者通过';'分开
    Ccs = Cc.split(';')  # 把多个邮件抄送者通过';'分开
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
    for file in files:  # 逐个读取文件,并添加到附件
        real_filename = re.findall('.*\\\\(.*\.xls.*)', file)[0]  # 取得真实的文件名，不然就是文件路径，很难看
        # print(real_filename)
        part = MIMEApplication(open(file, 'rb').read())
        part.add_header('Content-Disposition', 'attachment', filename=real_filename)
        msg.attach(part)

    print('发送中...')
    server = smtplib.SMTP_SSL(mailserver, 465)  # 连接邮件服务器
    server.login(username, password)  # 通过用户名和密码登录邮件服务器
    failed = server.sendmail(From, Tos + Ccs, msg.as_string())  # 发送邮件
    server.quit()  # 退出会话
    if failed:
        print('Falied recipients:', failed)  # 如果出现故障，打印故障原因！
        return
    else:
        print('邮件已经成功发出！！！', '\n')  # 如果没有故障发生
        return


if __name__ == '__main__':
    # 使用Linux解释器 & WIN解释器
    import datetime

    today = datetime.date.today()
    the_year, the_month, the_day, yesterday = str(today.year), str(today.month), str(today.day), str(int(today.day) - 1)
    date_today = the_year + '.' + the_month + '.' + the_day
    date_yesterday = the_year + '.' + the_month + '.' + yesterday

    while True:
        print('''流程：
    白班 or 晚班 ---> 发送机房资料  是   否 ---> 发送
                                 ↓
                                 --->机房资料日期 ---> 发送
对应文件必须存在！！！                                
回车立即生效，无确认项！！！''', '\n')

        print('班次： 白   晚')
        banci = input()
        if banci == '白':
            which_duty = banci
            the_date = date_today
            print('\n')
        elif banci == '晚':
            which_duty = banci
            the_date = date_yesterday
            print('\n')
        elif banci == 'exit':
            break
        else:
            print('什么东西？？重来', '\n')
            continue

        daily_record = 'C:\\Users\\Administrator\\Desktop\\资料汇总\\18.值班日志\\' + the_year + '\\' + the_month + '月份\\' + the_date + '\\' + the_date + '红山网运' + which_duty + '班值班日志.xls'
        data1 = 'C:\\Users\\Administrator\\Desktop\\资料汇总\\06.机房资料\\机房资料\\' + the_year + '年\\红山机房资料-' + the_date + '.xlsx'
        data2 = 'C:\\Users\\Administrator\\Desktop\\资料汇总\\06.机房资料\\机房资料\\' + the_year + '年\\红山机房资料-' + date_yesterday + '.xlsx'

        print('是否发送机房资料： 是   否')
        ziliao = input()
        print('\n')
        if ziliao == '是':

            print('''机房资料的时间：
        昨天 --- 与晚班日志时间一致，或其他需求
        今天 --- 与白班日志时间一致，或其他需求''', '\n')
            data_time = input()
            if data_time == '昨天':
                title = the_date + '红山网运' + which_duty + '班值班日志 & 红山机房资料-' + the_date
                attachments = [daily_record, data2]
                print('\n')
            elif data_time == '今天':
                title = the_date + '红山网运' + which_duty + '班值班日志 & 红山机房资料-' + date_today
                attachments = [daily_record, data1]
                print('\n')
            else:
                print('什么东西？？重来', '\n')
                continue

        elif ziliao == '否':
            title = the_date + '红山网运' + which_duty + '班值班日志'
            attachments = [daily_record]
            print('\n')
        elif ziliao == 'exit':
            break
        else:
            print('什么东西？？重来', '\n')
            continue

        send_mail('smtp.qq.com',
                  '2426848309@qq.com',
                  'rhrogewmkjtwdifg',
                  '2426848309@qq.com',
                  '1245912307@qq.com;1075708160@qq.com',  # 收信人
                  '24801810@qq.com',  # 抄送
                  title,
                  '',
                  attachments)
