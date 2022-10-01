"""
下架商品
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains  # .perform()
import requests
import json


def list_to_json(cookie):  # 将selenium获取的cookie列表整理成字典
    cookie_json = {}
    for i in cookie:
        cookie_json[i['name']] = i['value']
    return cookie_json


def json_to_string(cookies):  # 将cookies字典整理成字符串
    cookie = ''
    for i in cookies:
        cookie += i + '=' + cookies[i] + ';'
    return cookie


def list_to_str(_list):  # 将列表转换为参数需要的字符串格式
    s = '['
    for i in _list:
        s += '"' + i + '"' + ','
    s = s[:-1] + ']'
    return s


uid = ''  # 账号
pwd = ''  # 密码

# selenium获取cookie
options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.get('https://myseller.taobao.com/')  # 登录页面
time.sleep(1)

iframe = driver.find_element(By.ID, 'alibaba-login-box')
driver.switch_to.frame(iframe)
driver.find_element(By.ID, 'fm-login-id').send_keys(uid, Keys.TAB, pwd, Keys.ENTER)  # 输入账号密码登录，第一次登录需要手机验证码
driver.switch_to.default_content()

# 如果有手机验证码或滑块验证码要手动过验证码之后，在主页面的时候才能继续运行程序
input("按任意键开始：")
cookies = driver.get_cookies()
cookie = json_to_string(list_to_json(cookies))
print(cookie)
print('=' * 100)

ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36'

# 获取x-xsrf-token，从XSRF-TOKEN
url = 'https://item.upload.taobao.com/taobao/manager/render.htm?tab=on_sale&StringUtils=class+org.apache.commons.lang3.StringUtils&smart_publish_version_switch=0.4.44'
headers = {
    'cookie': cookie,
    'user-agent': ua
}
resp = requests.get(url, headers=headers)
print(resp)
# print(resp.text)
# print(resp.headers)
set_cookie = requests.utils.dict_from_cookiejar(resp.cookies)  # 从响应头整理出set-cookie
print(set_cookie)
print('=' * 100)
resp.close()

current_page = 1  # 当前页
no_data = False  # 判断标志：是否还有数据
while 1:
    print(f'第{current_page}页')

    # 获取一页的itemId
    url2 = 'https://item.upload.taobao.com/taobao/manager/table.htm'
    headers2 = {
        'cookie': cookie + f'XSRF-TOKEN={set_cookie["XSRF-TOKEN"]}',
        'referer': f'https://item.upload.taobao.com/taobao/manager/render.htm?StringUtils=class%20org.apache.commons.lang3.StringUtils&pagination.current={current_page}&pagination.pageSize=20&smart_publish_version_switch=0.4.44&tab=on_sale',
        'user-agent': ua,
        'x-xsrf-token': set_cookie["XSRF-TOKEN"]
    }
    # current为请求的页码
    data2 = {
        'jsonBody': '{"filter": {}, "pagination": {"current": ' + str(current_page) + ', "pageSize": 20}, "table": {"sort": {}}, "tab": "on_sale"}'
    }
    resp2 = requests.post(url2, headers=headers2, data=data2)
    print(resp2)
    # print(resp2.text)
    # print(resp2.headers)
    resp2_json = json.loads(resp2.text)
    print(f"总数：{resp2_json['data']['pagination']['total']}，共{math.ceil(int(resp2_json['data']['pagination']['total']) / int(resp2_json['data']['pagination']['pageSize']))}页")
    itemId_list = []
    for i in resp2_json['data']['table']['dataSource']:
        itemId_list.append(i['itemId'])
    if len(itemId_list) == 0:
        if no_data:  # 连续两次数据为0才会执行，证明已没有数据
            print('暂无数据hhh')
            break
        print('已是最后一页hhh')
        current_page = 1
        no_data = True
        continue
    print(itemId_list)
    resp2.close()

    # 下架商品
    url3 = 'https://item.upload.taobao.com/taobao/manager/batchFastEdit.htm?optType=batchDownShelf&action=submit'
    data3 = {
        'jsonBody': '{"auctionids":' + list_to_str(itemId_list) + '}'
    }
    # 请求频繁会出现“亲~人太多，被挤爆了！”
    resp3 = requests.post(url3, headers=headers2, data=data3)
    print(resp3)
    print(resp3.text)
    if '亲~人太多，被挤爆了！' in resp3.text:
        print('亲~人太多，被挤爆了！hhh')
        time.sleep(5)
    else:  # 下架成功
        current_page += 1
        time.sleep(1)
    print('=' * 100)
    resp3.close()
    no_data = False
