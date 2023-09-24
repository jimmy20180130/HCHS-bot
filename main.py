import requests
from bs4 import BeautifulSoup
import re
import json
import app
from discord.ext import commands
import discord
from discord import Option, option
from datetime import datetime
import asyncio
import time
import os
from func import unquote_unicode, is_string_an_url, update_news_count
from url_shortener import shrtco_de, short_url, short_repl_it_url, short_88nb_cc, surl_cc, urlcc_cc

intents = discord.Intents().all()
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
  print(f'機器人已上線({bot.user})')
  await start_timer()

async def get_id(ctx: discord.AutocompleteContext):
  with open('news.json', 'r', encoding='utf-8') as news_file:
    news = json.load(news_file)

  result_list = []
  # find all value
  for key, value in news.items():
    if value != 'None':
      result_list.append(value)

  return result_list

@bot.command(name="縮網址", description="機器人的附加功能")
@option('服務', description='想使用的縮網址服務', choices=["surl.cc", "88nb.cc", "urlcc.cc", "shrtco.de", "機器人內建"])
@option('網址', description='想縮短的網址')
@option('檔案名稱', description='想使用的檔案名稱(only surl.cc)')
async def short_url(ctx, 服務, 網址, 檔案名稱=None):
  if is_string_an_url(網址) is not False:
    if 服務 == 'surl.cc':
      shorted_url = surl_cc(網址, 檔案名稱)
      if shorted_url == 'error':
        await ctx.respond('無法連上api')
      else:
        await ctx.respond(shorted_url)
        
    elif 服務 == '88nb.cc':
      shorted_url = short_88nb_cc(網址)
      if shorted_url == 'error':
        await ctx.respond('無法連上api')
      else:
        await ctx.respond(shorted_url)
        
    elif 服務 == 'urlcc.cc':
      shorted_url = urlcc_cc(網址)
      if shorted_url == 'error':
        await ctx.respond('無法連上api')
      else:
        await ctx.respond(shorted_url)
        
    elif 服務 == 'shrtco.de':
      shorted_url = shrtco_de(網址)
      if shorted_url == 'error':
        await ctx.respond('無法連上api')
      else:
        await ctx.respond(shorted_url)
        
    elif 服務 == '機器人內建':
      shorted_url = short_repl_it_url(網址, 'jimmyishandsome')
      if shorted_url == 'Invalid key' or shorted_url == 'Invalid URL':
        await ctx.respond('無法連上api')
      else:
        await ctx.respond(shorted_url)
  else:
    await ctx.respond('無效的網址')

@bot.command(name="關於機器人", description="黑色麻中")
async def about_me(ctx):
  embed = discord.Embed(title="關於我", colour=0x00b0f4, timestamp=datetime.now())
  embed.add_field(name=f"我的名字", value='', inline=False)
  embed.add_field(name=f"我的作者", value='<@971730686685880322>', inline=False)
  embed.add_field(name=f"版本", value='2.0', inline=False)
  embed.add_field(name=f"神奇的資訊", value='||這||||個||||資||||訊||||比||||神||||奇||||的||||海||||螺||||還||||神||||奇||||所||||以||||你||||點||||到||||這||||裡||||幹||||嘛||||?||', inline=False)
  embed.add_field(name=f"如何取得免費Nitro(可能已失效)", value='https://www.youtube.com/watch?v=dQw4w9WgXcQ', inline=False)
  embed.set_footer(
        text="黑色麻中",
        icon_url=
        "https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp"
    )
  await ctx.respond(embed=embed)

