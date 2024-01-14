# 取得學校網站的所有公告

import requests
from bs4 import BeautifulSoup
import json
import threading
import time

# 儲存結果的字典
result = {}

def request(start, end):
    # 迴圈範圍：從1到9999
    for id in range(start, end):
        url = f"https://www.hchs.hc.edu.tw/ischool/public/news_view/show.php?nid={id}"

        response = requests.get(url)
        html = response.text
        if html != 'The news is not existed!' and html != '該消息已封存，所以無法開啟！':
            soup = BeautifulSoup(html, 'lxml')

            # 提取標題
            title_element = soup.find('h4')
            title = title_element.text.strip()

            result[id] = title
            print(f"ID: {id}, Title: {title}")
        else:
            result[id] = "None"
            print(f"ID: {id}, Title: None")
        
        while True:
            try:
                with open('news.json', 'w', encoding='utf-8') as json_file:
                    json.dump(result, json_file, ensure_ascii=False, indent=4)
                break
            except Exception as e:
                print(f"An error occurred: {str(e)}")

t1 = threading.Thread(target=request, args=(1, 1000))  #建立執行緒
t2 = threading.Thread(target=request, args=(1001, 2000))  #建立執行緒
t3= threading.Thread(target=request, args=(2001, 3000))  #建立執行緒
t4= threading.Thread(target=request, args=(3001, 4000))  #建立執行緒
t5= threading.Thread(target=request, args=(4001, 5000))  #建立執行緒
t6= threading.Thread(target=request, args=(5001, 6000))  #建立執行緒
t7= threading.Thread(target=request, args=(6001, 7000))  #建立執行緒
t8= threading.Thread(target=request, args=(7001, 8000))  #建立執行緒
t9= threading.Thread(target=request, args=(8001, 9000))  #建立執行緒
t10= threading.Thread(target=request, args=(9001, 10000))  #建立執行緒
t1.start()  #執行
t2.start()  #執行
t3.start()  #執行
t4.start()  #執行
t5.start()  #執行
t6.start()  #執行
t7.start()  #執行
t8.start()  #執行
t9.start()  #執行
t10.start()  #執行