from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as Soup
from lxml import html
import facebook_scraper as fs
import re
from func import load_file, save_file
import asyncio

async def crawl_fb():
    settings = load_file('settings.json')
    # ------ 設定要前往的網址 ------
    url = 'https://mbasic.facebook.com'

    # ------ 登入的帳號與密碼 ------
    username = settings['fb_username']
    password = settings['fb_pwd']

    options = Options()
    options.binary_location = "./webdriver"
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="m_login_email"]')))

    elem = driver.find_element(by=By.ID, value="m_login_email")
    elem.send_keys(username)

    elem = driver.find_element(by=By.XPATH, value='//*[@id="password_input_with_placeholder"]/input')
    elem.send_keys(password)        

    elem.send_keys(Keys.RETURN)
    await asyncio.sleep(5)

    #檢查有沒有被擋下來
    if len(driver.find_elements(by=By.XPATH, value="//*[contains(text(), '你的帳號暫時被鎖住')]")) > 0:
        driver.find_elements(by=By.XPATH, value="//*[contains(text(), '是')]")[1].click()

    # 切換頁面
    spec_url = 'https://mbasic.facebook.com/profile.php?id=100090573221915&v=timeline'
    driver.get(spec_url)
    await asyncio.sleep(5)

    url_next = ''
    for i in range(3):
        soup = Soup(driver.page_source, "lxml")
        articles = soup.find_all('article')
        # 貼文連結
        urls = []
        # 貼文圖片連結
        urls2 = []
        # 正常貼文連結
        urls3 = []
        for article in articles:
            #每一篇貼文
            temp = []
            article_tree = html.fromstring(str(article))
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
                driver.get(item)
                item_index = urla.index(item)
                await asyncio.sleep(5)
                soup = Soup(driver.page_source, "lxml")
                image = soup.find('div', class_='s')
                image_tree = html.fromstring(str(image))
                image_id = image.get('id')
                xpath_to_find = f'//*[@id="{image_id}"]/div/div[1]/div/div[1]/div/img'
                elements = image_tree.xpath(xpath_to_find)
                for element in elements:
                    urla[item_index] = element.get('src')
                await asyncio.sleep(3)

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
            driver.get(url)
            await asyncio.sleep(3)
            read_more_xpath = '/html/body/div/div/div[2]/div/div[1]/div[3]/div[2]/div/div[1]/a'
            buttons = html.fromstring(str(driver.page_source)).xpath(read_more_xpath)
            for button in buttons:
                url_next= button.get('href')
            driver.get('https://mbasic.facebook.com' + url_next)
            await asyncio.sleep(3)
        else:
            driver.get('https://mbasic.facebook.com' + url_next)
            await asyncio.sleep(3)
            read_more_xpath = '/html/body/div/div/div[1]/div/table/tbody/tr/td/div/div[1]/a'
            buttons = html.fromstring(driver.page_source).xpath(read_more_xpath)
            for button in buttons:
                url_next= button.get('href')
            driver.get('https://mbasic.facebook.com' + url_next)
            await asyncio.sleep(3)