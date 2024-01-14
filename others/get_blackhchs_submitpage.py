# 取得 https://submit.crush.ninja/116761461339363 上面提交的貼文

import json
import requests
from bs4 import BeautifulSoup
import re

url = "https://www.crush.ninja/zh-tw/pages/116761461339363"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
contents = soup.find('div', class_='container').find_all('div', class_='p-1')

with open('black_hchs.json', 'r', encoding='utf-8') as files:
    post_data = json.load(files)

for item in contents:
    content = item.get_text()

    number_match = re.search(r'#黑色麻中(\d+)', content)
    if number_match:
        number = number_match.group(1)
    else:
        continue

    date_match = re.search(r'投稿日期：  (.+)', content)
    date = date_match.group(1) if date_match else None

    post_data[number] = {"date": date, "content": content-date_match}

    with open('black_hchs.json', 'w', encoding='utf-8') as file:
        json.dump(post_data, file, indent=4, ensure_ascii=False)