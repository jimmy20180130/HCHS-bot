import requests
import random
import time
import hashlib
import xml.etree.ElementTree as ET
from func import is_string_an_url
import tracemalloc
import json

tracemalloc.start()

with open('settings.json', 'r', encoding='utf-8') as settings_file:
  setting = json.load(settings_file)

URL_ROOT = setting['url_root']
SHORT_URL_KEY = setting['key']


# def shrtco_de(url):
#   shortener_url = f'https://api.shrtco.de/v2/shorten?url={url}'
#   shorted_url = requests.get(shortener_url)
#   if shorted_url.status_code == 201:
#     return shorted_url.json()['result']['full_short_link']
#   else:
#     return 'error'


def short_repl_it_url(url, key):
  urla = is_string_an_url(url)
  if urla is None or urla == '':
    return 'error,invalid_url'
  url = f'{URL_ROOT}shorturl?key={key}&url={url}'
  response = requests.post(url).text
  return response


def surl_cc(url, filename=None):
  urla = is_string_an_url(url)
  if urla is None or urla == '':
    return 'error,invalid_url'
  ssur_cc_key_list = [
      'nZ9ZzSa4LZ4o', 'Ed8nLSFpNVGB', 'YJimrVqxmExf', 'L9YRXGPugtet',
      'HR7RDeKNVgTX', 'RKqh9qcjDoe4', 'XoWtP22exnmy', 'GGFedvn7yhFZ',
      'yJpFtTfXNZVi', 'MqQsBMbCvthf', 'MqQsBMbCvthf', 'vMd8zBusHzKk',
      'ZYhVdSnyyEH6', '4XKRnpnNEUYX', '84zd7S9HP7CF', 'PtpgRsxM5ozh'
  ]
  ssur_cc_key = random.choice(ssur_cc_key_list)
  if filename is not None:
    ssur_cc_shortener_url_custom = f'https://ssur.cc/api.php?appkey={ssur_cc_key}&format=text&longurl={url}'
  else:
    ssur_cc_shortener_url_custom = f'https://ssur.cc/api.php?appkey={ssur_cc_key}&longurl={url}'
  ssur_cc_shorted_url_custom = requests.get(ssur_cc_shortener_url_custom).text
  try:
    if ssur_cc_shorted_url_custom:
      return ssur_cc_shorted_url_custom
  except Exception as e:
    print(f'連接到ssur.cc的api時發生了一個錯誤\n{e}')
    return 'error'


def short_88nb_cc(url):
  urla = is_string_an_url(url)
  if urla is None or urla == '':
    return 'error'
  short_88nb_cc_key_list = [
      'ea8d7b3ded', 'b89377c881', 'b6fc6a3133', '44ccb4f4b2', '120ef9330f'
  ]
  short_88nb_cc_key = random.choice(short_88nb_cc_key_list)
  # timestamp
  timestamp = str(int(time.time()))
  api_url = 'https://88nb.cc/88nb-api.php'
  # signature
  signature = hashlib.md5((timestamp + short_88nb_cc_key).encode()).hexdigest()
  # data
  data = {
      'url': url,
      'action': 'shorturl',
      'timestamp': timestamp,
      'signature': signature
  }
  # POST request
  short_88nb_cc_shorted_url_response = requests.post(api_url, data=data).text
  root = ET.fromstring(short_88nb_cc_shorted_url_response)
  try:
    short_88nb_cc_shorted_url = root.find("./shorturl").text
    return short_88nb_cc_shorted_url
  except Exception as e:
    print(f'連接到88nb.cc的api時發生了一個錯誤\n{e}')
    return 'error'


def urlcc_cc(url):
  urla = is_string_an_url(url)
  if urla is None or urla == '':
    return 'error'
  urlcc_cc_key_list = ['86bcb4ac40', 'a5b036890f']
  urlcc_cc_key = random.choice(urlcc_cc_key_list)
  urlcc_cc_shortener_url = f'https://urlcc.cc/api.php?appkey={urlcc_cc_key}&longurl={url}'
  urlcc_cc_shorted_url = requests.get(urlcc_cc_shortener_url).json()
  try:
    urlcc_cc_url_data = urlcc_cc_shorted_url['sh_url']
    return urlcc_cc_url_data
  except Exception as e:
    print(f'連接到urlcc.cc的api時發生了一個錯誤\n{e}')
    return 'error'