@bot.command(name="新增公告點閱數", description="這是一個神奇的功能")
@option('公告id', description='你要查詢的公告', autocomplete=discord.utils.basic_autocomplete(get_id))
async def add_news_clicks(ctx, 公告id, 點閱數: Option(int, '欲新增的點閱數')):
  await ctx.defer()
  embed = discord.Embed(title="發生錯誤", colour=0x00b0f4, timestamp=datetime.now())
  embed.set_footer(text="黑色麻中", icon_url= "https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp")
  if 點閱數 >= 10:
    embed.add_field(name=f"原因", value='為了不要讓<@971730686685880322>被抓去約談，所以超過十次請求須付費解鎖', inline=False)
    embed.add_field(name=f"付費管道", value='https://www.youtube.com/watch?v=dQw4w9WgXcQ', inline=False)
    await ctx.respond(embed=embed)
    
  elif 點閱數<=0:
    embed.add_field(name=f"原因", value='點閱數<=0', inline=False)
    await ctx.respond(embed=embed)
    
  elif not 點閱數.isdigit():
    embed.add_field(name=f"原因", value='點閱數不能為非數字', inline=False)
    await ctx.respond(embed=embed)
    
  else:  
    news_id = 公告id
    now_times = 0
    loop_times = input('loop_times')
    await ctx.respond(f'預計至少{0.5*點閱數}秒後完成')
    await ctx.send(f'已新增0次點閱數')
    while int(now_times) < int(loop_times):
        if update_news_count(news_id) == 'error':
            continue
        now_times += 1
        print(f'已新增{now_times}次點閱數')
        await ctx.edit(f'已新增{now_times}次點閱數')
        time.sleep(0.5)
    with open('news.json', 'r', encoding='utf-8') as news_data:
      news = json.load(news_data)
    await ctx.edit(f'點閱數已新增完成\n你可以至[這個網站](https://www.hchs.hc.edu.tw/ischool/widget/site_news/main2.php?uid=WID_0_2_0516b5aba93b58b0547367faafb2f1dbe2ebba4c&maximize=1&allbtn=0)中尋找標題*{news[str(news_id)]}*並查看結果')

@bot.command(name="設定新公告發送頻道", description="設定新公告發送頻道")
@commands.has_permissions(administrator = True)
async def set_channel(ctx, 公告頻道: Option(discord.TextChannel, '你要公告定期發送的頻道')):
  try:
    with open('settings.json', 'r', encoding='utf-8') as settings:
      setting = json.load(settings)

    # not in channel_id list
    if 公告頻道.id not in setting['channel_id']:
      setting['channel_id'].append(公告頻道.id)
    elif 公告頻道.id in setting['channel_id']:
      raise ValueError('重複的ID')

    with open('settings.json', 'w', encoding='utf-8') as settings:
      json.dump(setting, settings, ensure_ascii=False, indent=4)

    await ctx.respond(f'已將<#{公告頻道.id}>設為您的新聞公告頻道')
  except Exception as e:
    embed = discord.Embed(title="發生了錯誤",
                          description=f'```{e}```',
                          colour=0x00b0f4,
                          timestamp=datetime.now())
    embed.set_footer(
        text="黑色麻中",
        icon_url=
        "https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp"
    )

    await ctx.respond(embed=embed)
    
@bot.command(name="移除新公告發送頻道", description="移除新公告發送頻道")
@commands.has_permissions(administrator = True)
async def remove_channel(ctx, 公告頻道: Option(discord.TextChannel, '你要公告定期發送的頻道')):
  try:
    with open('settings.json', 'r', encoding='utf-8') as settings:
      setting = json.load(settings)

    # is digit and not in channel_id list
    if 公告頻道.id in setting['channel_id']:
      setting['channel_id'].remove(公告頻道.id)
    elif 公告頻道.id not in setting['channel_id']:
      raise ValueError('不存在的ID')

    with open('settings.json', 'w', encoding='utf-8') as settings:
      json.dump(setting, settings, ensure_ascii=False, indent=4)

    await ctx.respond(f'已將<#{公告頻道.id}>移除從新聞公告頻道列表移除')
  except Exception as e:
    embed = discord.Embed(title="發生了錯誤",
                          description=f'```{e}```',
                          colour=0x00b0f4,
                          timestamp=datetime.now())
    embed.set_footer(
        text="黑色麻中",
        icon_url=
        "https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp"
    )

    await ctx.respond(embed=embed)

@bot.command(name='尋找公告', description="取得指定公告標題的資訊")
@option('公告標題',
        description='你要查詢的標題',
        autocomplete=discord.utils.basic_autocomplete(get_id))
async def search(ctx, 公告標題):
  await ctx.defer()
  try:
    message = await ctx.respond('資料處理中，請稍後')
    with open('news.json', 'r', encoding='utf-8') as news_file:
      news = json.load(news_file)

    # find all value
    for key, value in news.items():
      if value == 公告標題:
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
      file_link = f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/?id={news_id}&news_unique_id={news_unique_id}&res_folder={resource_folder}&res_name={file_name}'
      shorted_repl_it_url = short_repl_it_url(file_link, os.environ['key'])
      shorted_url = short_url(shorted_repl_it_url, file_name, None)
      attachments.append(str(shorted_url))
      time.sleep(0.2)

    # get title
    title_element = soup.find('h4')
    title = title_element.text.strip()

    # get info
    info_unit = soup.find(id='info_unit').text.strip()
    info_person = soup.find(id='info_person').text.strip()
    info_time = soup.find(id='info_time').text.strip()
    
    def html_to_text_1(html):
      soup = BeautifulSoup(html, 'html.parser')
      paragraphs = soup.find_all('p')
      text = '\n'.join([p.get_text(strip=True) for p in paragraphs[1:] if p.get_text(strip=True)])
      return text
    
    def html_to_text_2(html):
      soup = BeautifulSoup(html, 'html.parser')
      paragraphs = soup.find('p').find('table').find('tbody').find_all('tr')
      text_list = []
      for tr in paragraphs:
        tr_text = ''
        for td in tr:
          if td.get_text(strip=True) != '':
            tr_text += f'{td.get_text(strip=True)}\t'
        text_list.append(tr_text[:-1])
      print(text_list)
      text = '\n'.join(text_list)
      return text
    
    content = soup.find('div', id='content')
    formatted_text = ''
    if content.find('p').find() == 'p':
      formatted_text = html_to_text_1(content)
    elif content.find('p').find() == 'table':
      formatted_text = html_to_text_2(content)        

    # regex find all links(without unicode)
    pattern = r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])(?![\/u4e00\-\/u9fa5])'
    compiled_pattern = re.compile(pattern, re.MULTILINE | re.ASCII)
    links = compiled_pattern.findall(formatted_text)

    # format links and add a space after it
    formatted_links = ['{}://{}{} '.format(link[0], link[1], link[2]) for link in links]

    # put formatted links back to formatted_text
    for link in formatted_links:
      formatted_text = formatted_text.replace(link.strip(), link)

    # get all pic's link
    image_links = []
    img_tags = soup.find_all('img')
    for img_tag in img_tags:
      if 'src' in img_tag.attrs:
        image_links.append(img_tag['src'])

    embed = discord.Embed(title="爬蟲結果", description=f'新聞ID: {news_id}', colour=0x00b0f4, timestamp=datetime.now())
    embed.add_field(name="標題", value=title, inline=False)
    embed.add_field(name="單位", value=info_unit, inline=False)
    embed.add_field(name="張貼人", value=info_person, inline=False)
    embed.add_field(name="張貼日期", value=info_time, inline=False)
    if formatted_text != '' or formatted_text != None:
      embed.add_field(name="內容", value=formatted_text, inline=False)
    else:
      embed.add_field(name='內容', value='無', inline=False)
    # attachments
    if attachments:
      attachments_formatted = "\n".join(attachment for attachment in attachments)
      embed.add_field(name="附件檔案", value=attachments_formatted, inline=False)
    else:
      embed.add_field(name="附件檔案", value="無", inline=False)

    # pic links
    if image_links:
      image_links_formatted = "\n".join([
          f"`圖片{id}` | {short_url(short_repl_it_url(f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/images?id={news_id}&name={image_filename}', os.environ['key']), image_filename, 'image')}"
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
    await message.edit(embed=embed)
  except Exception as e:
    embed = discord.Embed(title="發生了錯誤",
                          description=f'```{e}```',
                          colour=0x00b0f4,
                          timestamp=datetime.now())
    embed.set_footer(
        text="黑色麻中",
        icon_url=
        "https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp"
    )

    await message.edit(embed=embed)


async def get_id2(ctx: discord.AutocompleteContext):
  with open('news.json', 'r', encoding='utf-8') as news_file:
    news = json.load(news_file)

  result_list = []
  # get values
  for key, value in news.items():
    if value != 'None':
      result_list.append(key)

  return result_list


@bot.command(name='用id尋找公告', description="取得指定公告ID的資訊")
@option('公告id',
        description='你要查詢的公告ID',
        autocomplete=discord.utils.basic_autocomplete(get_id2))
async def search(ctx, 公告id):
  await ctx.defer()
  try:
    await ctx.respond('資料處理中，請稍後')
    url = f"https://www.hchs.hc.edu.tw/ischool/public/news_view/show.php?nid={公告id}"

    # GET request
    response = requests.get(url)
    html = response.text

    # bs4 html
    soup = BeautifulSoup(html, 'lxml')

    # get js
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
      file_link = f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/?id={公告id}&news_unique_id={news_unique_id}&res_folder={resource_folder}&res_name={file_name}'
      shorted_repl_it_url = short_repl_it_url(file_link, os.environ['key'])
      shorted_url = short_url(shorted_repl_it_url, file_name, None)
      attachments.append(shorted_url)

    # get title
    title_element = soup.find('h4')
    title = title_element.text.strip()

    # getr info
    info_unit = soup.find(id='info_unit').text.strip()
    info_person = soup.find(id='info_person').text.strip()
    info_time = soup.find(id='info_time').text.strip()

    def html_to_text_1(html):
      soup = BeautifulSoup(html, 'html.parser')
      paragraphs = soup.find_all('p')
      text = '\n'.join([p.get_text(strip=True) for p in paragraphs[1:] if p.get_text(strip=True)])
      return text
    
    def html_to_text_2(html):
      soup = BeautifulSoup(html, 'html.parser')
      paragraphs = soup.find('p').find('table').find('tbody').find_all('tr')
      text_list = []
      for tr in paragraphs:
        tr_text = ''
        for td in tr:
          if td.get_text(strip=True) != '':
            tr_text += f'{td.get_text(strip=True)}\t'
        text_list.append(tr_text[:-1])
      print(text_list)
      text = '\n'.join(text_list)
      return text
    
    content = soup.find('div', id='content')
    formatted_text = ''
    if content.find('p').find() == 'p':
      formatted_text = html_to_text_1(content)
    elif content.find('p').find() == 'table':
      formatted_text = html_to_text_2(content) 

    # regex find all links
    pattern = r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])(?![\/u4e00\-\/u9fa5])'
    compiled_pattern = re.compile(pattern, re.MULTILINE | re.ASCII)
    links = compiled_pattern.findall(formatted_text)

    # format links
    formatted_links = [
        '{}://{}{} '.format(link[0], link[1], link[2]) for link in links
    ]

    # replace
    for link in formatted_links:
      formatted_text = formatted_text.replace(link.strip(), link)

    # get all pic's link
    image_links = []
    img_tags = soup.find_all('img')
    for img_tag in img_tags:
      if 'src' in img_tag.attrs:
        image_links.append(img_tag['src'])

    embed = discord.Embed(title="爬蟲結果",
                          description=f'新聞ID: {公告id}',
                          colour=0x00b0f4,
                          timestamp=datetime.now())
    embed.add_field(name="標題", value=title, inline=False)
    embed.add_field(name="單位", value=info_unit, inline=False)
    embed.add_field(name="張貼人", value=info_person, inline=False)
    embed.add_field(name="張貼日期", value=info_time, inline=False)
    if formatted_text != '' or formatted_text != None:
      embed.add_field(name="內容", value=formatted_text, inline=False)
    else:
      embed.add_field(name='內容', value='無', inline=False)
    # attachments
    if attachments:
      attachments_formatted = "\n".join(attachment
                                        for attachment in attachments)
      embed.add_field(name="附件檔案", value=attachments_formatted, inline=False)
    else:
      embed.add_field(name="附件檔案", value="無", inline=False)

    # image links
    if image_links:
      image_links_formatted = "\n".join([
          f"`圖片{id}` | {short_url(short_repl_it_url(f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/images?id={公告id}&name={image_filename}', os.environ['key']), image_filename, 'image')}"
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
    await ctx.respond(embed=embed)
  except Exception as e:
    embed = discord.Embed(title="發生了錯誤",
                          description=f'```{e}```',
                          colour=0x00b0f4,
                          timestamp=datetime.now())
    embed.set_footer(
        text="黑色麻中",
        icon_url=
        "https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp"
    )

    await ctx.edit(embed=embed)


async def start_timer():
  while True:
    with open('news.json', 'r', encoding='utf-8') as news_file:
      news = json.load(news_file)

    # 将字符串键转换为整数，然后按照整数进行排序
    sorted_data = {int(key): value for key, value in news.items()}
    sorted_data = dict(sorted(sorted_data.items()))
    
    # 查找最后一个不为"None"的项
    last_non_none_item = None
    for key, value in sorted_data.items():
        if value != "None":
            last_non_none_item = key

    for key, value in news.items():
      if value == 'None' and int(key) > int(last_non_none_item) and int(key) < int(last_non_none_item)+10:
        try:
          url = f"https://www.hchs.hc.edu.tw/ischool/public/news_view/show.php?nid={key}"

          # GET request
          response = requests.get(url)
          html = response.text
          if str(html) == 'The news is not existed!':
            raise ValueError('news_not_exists')

          # bs4 html
          soup = BeautifulSoup(html, 'lxml')

          # get js
          js_code = soup.find_all('script', type='text/javascript')

          try:
            # regex get value
            attached_file_data = re.search(
                r'var g_attached_file_json_data = \'(.*?)\'',
                str(js_code)).group(1)
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
            file_link = f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/?id={key}&news_unique_id={news_unique_id}&res_folder={resource_folder}&res_name={file_name}'
            shorted_repl_it_url = short_repl_it_url(file_link,
                                                    os.environ['key'])
            shorted_url = short_url(shorted_repl_it_url, file_name, None)
            attachments.append(shorted_url)

          # get title
          title_element = soup.find('h4')
          title = title_element.text.strip()
          news[key] = title

          # get info
          info_unit = soup.find(id='info_unit').text.strip()
          info_person = soup.find(id='info_person').text.strip()
          info_time = soup.find(id='info_time').text.strip()

          def html_to_text_1(html):
            soup = BeautifulSoup(html, 'html.parser')
            paragraphs = soup.find_all('p')
            text = '\n'.join([p.get_text(strip=True) for p in paragraphs[1:] if p.get_text(strip=True)])
            return text
    
          def html_to_text_2(html):
            soup = BeautifulSoup(html, 'html.parser')
            paragraphs = soup.find('p').find('table').find('tbody').find_all('tr')
            text_list = []
            for tr in paragraphs:
              tr_text = ''
              for td in tr:
                if td.get_text(strip=True) != '':
                  tr_text += f'{td.get_text(strip=True)}\t'
              text_list.append(tr_text[:-1])
            print(text_list)
            text = '\n'.join(text_list)
            return text
          
          content = soup.find('div', id='content')
          formatted_text = ''
          if content.find('p').find() == 'p':
            formatted_text = html_to_text_1(content)
          elif content.find('p').find() == 'table':
            formatted_text = html_to_text_2(content) 

          # regex find all links
          pattern = r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])(?![\/u4e00\-\/u9fa5])'
          compiled_pattern = re.compile(pattern, re.MULTILINE | re.ASCII)
          links = compiled_pattern.findall(formatted_text)

          # format links
          formatted_links = [
              '{}://{}{} '.format(link[0], link[1], link[2]) for link in links
          ]

          # replace
          for link in formatted_links:
            formatted_text = formatted_text.replace(link.strip(), link)

          # get all pic's link
          image_links = []
          img_tags = soup.find_all('img')
          for img_tag in img_tags:
            if 'src' in img_tag.attrs:
              image_links.append(img_tag['src'])

          embed = discord.Embed(title="爬蟲結果",
                                description=f'新聞ID: {key}',
                                colour=0x00b0f4,
                                timestamp=datetime.now())
          embed.add_field(name="標題", value=title, inline=False)
          embed.add_field(name="單位", value=info_unit, inline=False)
          embed.add_field(name="張貼人", value=info_person, inline=False)
          embed.add_field(name="張貼日期", value=info_time, inline=False)
          if formatted_text != '' or formatted_text != None:
            embed.add_field(name="內容", value=formatted_text, inline=False)
          else:
            embed.add_field(name='內容', value='無', inline=False)
          # attachments
          if attachments:
            attachments_formatted = "\n".join(attachment
                                              for attachment in attachments)
            embed.add_field(name="附件檔案",
                            value=attachments_formatted,
                            inline=False)
          else:
            embed.add_field(name="附件檔案", value="無", inline=False)

          # image links
          if image_links:
            image_links_formatted = "\n".join([
                f"`圖片{id}` | {short_url(short_repl_it_url(f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/images?id={key}&name={image_filename}', os.environ['key']), image_filename, 'image')}"
                for id, image_filename in enumerate(image_links, start=1)
            ])
            embed.add_field(name="圖片",
                            value=image_links_formatted,
                            inline=False)
          else:
            embed.add_field(name="圖片", value="無", inline=False)

          embed.set_footer(
              text="黑色麻中",
              icon_url=
              "https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp"
          )

          with open('settings.json', 'r', encoding='utf-8') as settings:
            setting = json.load(settings)

          for channel_id in setting['channel_id']:
            try:
              channel = bot.get_channel(int(channel_id))
              await channel.send(embed=embed)
            except Exception as e:
              print(e)
              continue
        except Exception as e:
          if str(e) != 'news_not_exists':
            print(e)
            embed = discord.Embed(title="發生了錯誤",
                                  description=f'```{e}```',
                                  colour=0x00b0f4,
                                  timestamp=datetime.now())
            embed.set_footer(
                text="黑色麻中",
                icon_url=
                "https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp"
            )

            with open('settings.json', 'r', encoding='utf-8') as settings:
              setting = json.load(settings)

            print(setting['channel_id'])
            for channel_id in setting['channel_id']:
              try:
                channel = bot.get_channel(int(channel_id))
                await channel.send(embed=embed)
              except Exception as e:
                print(e)
                continue

    with open('news.json', 'w', encoding='utf-8') as news_file:
      json.dump(news, news_file, ensure_ascii=False, indent=4)

    await asyncio.sleep(3600)


if __name__ == '__main__':
  app.keep_alive()
  bot.run(os.environ['bot_token'])