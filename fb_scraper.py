from bs4 import BeautifulSoup as Soup
from lxml import html
import facebook_scraper as fs
import re
from func import load_file, save_file
import asyncio
import time
import requests
from urllib.parse import urlencode

def crawl_fb():
    settings = load_file('settings.json')
    username = settings['fb_username']
    password = settings['fb_pwd']
    session = requests.Session()
    headers = {
        'Host': 'www.facebook.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Connection': 'close',
    }

    response = session.get('https://www.facebook.com/', headers=headers)
    fr=response.cookies['fr']
    sb=response.cookies['sb']
    _datr=response.text.split('"_js_datr","')[1].split('"')[0]
    _token=response.text.split('privacy_mutation_token=')[1].split('"')[0]
    _jago=response.text.split('"jazoest" value="')[1].split('"')[0]
    _lsd=response.text.split('name="lsd" value="')[1].split('"')[0]

    cookies = {
        'fr': fr,
        'sb': sb,
        '_js_datr': _datr,
        'wd': '717x730',
        'dpr': '1.25',
    }

    data = urlencode({
        'jazoest': _jago,
        'lsd': _lsd,
        'email': username,
        'login_source': 'comet_headerless_login',
        'next': '',
        'encpass': f'#PWD_BROWSER:0:{round(time.time())}:{password}',
    })

    headers = {
        'Host': 'www.facebook.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'https://www.facebook.com/',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': str(len(data)),
        'Origin': 'https://www.facebook.com',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
    }

    response = session.post(f'https://www.facebook.com/login/?privacy_mutation_token={_token}', cookies=cookies, headers=headers, data=data)
    print(response.cookies.get_dict())

    if 'should_show_close_friend_badge":false' in response.text:
        print('Login Success ')
    else:
        print(response.content)
        
    black_hchs_url = 'https://mbasic.facebook.com/profile.php?id=100090573221915&v=timeline'
    response = session.get(black_hchs_url)
    
    url_next = ''
    for i in range(3):
        soup = Soup(response.content, "lxml")
        articles = soup.find_all('div', {'data-ft': True})
        # 貼文連結
        urls = []
        # 貼文圖片連結
        urls2 = []
        # 正常貼文連結
        urls3 = []
        for article in articles:
            #每一篇貼文
            temp = []
            article_tree = html.fromstring(article)
            article_id = article.get('id')
            xpath_to_find1 = f'//*[@id="{article_id}"]/footer/div[2]/a[3]'
            xpath_to_find2 = f'//*[@id="{article_id}"]/div/div[2]/div[1]/a'
            elements1 = article_tree.xpath(xpath_to_find1)
            elements2 = article_tree.xpath(xpath_to_find2)
            for element in elements1:
                urls.append('https://mbasic.facebook.com' + element.get('href'))
                urls3.append('https://www.facebook.com' + element.get('href'))
            for element in elements2:
                temp.append('https://mbasic.facebook.com' + element.get('href'))
            urls2.append(temp)

        # urls2 = [[貼文一], [貼文二], [貼文三 ]]
        for urla in urls2:
            for item in urla:
                item_response = session.get(item)
                item_index = urla.index(item)
                soup = Soup(item_response.content, "lxml")
                image_tree1 = html.fromstring(item_response.text)
                xpath_to_find = '/html/body/div/div/div[2]/div/div[1]/div'
                image_id1 = image_tree1.xpath(xpath_to_find)[0].get('id')
                image = soup.find('div', id=image_id1)
                image_tree = html.fromstring(image)
                image_id = image.get('id')
                xpath_to_find = f'//*[@id="{image_id}"]/div/div[1]/div/div[1]/div/img'
                elements = image_tree.xpath(xpath_to_find)
                for element in elements:
                    urla[item_index] = element.get('src')

        posts = fs.get_posts(
            post_urls=urls3,
            credentials=(username, password),
            options={"comments": True, "reactors": True, "allow_extra_requests": True}
        )
        post_data = load_file('black_hchs.json')

        for post, urll in zip(posts, urls2):
            number_match = re.search(r'#黑色麻中(\d+)', post['post_text'])
            if number_match:
                number = number_match.group(1)
            date_match = re.search(r'投稿日期：  (.+)', post['post_text'])
            date = date_match.group(1) if date_match else None
            if number in post_data:
                post_data[number]['commments_full'] = post['comments_full']
                post_data[number]['commments'] = post['comments']
                post_data[number]['reactions'] = post['reactions']
                post_data[number]['reactors'] = post['reactors']
                save_file('black_hchs.json', post_data)
            else:
                post_data.update({
                    number: {
                        "date": date,
                        "content": post['post_text'],
                        "images": urll,
                        "comments": post['comments'],
                        "comments_full": post['comments_full'], 
                        "reactions": post['reactions'],
                        "reactors": post['reactors']
                    }
                })

                save_file('black_hchs.json', post_data)

        if i == 0:
            url = 'https://mbasic.facebook.com/profile.php?id=100090573221915&v=timeline'
            response = session.get(url)   
            read_more_xpath = '/html/body/div/div/div[2]/div/div[1]/div[3]/div[2]/div/div[1]/a'
            buttons = html.fromstring(response.content).xpath(read_more_xpath)
            for button in buttons:
                url_next= button.get('href')
            response = session.get('https://mbasic.facebook.com' + url_next)
        else:
            response = session.get('https://mbasic.facebook.com' + url_next)
            read_more_xpath = '/html/body/div/div/div[1]/div/table/tbody/tr/td/div/div[1]/a'
            buttons = html.fromstring(response.content).xpath(read_more_xpath)
            for button in buttons:
                url_next= button.get('href')
            response = session.get('https://mbasic.facebook.com' + url_next)