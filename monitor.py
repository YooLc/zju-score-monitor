# 吐槽：
# 为什么会有人变态到想第一时间查到自己成绩啊....

import os
import time
import hmac
import json
import base64
import hashlib
import requests
import urllib.parse
import zjuam.zjuam

ACCESS_TOKEN = '' # 钉钉机器人的 Access Token
SECRET = ''       # 钉钉机器人加签的 Secret
USERNAME = ''     # 学号
PASSWORD = ''     # 密码
CURRENT_SEMESTER = ''  # 查询成绩 / 计算均绩的学年

login = zjuam.login(USERNAME, PASSWORD)

def dingtalk_push(title, message):
    # 机器人加签
    # 文档: https://open.dingtalk.com/document/robots/custom-robot-access
    timestamp = str(round(time.time() * 1000))
    secret = SECRET
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    webHook = 'https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}'.format(ACCESS_TOKEN, timestamp, sign)
    # 推送至群聊
    data = {
        'msgtype': 'markdown',
        'markdown': {
            'title': title,
            'text': message
        }
    }
    response = requests.post(webHook, json = data)
    data = response.json()
    if (data['errcode']):
        print('Dingtalk push error!\nError Code: {}\nError message: {}'\
              .format(str(data['errcode']), data['errmsg']))

def get_score_list():
    url = 'http://appservice.zju.edu.cn/zju-smartcampus/zdydjw/api/kkqk_cxXscjxx'
    response = login.session.post(url = url)
    data = response.json()
    if int(data['error_code']):
        dingtalk_push('成绩查询出错', '[一团乱麻]**成绩查询出错！**\n\n错误代码: {}\n\n错误信息: {}'\
                      .format(data['error_code'], data['message']))
        print('Cannot get score! Please check cookies setting. \nError code: {}\nError message: {}'\
              .format(data['error_code'], data['message']))
        return 
    return response.json()['data']['list']

def calculate_gpa(scoreList):
    totalPoint = 0
    gradePoint = 0
    for course in scoreList:
        if course['xn'] != CURRENT_SEMESTER or course['cj'] in ['缺考', '缓考', '无效', '弃修', 'W', 'null', 'Q']:
            continue
        totalPoint = totalPoint + float(course['xf'])
        gradePoint = gradePoint + float(course['xf']) * course['jd']
    gradePointAverage = gradePoint / totalPoint
    return round(gradePointAverage, 2)

def score_monitor(curList, preList):
    changed = False
    preGPA = calculate_gpa(preList)
    curGPA = calculate_gpa(curList)
    for course in curList:
        if course in preList:
            continue
        # 出分提醒
        title = '你的【{}】出分啦！'.format(course['kcmc'])
        message = '[撒花]你修读的【**{}**】出分啦！\n\n[二哈]你的成绩为:【**{}**】\n\n[狗子]获得绩点:【**{}**】'\
                   .format(course['kcmc'], course['cj'], course['jd'])
        dingtalk_push(title, message)
        # 绩点提醒
        deltaGPA = curGPA - preGPA
        if deltaGPA > 0:
            title = '【{}】出分绩点变动提醒'.format(course['kcmc'])
            message = '[等一等]**检测到绩点变动**\n\nGPA: **{:.2f}** (+{:.2f}) [撒花]' \
                    .format(curGPA, deltaGPA)
            dingtalk_push(title, message)
        elif deltaGPA < 0:
            title = '【{}】出分绩点变动提醒'.format(course['kcmc'])
            message = '[等一等]**检测到绩点变动**\n\nGPA: **{:.2f}** (-{:.2f}) [跪了]' \
                    .format(curGPA, -deltaGPA)
            dingtalk_push(title, message)
        print("Score has changed!")
        print(course)
        changed = True
    if not changed:
        print("Score was unchanged.")

def main():
    # 第一次运行
    if not os.path.exists('preList.json'):
        curList = get_score_list()
        with open('preList.json', 'w', encoding = 'utf-8') as file:
            json.dump(curList, file)
            # json.dump(curList, file, indent = 4, ensure_ascii = False)
        dingtalk_push('成绩查询机器人设置成功', '成绩查询机器人设置成功！\n\n祝主人门门满绩~[100分]')
        print("Score file created and saved.")
        return

    # 对成绩更新进行监控
    with open('preList.json', encoding = 'utf-8') as file:
        preList = json.load(file)
    curList = get_score_list()

    # 处理查询出错的情况
    if curList is None:
        print('Something wrong with score checking.')
        return
    if preList is None:
        preList = curList
    
    score_monitor(curList, preList)
    
    # 写入变动
    with open('preList.json', 'w', encoding = 'utf-8') as file:
        json.dump(curList, file)
        # json.dump(curList, file, indent = 4, ensure_ascii = False)

if __name__ == '__main__':
    main()