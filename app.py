import requests
from flask import Flask, request, make_response, redirect
from urllib.parse import unquote
import mimetypes
import urllib.parse
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from threading import Thread
from bs4 import BeautifulSoup
import json
import random
import time
import validators
from validators.utils import ValidationError

app = Flask(__name__)

unichr = chr


def unquote_unicode(string, _cache={}):
  string = unquote(string)  # handle two-digit %hh components first
  parts = string.split(u'%u')
  if len(parts) == 1:
    return parts
  r = [parts[0]]
  append = r.append
  for part in parts[1:]:
    try:
      digits = part[:4].lower()
      if len(digits) < 4:
        raise ValueError
      ch = _cache.get(digits)
      if ch is None:
        ch = _cache[digits] = unichr(int(digits, 16))
      if (not r[-1] and u'\uDC00' <= ch <= u'\uDFFF'
          and u'\uD800' <= r[-2] <= u'\uDBFF'):
        # UTF-16 surrogate pair, replace with single non-BMP codepoint
        r[-2] = (r[-2] + ch).encode('utf-16', 'surrogatepass').decode('utf-16')
      else:
        append(ch)
      append(part[4:])
    except ValueError:
      append(u'%u')
      append(part)
  return u''.join(r)


# 用於存儲短網址的字典
try:
  with open('short_urls.json', 'r') as file:
    short_urls = json.load(file)
except FileNotFoundError:
  short_urls = {}


# 驗證key的函數
def validate_key(key):
  return key == "jimmyishandsome"


# 生成唯一的短網址的key
def generate_unique_short_key():
  characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
  while True:
    short_key = ''.join(random.choice(characters) for _ in range(5))
    if short_key not in short_urls:
      return short_key


@app.route('/')
def index():
  news_id = request.args.get('id')
  g_root_path = 'https://www.hchs.hc.edu.tw/ischool/'
  news_unique_id = request.args.get('news_unique_id')
  resource_folder = request.args.get('res_folder')
  file_name = request.args.get('res_name')
  res = f"{g_root_path}resources/{news_unique_id}/{resource_folder}/attached/{file_name}"
  url = f'https://www.hchs.hc.edu.tw/ischool/public/news_view/show.php?nid={news_id}'
  if news_id != None and news_unique_id != None and resource_folder != None and file_name != None:
    # 設定首次請求的URL和Headers
    url_first = url
    headers_first = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    # 發送首次請求，獲取Cookies
    response_first = requests.get(url_first, headers=headers_first)
    cookies = response_first.cookies

    # 設定第二次請求的URL和Headers
    url_second = res
    headers_second = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Referer": url_first,  # 引用來源網址
        "Cookie": f"PHPSESSID={cookies}"
    }

    # 發送第二次請求，使用之前取得的Cookies和原本的Headers
    response_second = requests.get(url_second,
                                   headers=headers_second,
                                   cookies=cookies)

    # http://localhost:5000/?id=6087&news_unique_id=WID_13_2_4edf85a1c7791721ccf4b29a28fc50de439cd73c&res_folder=NEWS_13_2_120d39fa1f2e375b45a4c7a2160d6292a26cb8d8&res_name=%E6%96%B0%E7%AB%B9%E9%AB%98%E4%B8%AD112%E5%AD%B8%E5%B9%B4%E5%BA%A6%E7%AC%AC%E4%B8%80%E5%AD%B8%E6%9C%9F%E5%B0%88%E8%BB%8A%E5%90%8D%E5%96%AE.xlsx
    # 建立包含第二次回應內容的回應物件，並加入原本的Headers
    response = make_response(response_second.content)
    if url_second.endswith('.pdf'):
      response.headers['Content-Type'] = 'application/pdf'
    elif url_second.endswith('.jpg'):
      response.headers['Content-Type'] = 'image/jpeg'
    elif url_second.endswith('.jpeg'):
      response.headers['Content-Type'] = 'image/jpeg'
    elif url_second.endswith('.png'):
      response.headers['Content-Type'] = 'image/png'
    elif url_second.endswith('.gif'):
      response.headers['Content-Type'] = 'image/gif'
    elif url_second.endswith('.bmp'):
      response.headers['Content-Type'] = 'image/bmp'
    elif url_second.endswith('.tiff'):
      response.headers['Content-Type'] = 'image/tiff'
    elif url_second.endswith('.webp'):
      response.headers['Content-Type'] = 'image/webp'
    else:
      # 設定回應的Content-Type
      if 'Content-Type' in response.headers:
        response.headers['Content-Type'] = response.headers['Content-Type']

      # 使用mimetypes模組根據Content-Type來取得副檔名
      content_type = response.headers.get('Content-Type', '')
      extension = mimetypes.guess_extension(content_type)

      # 如果無法判斷副檔名，預設使用.bin副檔名
      if not extension:
        extension = '.bin'

      # 設定回應的Content-Disposition為attachment，指示瀏覽器下載而非預覽
      filename = urllib.parse.quote(unquote_unicode(file_name)[0])
      response.headers[
          'Content-Disposition'] = f'attachment; filename="{filename}"'

    for key, value in headers_second.items():
      response.headers[key] = value

    return response

  elif news_unique_id == None or resource_folder == None or news_id == None or file_name == None:
    return redirect('/error?flag=no_args')
  else:
    return redirect('/error')


