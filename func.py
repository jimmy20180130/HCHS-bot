import requests
from urllib.parse import unquote
import re
import json

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


def is_string_an_url(url_string: str) -> bool:
  regex = re.compile(
      r'^(?:http|ftp)s?://'  # http:// or https://
      r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  #domain...
      r'localhost|'  #localhost...
      r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
      r'(?::\d+)?'  # optional port
      r'(?:/?|[/?]\S+)$',
      re.IGNORECASE)
  link = re.match(regex, url_string)
  return link


def update_news_count(a):
  url = f"https://www.hchs.hc.edu.tw/ischool/widget/site_news/update_news_clicks.php?newsId={a}"
  try:
    # 讀取代理伺服器列表
    proxy_url = "https://gimmeproxy.com/api/getProxy?supportsHttps=true&maxCheckPeriod=10000&protocol=http"
    response = requests.get(proxy_url)
    response_json = response.json()
    if response_json == {"error": "no more proxies left"}:
      print(response_json)
      return 'error'
    proxy = f"{response.json()['ip']}:{response.json()['port']}"
    proxies = {"http": proxy}
    response = requests.get(url, timeout=7, proxies=proxies)
    response.raise_for_status()

  except requests.exceptions.RequestException as e:
    print("error:", e)
    return 'error'



def detect_and_resolve_duplicates():
  with open('news.json', 'r', encoding='utf-8') as news_file:
    news = json.load(news_file)
  value_counts = {}
  resolved_data = {}

  for key, value in news.items():
      if value != "None":
          if value in value_counts:
              value_counts[value] += 1
              new_value = f"{value}{value_counts[value]}"
              resolved_data[key] = new_value
          else:
              value_counts[value] = 1
              resolved_data[key] = value
      else:
          resolved_data[key] = value
  resolved_data = dict(sorted(news.items()))
  with open('news.json', 'w', encoding='utf-8') as file:
    json.dump(resolved_data, file, indent=4)
    
  return