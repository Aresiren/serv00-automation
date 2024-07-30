# # -*-coding:utf8-*-

import os
import paramiko
import requests
import json
from datetime import datetime, timezone, timedelta

'''

SSH_INFO:
[
  {"username": "serv00的账号", "password": "serv00的密码", "panel": "panel6.serv00.com"},
  {"username": "ct8的账号", "password": "ct8的密码", "panel": "panel.ct8.pl"},
  {"username": "user2", "password": "password2", "panel": "panel6.serv00.com"}
]

LOGIN_TYPE:
ssh or telegram or http

TELEGRAM_BOT_TOKEN:
示例：733255939:AAHsoQf-3lOoc1xC8le2d58qlfrCqEXzu74

TELEGRAM_CHAT_ID:
示例：5329499650

PUSH:
推送渠道值为mail或者telegram。示例：mail

MAIL:
接收通知的邮箱。示例：mail@mail.com
'''

# 从环境变量中获取
mail = os.getenv('MAIL')
push = os.getenv('PUSH')
LOGIN_TYPE = os.getenv('LOGIN_TYPE') # ssh or telegram or http
ssh_info_str = os.getenv('SSH_INFO', '[]')
host_infos = json.loads(ssh_info_str)

commands = ['whoami', 'cat /etc/issue', 'whoami']
message = 'serv00&ct8自动化脚本运行\n'

def main_fuc():
    login_auth(LOGIN_TYPE, push, host_infos, commands[0])
    print('ending...')
    
def login_auth(login_type, push_type, host_infos, command):
    global message
    message = 'serv00&ct8自动化脚本运行\n'
    # 登录方式
    if login_type == "ssh":
        message += ssh_multiple_connections(host_infos, command)
    elif login_type == "http":
        message += http_multiple_connections(host_infos)
    else:
        message += ssh_multiple_connections(host_infos, command)
    
    
    # 推送方式
    if push_type == "mail":
        mail_push('https://zzzwb.us.kg/test')
    elif push_type == "telegram":
        telegram_push(message)
    else:
        print("推送失败，推送参数设置错误")
    
    
def ssh_multiple_connections(host_infos, command) -> str:
    content = "SSH服务器登录信息：\n"
    
    stdout_contents = []
    hostnames = []
    for host_info in host_infos:
        hostname = host_info['hostname']
        username = host_info['username']
        password = host_info['password']
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=hostname, port=22, username=username, password=password)
            stdin, stdout, stderr = ssh.exec_command(command)
            stdout_content = stdout.read().decode().strip()
            print('ssh 回显信息：',stdout_content)
            stdout_contents.append(stdout_content)
            hostnames.append(hostname)
            ssh.close()
        except Exception as e:
            print(f"用户：{username}，连接 {hostname} 时出错: {str(e)}")
    
    content += "SSH服务器登录信息：\n"
    user_num = len(stdout_contents)
    for msg, hostname in zip(hostnames, hostnames):
        content += f"服务器：{hostname},回显信息：{msg}\n"
    
    beijing_timezone = timezone(timedelta(hours=8))
    time = datetime.now(beijing_timezone).strftime('%Y-%m-%d %H:%M:%S')
    # menu = requests.get('https://api.zzzwb.com/v1?get=tg').json()
    loginip = requests.get('https://api.ipify.org?format=json').json()['ip']
    
    content += f"本次登录用户共： {user_num} 个\n登录时间：{time}\n登录IP：{loginip}"
    return content


def http_multiple_connections(host_infos):
    for host_info in host_infos:
        hostname = host_info['hostname']
        username = host_info['username']
        password = host_info['password']
        panel = host_info['panel']
        
        url = f'https://{panel}/login/?next=/'

# push = os.getenv('PUSH')

def mail_push(url, content):
    data = {
        "body": content,
        "email": os.getenv('MAIL')
    }

    response = requests.post(url, json=data)

    try:
        response_data = json.loads(response.text)
        if response_data['code'] == 200:
            print("推送成功")
        else:
            print(f"推送失败，错误代码：{response_data['code']}")
    except json.JSONDecodeError:
        print("连接邮箱服务器失败了")

def telegram_push(msg):
    menu = requests.get('https://api.zzzwb.com/v1?get=tg').json()
    
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
    payload = {
        'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
        'text': msg,
        'parse_mode': 'HTML',
        'reply_markup': json.dumps({
            "inline_keyboard": menu,
            "one_time_keyboard": True
         })
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"发送消息到Telegram失败: {response.text}")

if __name__ == '__main__':
    main_fuc()