@app.route('/error')
def error():
  flag = request.args.get('flag')
  if flag == 'no_args':
    return '找不到參數', 404
  else:
    return 'error'


@app.route('/images')
def show_image():
  id = request.args.get('id')
  image_url = f"https://www.hchs.hc.edu.tw/ischool/public/news_view/show.php?nid={id}"
  image_filename = request.args.get('name')

  url_first = image_url
  headers_first = {
      "User-Agent":
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
  }

  # 發送首次請求，獲取Cookies
  response_first = requests.get(url_first, headers=headers_first)
  cookies = response_first.cookies

  soup = BeautifulSoup(response_first.text, 'html.parser')

  # 找到所有的<img>标签
  img_tags = soup.find_all('img')
  for image_tag in img_tags:
    src = image_tag.get('src')
    if src.endswith(image_filename):
      img_src = src

  # 設定第二次請求的URL和Headers
  url_second = img_src
  headers_second = {
      "User-Agent":
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
      "Referer": url_first,  # 引用來源網址
      "Cookie": f"PHPSESSID={cookies}"
  }

  # 發送第二次請求，使用之前取得的Cookies和原本的Headers
  response_second = requests.get(url_second,
                                 headers=headers_second,
                                 cookies=cookies)

  # 建立包含第二次回應內容的回應物件，並加入原本的Headers
  response = make_response(response_second.content)

  if url_second.endswith('.jpg'):
    response.headers['Content-Type'] = 'image/jpeg'
  elif url_second.endswith('.jpeg'):
    response.headers['Content-Type'] = 'image/jpeg'
  elif url_second.endswith('.png'):
    response.headers['Content-Type'] = 'image/png'
  elif url_second.endswith('.gif'):
    response.headers['Content-Type'] = 'image/gif'
  elif url_second.endswith('.bmp'):
    response.headers['Content-Type'] = 'image/bmp'
  elif url_second.endswith('.tiff'):
    response.headers['Content-Type'] = 'image/tiff'
  elif url_second.endswith('.webp'):
    response.headers['Content-Type'] = 'image/webp'

  return response


def is_string_an_url(url_string: str) -> bool:
  if ValidationError:
    return False
  result = validators.url(url_string)
  return result


# 將短網址映射到原始URL
@app.route('/shorturl', methods=['GET'])
def create_short_url():
  key = request.args.get('key')
  full_url = request.full_path  # 获取完整的请求路径，包括查询参数

  # 使用urlparse解析URL
  parsed_url = urlparse(full_url)

  # 提取URL中的查询参数
  query_params = parse_qs(parsed_url.query)

  # 移除key参数
  query_params.pop('key', None)

  # 重新构建URL
  updated_query_string = urlencode(query_params, doseq=True)
  updated_url = urlunparse(parsed_url._replace(query=updated_query_string))
  decoded_url = unquote(updated_url[len('/shorturl?url='):])

  # 检查是否已存在相同的decoded_url，如果是，获取现有的short_key
  existing_short_key = next(
      (k for k, v in short_urls.items() if v == decoded_url), None)

  if not validate_key(key):
    return "Invalid key", 401
  elif existing_short_key:
    return f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/redirect?short_key={existing_short_key}'
  elif is_string_an_url(decoded_url) == False:
    return "Invalid URL", 404

  # 生成唯一的短網址的key
  short_key = generate_unique_short_key()

  # 將短網址映射到原始URL
  short_urls[short_key] = decoded_url

  # 寫入短網址映射到JSON文件
  with open('short_urls.json', 'w') as file:
    json.dump(short_urls, file, indent=4)

  return f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/redirect?short_key={short_key}'


@app.route('/<key>', methods=['GET'])
def redirect_to_original_url(key):
  if key in short_urls:
    return redirect(short_urls[key])
  else:
    return "Short URL not found", 404


def run():
  app.run(host="0.0.0.0", port=8080, debug=False)


def send_request():
  while True:
    # 发送GET请求到指定的URL
    url = "https://alivesrfewsdfcdrwerfdwe.jimmy20180130.repl.co"
    response = requests.get(url)

    # 打印响应内容和状态码
    print(f"網站 {url} : {response.status_code}")

    # 等待60秒再次发送请求
    time.sleep(60)


def keep_alive():
  server = Thread(target=run)
  request_thread = Thread(target=send_request)  # Rename the variable here
  server.start()
  request_thread.start()
