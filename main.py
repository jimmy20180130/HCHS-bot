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
import tracemalloc
from func import unquote_unicode, is_string_an_url, update_news_count, detect_and_resolve_duplicates
from url_shortener import shrtco_de, shorts_url, short_88nb_cc, surl_cc, urlcc_cc, short_repl_it_url

tracemalloc.start()
intents = discord.Intents().all()
bot = discord.Bot(intents=intents)
TOKEN = os.environ['bot_token']
SHORT_URL_KEY = os.environ['key']


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
      result_list.append(value[:100])

  return result_list


@bot.command(name="縮網址", description="機器人的附加功能")
# 添加命令冷卻，限制該指令的觸發頻率
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
@option('服務',
        description='想使用的縮網址服務',
        choices=["surl.cc", "88nb.cc", "urlcc.cc", "shrtco.de", "機器人內建"])
@option('網址', description='想縮短的網址')
@option('檔案名稱', description='想使用的檔案名稱(only surl.cc)')
async def short_url(ctx, 服務, 網址, 檔案名稱=None):

  async def shorting_url():
    await ctx.defer()
    if is_string_an_url(網址) is not False:
      if 服務 == 'surl.cc':
        if 檔案名稱 is not None:
          shorted_url = surl_cc(網址, 檔案名稱)
        else:
          shorted_url = surl_cc(網址)
        if shorted_url == 'error':
          await ctx.respond('無法連上api')
        else:
          print(shorted_url)
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
        shorted_url = short_repl_it_url(網址, SHORT_URL_KEY)
        if shorted_url == 'Invalid key' or shorted_url == 'Invalid URL':
          await ctx.respond('無法連上api')
        else:
          await ctx.respond(shorted_url)
    else:
      await ctx.respond('無效的網址')

  await shorting_url()


@short_url.error
async def short_url_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    # 冷卻時間還未到達，顯示剩餘時間
    remaining_time = round(error.retry_after, 2)
    await ctx.respond(f"您目前的狀態為冷卻中，剩餘 {remaining_time} 秒後解除冷卻。")
  elif isinstance(error, commands.MaxConcurrencyReached):
    await ctx.respond("目前因多人同時使用此功能，請稍後再試")


@bot.command(name="關於機器人", description="黑色麻中")
async def about_me(ctx):
  embed = discord.Embed(title="關於我", colour=0x00b0f4, timestamp=datetime.now())
  embed.add_field(name=f"我的名字", value='黑色麻中ㄐㄐ人', inline=False)
  embed.add_field(name=f"我的作者", value='<@971730686685880322>', inline=False)
  embed.add_field(name=f"版本", value='2.0', inline=False)
  embed.add_field(
      name=f"神奇的資訊",
      value=
      '||這||||個||||資||||訊||||比||||神||||奇||||的||||海||||螺||||還||||神||||奇||||所||||以||||你||||點||||到||||這||||裡||||幹||||嘛||||?||',
      inline=False)
  embed.add_field(name=f"如何取得免費Nitro(可能已失效)",
                  value='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                  inline=False)
  embed.set_footer(
      text="黑色麻中",
      icon_url=
      "https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp"
  )
  await ctx.respond(embed=embed)


# 添加命令冷卻，限制該指令的觸發頻率
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
@bot.command(name="新增公告點閱數", description="這是一個神奇的功能")
@option('公告id',
        description='你要新增點閱數的公告',
        autocomplete=discord.utils.basic_autocomplete(get_id))
async def add_news_clicks(ctx, 公告id, 點閱數: Option(int, '欲新增的點閱數')):

  async def process_clicks():
    await ctx.defer()
    try:
      embed = discord.Embed(title="發生錯誤",
                            colour=0x00b0f4,
                            timestamp=datetime.now())
      embed.set_footer(
          text="黑色麻中",
          icon_url=
          "https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp"
      )
      if 點閱數 > 10:
        embed.add_field(name=f"原因",
                        value='為了不要讓<@971730686685880322>被抓去約談，所以超過十次請求須付費解鎖',
                        inline=False)
        embed.add_field(name=f"付費管道",
                        value='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                        inline=False)
        await ctx.respond(embed=embed)

      elif 點閱數 <= 0:
        embed.add_field(name=f"原因", value='點閱數<=0', inline=False)
        await ctx.respond(embed=embed)

      else:
        with open('news.json', 'r', encoding='utf-8') as news_data:
          news = json.load(news_data)
        news_id = [
            key for key, value in news.items() if value.startswith(公告id)
        ]
        loop_times = 點閱數
        message = await ctx.respond(f'預計至少{7.5 * 點閱數}秒後完成\n已新增0次點閱數')

        now_times = 0
        while now_times < loop_times:
          if await update_news_count(str(news_id[0])) == 'error':
            url = f"https://www.hchs.hc.edu.tw/ischool/widget/site_news/update_news_clicks.php?newsId={news_id[0]}"
            response = requests.get(url, timeout=20)
            response.raise_for_status()
          now_times += 1
          print(f'已新增{now_times}次點閱數')
          await message.edit(f'預計至少{7.5 * 點閱數}秒後完成\n已新增{now_times}次點閱數')
          await asyncio.sleep(0.5)
        embed = discord.Embed(title="已新增公告點閱數",
                              colour=0x00b0f4,
                              timestamp=datetime.now())
        embed.add_field(name="點閱數", value=點閱數, inline=False)
        embed.add_field(
            name="公告標題",
            value=
            f"在[這個網頁](https://www.hchs.hc.edu.tw/ischool/widget/site_news/main2.php?uid=WID_0_2_0516b5aba93b58b0547367faafb2f1dbe2ebba4c&maximize=1&allbtn=0)尋找**{公告id}**",
            inline=False)
        embed.set_footer(
            text="黑色麻中",
            icon_url=
            "https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp"
        )
        await message.reply(embed=embed)
    except Exception as e:
      print(e)
      await ctx.respond(f'```{e}```')

  await process_clicks()


@add_news_clicks.error
async def add_news_clicks_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    # 冷卻時間還未到達，顯示剩餘時間
    remaining_time = round(error.retry_after, 2)
    await ctx.respond(f"您目前的狀態為冷卻中，剩餘 {remaining_time} 秒後解除冷卻。")
  elif isinstance(error, commands.MaxConcurrencyReached):
    await ctx.respond("目前因多人同時使用此功能，請稍後再試")


@bot.command(name="設定新公告發送頻道", description="設定新公告發送頻道")
@commands.has_permissions(administrator=True)
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
@commands.has_permissions(administrator=True)
async def remove_channel(ctx, 公告頻道: Option(discord.TextChannel,
                                           '你要公告定期發送的頻道')):
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
      if len(value) == 100 and value.startswith(公告標題):
        news_id = key
      elif len(value) < 100 and value == 公告標題:
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
          f"`圖片{id}` | {shorts_url(short_repl_it_url(f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/images?id={news_id}&name={image_filename}', SHORT_URL_KEY), image_filename, 'image')}"
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
    await message.edit(content="", embed=embed)
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

    await message.edit(content="", embed=embed)


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
    message = await ctx.respond('資料處理中，請稍後')
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
      shorted_url = shorts_url(short_repl_it_url(file_link, SHORT_URL_KEY),
                               file_name, None)
      attachments.append(str(shorted_url))
      time.sleep(0.2)

    # get title
    title_element = soup.find('h4')
    title = title_element.text.strip()

    # getr info
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
                          url=url,
                          description=f'新聞ID: {公告id}',
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

    # image links
    if image_links:
      image_links_formatted = "\n".join([
          f"`圖片{id}` | {shorts_url(short_repl_it_url(f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/images?id={公告id}&name={image_filename}', SHORT_URL_KEY), image_filename, 'image')}"
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
    await message.edit(content="", embed=embed)
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

    await message.edit(content="", embed=embed)


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
      if value == 'None' and int(key) > int(last_non_none_item) and int(
          key) < int(last_non_none_item) + 10:
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
            shorted_url = shorts_url(
                short_repl_it_url(file_link, SHORT_URL_KEY), file_name, None)
            attachments.append(str(shorted_url))
            time.sleep(0.2)

          # get title
          title_element = soup.find('h4')
          title = title_element.text.strip()
          news[key] = title

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
                  row_text = '\t'.join(
                      [cell.get_text(strip=True) for cell in cells])
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
                                url=url,
                                description=f'新聞ID: {key}',
                                colour=0x00b0f4,
                                timestamp=datetime.now())
          embed.add_field(name="標題", value=title, inline=False)
          embed.add_field(name="單位", value=info_unit, inline=False)
          embed.add_field(name="張貼人", value=info_person, inline=False)
          embed.add_field(name="張貼日期", value=info_time, inline=False)
          if formatted_text != '' and formatted_text != None and formatted_text != "\n":
            embed.add_field(name="內容",
                            value=formatted_text[:1024],
                            inline=False)
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
                f"`圖片{id}` | {shorts_url(short_repl_it_url(f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/images?id={key}&name={image_filename}', SHORT_URL_KEY), image_filename, 'image')}"
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

    detect_and_resolve_duplicates()

    await asyncio.sleep(3600)


if __name__ == '__main__':
  app.keep_alive()
  bot.run(TOKEN)
