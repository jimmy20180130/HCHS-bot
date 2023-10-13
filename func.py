import requests
from urllib.parse import unquote
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import discord

with open('settings.json', 'r', encoding='utf-8') as settings_file:
  setting = json.load(settings_file)
  
SHORT_URL_KEY = setting['key']
URL_ROOT = setting['url_root']

unichr = chr

def short_repl_it_url(url, key):
  url = is_string_an_url(url)
  if url is None or url == '':
    return 'error'
  url = f'{URL_ROOT}shorturl?key={key}&url={url}'
  response = requests.get(url).text
  return response

def shorts_url(url, filename, image=None):
  if image is None:
    # shrtco_de_url = f'`{filename}` | {shrtco_de(url)}'
    shrtco_de_url = f'`{filename}` | {url}'
  elif image == 'image':
    # shrtco_de_url = shrtco_de(url)
    shrtco_de_url = short_repl_it_url(url, SHORT_URL_KEY)
  if not shrtco_de_url.endswith('error'):
    return shrtco_de_url
  else:
    print('無法連上api')
    return f'`{filename}` | [連結點我]({url})'

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


async def update_news_count(a):
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
  resolved_data = {
      str(k): v
      for k, v in sorted(
          news.items(), key=lambda item: int(item[0]), reverse=True)
  }

  with open('news.json', 'w') as file:
    json.dump(resolved_data, file, indent=4)

  return

async def get_anc(news_id):
  try:
    with open('news.json', 'r', encoding='utf-8') as news_file:
        news = json.load(news_file)

    # find all value
    for key, value in news.items():
      if len(value) == 100 and value.startswith(news_id):
        news_id = key
      elif len(value) < 100 and value == news_id:
        news_id = key

    url = f"https://www.hchs.hc.edu.tw/ischool/public/news_view/show.php?nid={news_id}"

    # GET request
    response = requests.get(url)
    html = response.text

    # bs4 html
    soup = BeautifulSoup(html, 'lxml')

    # find js
    js_code = soup.find_all('script', type='text/javascript')

    try:
      # regex get value
      attached_file_data = re.search(
          r'var g_attached_file_json_data = \'(.*?)\'', str(js_code)).group(1)
      news_unique_id = re.search(r'var g_news_unique_id = "(.*?)"',
                                  str(js_code)).group(1)
      resource_folder = re.search(r'var g_resource_folder = "(.*?)"',
                                  str(js_code)).group(1)
      attached_file_json_data = json.loads(attached_file_data)
    except:
      raise ValueError('公告ID錯誤: 找不到該ID')

    attachments = []
    for file_data in attached_file_json_data:
      file_name = unquote_unicode(file_data[2])
      if type(file_name) == list:
        file_name = file_name[0]
      file_link = f'{URL_ROOT}?id={news_id}&news_unique_id={news_unique_id}&res_folder={resource_folder}&res_name={file_name}'
      shorted_url = shorts_url(short_repl_it_url(file_link, SHORT_URL_KEY),
                                file_name, None)
      attachments.append(str(shorted_url))
      time.sleep(0.2)

    # get title
    title_element = soup.find('h4')
    title = title_element.text.strip()

    # get info
    info_unit = soup.find(id='info_unit').text.strip()
    info_person = soup.find(id='info_person').text.strip()
    info_time = soup.find(id='info_time').text.strip()

    def html_to_text(content):
      try:
        table = content.find('table').find('tbody')
        if table:
          rows = table.find_all('tr')
          text_list = []
          for row in rows:
            cells = row.find_all('td')
            row_text = '\t'.join([cell.get_text(strip=True) for cell in cells])
            text_list.append(row_text)

          return '\n'.join(text_list)
      except:
        paragraphs = content.find_all('p')
        text = '\n'.join([
            p.get_text(strip=True) for p in paragraphs[1:]
            if p.get_text(strip=True)
        ])
        if text == "\n" or text is None or text == "":
          divs = content.find_all('div')
          div_text = '\n'.join([
              div.get_text(strip=True) for div in divs[1:]
              if div.get_text(strip=True)
          ])
          return div_text
        return text

    content = soup.find('div', id='content')
    formatted_text = html_to_text(content)

    # regex find all links(without unicode)
    pattern = r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])(?![\/u4e00\-\/u9fa5])'
    compiled_pattern = re.compile(pattern, re.MULTILINE | re.ASCII)
    links = compiled_pattern.findall(formatted_text)

    # format links and add a space after it
    formatted_links = [
        '{}://{}{} '.format(link[0], link[1], link[2]) for link in links
    ]

    # put formatted links back to formatted_text
    for link in formatted_links:
      formatted_text = formatted_text.replace(link.strip(), link)

    # get all pic's link
    image_links = []
    img_tags = soup.find_all('img')
    for img_tag in img_tags:
      if 'src' in img_tag.attrs:
        if not '/ischool/resources/WID' in img_tag['src']:
          image_links.append(f"{img_tag['src']}+")
        else:
          image_links.append(img_tag['src'])

    embed = discord.Embed(title="爬蟲結果",
                          url=url,
                          description=f'新聞ID: {news_id}',
                          colour=0x00b0f4,
                          timestamp=datetime.now())
    embed.add_field(name="標題", value=title, inline=False)
    embed.add_field(name="單位", value=info_unit, inline=False)
    embed.add_field(name="張貼人", value=info_person, inline=False)
    embed.add_field(name="張貼日期", value=info_time, inline=False)
    if formatted_text != '' and formatted_text != None and formatted_text != "\n":
      embed.add_field(name="內容", value=formatted_text[:1024], inline=False)
    else:
      embed.add_field(name='內容', value='無', inline=False)
    # attachments
    if attachments:
      attachments_formatted = "\n".join(attachment
                                        for attachment in attachments)
      embed.add_field(name="附件檔案", value=attachments_formatted, inline=False)
    else:
      embed.add_field(name="附件檔案", value="無", inline=False)

    # pic links
    if image_links:
      image_links_formatted = "\n".join([
          f"`圖片{id}` | {shorts_url(f'{URL_ROOT}images?id={news_id}&name={image_filename}', image_filename, 'image')}"
          if not image_filename.endswith('+')
          else f"`圖片{id}` | {shorts_url(image_filename.rstrip('+'), '', 'image')}"
          for id, image_filename in enumerate(image_links, start=1)
      ])
      embed.add_field(name="圖片", value=image_links_formatted, inline=False)
    else:
      embed.add_field(name="圖片", value="無", inline=False)

    embed.set_footer(
        text="黑色麻中",
        icon_url=
        "https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp"
    )
    return embed
  except Exception as e:
    return f'error{e}'