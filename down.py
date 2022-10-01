"""
@Author: wfyr
@Date: 2022-2-13
@Description: 下架商品
"""

# selenium.common.exceptions.InvalidCookieDomainException: Message: invalid cookie domain: Cookie 'domain' mismatch，检查一下domain的域名是否一致
# 不登陆无法访问的页面：先录入cookies，再打开登陆后的网址

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import sys
import winsound

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


def main():
    # yn = int(input('1、有头\n2、无头\n选择：'))
    yn = 1
    if yn != 1 and yn != 2:
        print('无效输入')
        sys.exit()

    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.get('https://myseller.taobao.com/')  # 登录

    input("按任意键开始：")
    cookies = driver.get_cookies()
    print(cookies)
    print(json_to_string(list_to_json(cookies)))
    num = 50  # 下架多少次刷新一次，不能大于50

    if yn == 1:
        pass
    elif yn == 2:  # 无头
        cookies = driver.get_cookies()
        driver.quit()

        options.add_argument('--headless')
        options.add_argument('--disable-gpu')  # gpu显卡
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        driver.get('https://myseller.taobao.com/home.htm/QnworkbenchHome/')
        for cookie in cookies:
            cookie['domain'] = '.taobao.com'
        for cookie in cookies:
            driver.add_cookie(cookie)
        # 刷新页面
        driver.get('https://myseller.taobao.com/home.htm/QnworkbenchHome/')
        time.sleep(2)

    driver.get(
        'https://item.manager.taobao.com/taobao/manager/render.htm?tab=on_sale&table.sort.startDate_m=desc')  # 出售中的宝贝
    time.sleep(2)
    try:
        div = driver.find_element(By.CLASS_NAME, 'introjs-tooltipReferenceLayer')
        div.find_element(By.XPATH, './div/div[5]/a').click()  # 知道了
        time.sleep(2)
    except:
        print('没有按钮')
    driver.execute_script("var q=document.documentElement.scrollTop=400")

    n = 1
    while 1:
        while 1:
            try:
                driver.find_element(By.XPATH,  # 会报错
                                    '//*[@id="root"]/div/div/div[5]/div/div[1]/div/table/tbody/tr/th[1]/div/label/input').click()  # 点击全选
                break
            except:
                time.sleep(0.5)  # 1次
                pass
        time.sleep(1)

        try:
            bts = driver.find_elements(By.XPATH,
                                       '/html/body/div[3]/div/div[1]/div/div/div/div/div/div/div[4]/div/div/div[1]/button')
            for bt in bts:
                if bt.text == '批量下架':
                    bt.click()  # 点击批量下架
            time.sleep(1)
        except:
            driver.refresh()
            print('已刷新')
            time.sleep(10)
            driver.find_element(By.XPATH,
                                '//*[@id="root"]/div/div/div[5]/div/div[1]/div/table/tbody/tr/th[1]/div/label/input').click()  # 全选
            bts = driver.find_elements(By.XPATH,
                                       '/html/body/div[3]/div/div[1]/div/div/div/div/div/div/div[4]/div/div/div[1]/button')
            for bt in bts:
                if bt.text == '批量下架':
                    bt.click()  # 点击批量下架
            time.sleep(1)

        try:
            driver.find_element(By.XPATH, '/html/body/div[9]/div/div[2]/div[3]/button').click()  # 点击确认；网页小崩这里会报错
        except:
            driver.refresh()
            print('已刷新2')
            time.sleep(10)
            driver.find_element(By.XPATH,
                                '//*[@id="root"]/div/div/div[5]/div/div[1]/div/table/tbody/tr/th[1]/div/label/input').click()  # 全选
            bts = driver.find_elements(By.XPATH,
                                       '/html/body/div[3]/div/div[1]/div/div/div/div/div/div/div[4]/div/div/div[1]/button')
            for bt in bts:
                if bt.text == '批量下架':
                    bt.click()  # 点击批量下架
            time.sleep(1)
            driver.find_element(By.XPATH, '/html/body/div[9]/div/div[2]/div[3]/button').click()  # 点击确认
        print(f'批量下架{n}次')

        n1 = 1
        while 1:
            if n1 > 10:
                break
            try:
                driver.find_element(By.XPATH,
                                    '//*[@id="root"]/div/div/div[5]/div/div[1]/div/table/tbody/tr/th[1]/div/label/input').click()  # 等待点击全选
                break
            except:

                while True:
                    try:
                        driver.find_element(By.XPATH, '/html/body/div[7]/div[2]/iframe')
                        print('出现滑块验证')
                        winsound.Beep(500, 2000)
                        time.sleep(5)
                    except:
                        break

                time.sleep(1)  # 5、6次
                pass
            n1 += 1
        time.sleep(1)

        try:
            # 判断商品数量是否为0
            if driver.find_element(By.XPATH, '//*[@id="list-pagination-top-total"]').text == '0':
                print("商品数量为0，正在刷新页面...")
                driver.get(
                    'https://item.manager.taobao.com/taobao/manager/render.htm?tab=on_sale&table.sort.startDate_m=desc')  # 出售中的宝贝
                time.sleep(2)
                driver.execute_script("var q=document.documentElement.scrollTop=400")
                if driver.find_element(By.XPATH, '//*[@id="list-pagination-top-total"]').text == '0':
                    print('\n下架完成')
                    break

            # 判断页数是否相等
            a, b = driver.find_element(By.XPATH, '//*[@id="pagination-toolbar"]/div[2]/div/span').text.split("/")
            if a == b:
                driver.get(
                    'https://item.manager.taobao.com/taobao/manager/render.htm?tab=on_sale&table.sort.startDate_m=desc')  # 出售中的宝贝
                time.sleep(2)
                driver.execute_script("var q=document.documentElement.scrollTop=400")
                continue
        except:
            pass

        if n % num == 0:
            driver.refresh()
            print('网页已刷新')
            time.sleep(8)

        # button[1]上一页，button[2]下一页
        try:  # 此处会出现验证码
            driver.find_element(By.XPATH, '//*[@id="pagination-toolbar"]/div[2]/div/button[2]').click()  # 点击下一页
        except:
            driver.refresh()
            print('已刷新3')
            time.sleep(2)
            driver.find_element(By.XPATH, '//*[@id="pagination-toolbar"]/div[2]/div/button[2]').click()  # 点击下一页
        time.sleep(1)
        n += 1

    input('\n已完成，按任意键退出：')


if __name__ == '__main__':
    main()

# 纪博严:产品上架
# qwe123456

# if driver.find_element(By.XPATH, '/html/body/div[9]/div/div[2]/div[2]/span').text == '亲，您的操作速度太快了，请您稍等一会儿再试':
# if '查看详情' in driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[5]').text:
