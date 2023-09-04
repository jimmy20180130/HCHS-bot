import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import unquote
import app
import discord
from discord import option
from datetime import datetime
import asyncio
import random
import time
import hashlib
import xml.etree.ElementTree as ET
import os

intents = discord.Intents().all()
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'機器人已上線({bot.user})')
    await start_timer()

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
            if (
                not r[-1] and
                u'\uDC00' <= ch <= u'\uDFFF' and
                u'\uD800' <= r[-2] <= u'\uDBFF'
            ):
                # UTF-16 surrogate pair, replace with single non-BMP codepoint
                r[-2] = (r[-2] + ch).encode(
                    'utf-16', 'surrogatepass').decode('utf-16')
            else:
                append(ch)
            append(part[4:])
        except ValueError:
            append(u'%u')
            append(part)
    return u''.join(r)

def short_url(url, filename, image):
    def shrtco_de(url, filename):
        shortener_url = f'https://api.shrtco.de/v2/shorten?url={url}'
        shorted_url = requests.get(shortener_url)
        if shorted_url.status_code == 201:
            result = shorted_url.json()['result']['full_short_link']
            return result
        else:
            return 'error'

    if image == None:
        shrtco_de_url = f'`{filename}` | {shrtco_de(url, filename)}'
    elif image == 'image':
        shrtco_de_url = shrtco_de(url, filename)
    
    if not shrtco_de_url.endswith('error'):
        return shrtco_de_url
    else:
        print('無法連上api')
        return f'`{filename}` | [連結點我]({url})'
    
def short_repl_it_url(url, key):
    url = f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/shorturl?key={key}&url={url}'
    response = requests.get(url).text
    return response

async def get_id(ctx: discord.AutocompleteContext):
    with open('news.json', 'r', encoding='utf-8') as news_file:
        news = json.load(news_file)

    result_list = []
    # find all value
    for key, value in news.items():
        if value != 'None':
            result_list.append(value)
    
    return result_list

@bot.command(name="設定新公告發送頻道", description="設定新公告發送頻道")
async def set_channel(ctx, channel_id):
    try:
        with open('settings.json', 'r', encoding='utf-8') as settings:
            setting = json.load(settings)

        # is digit and not in channel_id list
        if channel_id.isdigit() and channel_id not in setting['channel_id']:
            setting['channel_id'].append(channel_id)
        elif not channel_id.isdigit():
            raise ValueError('請輸入數字')
        elif channel_id in setting['channel_id']:
            raise ValueError('重複的ID')

        with open('settings.json', 'w', encoding='utf-8') as settings:
            json.dump(setting, settings, ensure_ascii=False, indent=4)

        await ctx.respond(f'已將{channel_id}設為您的新聞公告頻道')
    except Exception as e:
        embed = discord.Embed(title="發生了錯誤", description=f'```{e}```', colour=0x00b0f4, timestamp=datetime.now())
        embed.set_footer(text="黑色麻中", icon_url="https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp")

        await ctx.respond(embed=embed)

@bot.command(name='尋找公告', description="取得指定公告標題的資訊")
@option('公告標題', description='你要查詢的標題', autocomplete=discord.utils.basic_autocomplete(get_id))
async def search(ctx, 公告標題):
    await ctx.defer()
    try:
        await ctx.respond('資料處理中，請稍後')
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
            attached_file_data = re.search(r'var g_attached_file_json_data = \'(.*?)\'', str(js_code)).group(1)
            news_unique_id = re.search(r'var g_news_unique_id = "(.*?)"', str(js_code)).group(1)
            resource_folder = re.search(r'var g_resource_folder = "(.*?)"', str(js_code)).group(1)
            attached_file_json_data = json.loads(attached_file_data)
        except:
            raise ValueError('公告ID錯誤: 找不到該ID')

        attachments = []
        for file_data in attached_file_json_data:
            file_name = unquote_unicode(file_data[2])
            if type(file_name) == list:
                file_name = file_name[0]
            file_link = f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/?id={news_id}&news_unique_id={news_unique_id}&res_folder={resource_folder}&res_name={file_name}'
            shorted_repl_it_url = short_repl_it_url(file_link, os.getenv("key"))
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
        
        # get content
        content_node = soup.find('div', id='content')  
        
        # format content
        formatted_text = ""
        previous_tag_name = None

        for tag in content_node.find_all():
            tag_name = tag.name

            if tag_name == 'p':
                if previous_tag_name == 'p':
                    formatted_text += '\n'
                formatted_text += tag.get_text(strip=True) + '\n'
            elif tag_name == 'div':
                if previous_tag_name == 'p':
                    formatted_text += '\n'
                formatted_text += tag.get_text(strip=True) + '\n'
            
            previous_tag_name = tag_name

        # remove spaces
        formatted_text = formatted_text.strip()
        formatted_text = re.sub(r'\s', '', formatted_text)

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
            image_links_formatted = "\n".join([f"`圖片{id}` | {short_url(short_repl_it_url(f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/images?id={news_id}&name={image_filename}', 'jimmyishandsome'), image_filename, 'image')}" for id, image_filename in enumerate(image_links, start=1)])
            embed.add_field(name="圖片", value=image_links_formatted, inline=False)
        else:
            embed.add_field(name="圖片", value="無", inline=False)

        embed.set_footer(text="黑色麻中", icon_url="https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp")
        await ctx.edit(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="發生了錯誤", description=f'```{e}```', colour=0x00b0f4, timestamp=datetime.now())
        embed.set_footer(text="黑色麻中", icon_url="https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp")

        await ctx.edit(embed=embed)

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
@option('公告id', description='你要查詢的公告ID', autocomplete=discord.utils.basic_autocomplete(get_id2))
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
            attached_file_data = re.search(r'var g_attached_file_json_data = \'(.*?)\'', str(js_code)).group(1)
            news_unique_id = re.search(r'var g_news_unique_id = "(.*?)"', str(js_code)).group(1)
            resource_folder = re.search(r'var g_resource_folder = "(.*?)"', str(js_code)).group(1)
            attached_file_json_data = json.loads(attached_file_data)
        except:
            raise ValueError('公告ID錯誤: 找不到該ID')

        attachments = []
        for file_data in attached_file_json_data:
            file_name = unquote_unicode(file_data[2])
            if type(file_name) == list:
                file_name = file_name[0]
            file_link = f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/?id={公告id}&news_unique_id={news_unique_id}&res_folder={resource_folder}&res_name={file_name}'
            shorted_repl_it_url = short_repl_it_url(file_link, os.getenv("key"))
            shorted_url = short_url(shorted_repl_it_url, file_name, None)
            attachments.append(shorted_url)
            
        # get title
        title_element = soup.find('h4')
        title = title_element.text.strip()

        # getr info
        info_unit = soup.find(id='info_unit').text.strip()
        info_person = soup.find(id='info_person').text.strip()
        info_time = soup.find(id='info_time').text.strip()
        
        # get content
        content_node = soup.find('div', id='content')  
        
        # format content
        formatted_text = ""
        previous_tag_name = None

        for tag in content_node.find_all():
            tag_name = tag.name

            if tag_name == 'p':
                if previous_tag_name == 'p':
                    formatted_text += '\n'
                formatted_text += tag.get_text(strip=True) + '\n'
            elif tag_name == 'div':
                if previous_tag_name == 'p':
                    formatted_text += '\n'
                formatted_text += tag.get_text(strip=True) + '\n'
            
            previous_tag_name = tag_name

        # remove spaces
        formatted_text = formatted_text.strip()
        formatted_text = re.sub(r'\s', '', formatted_text)

        # regex find all links
        pattern = r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])(?![\/u4e00\-\/u9fa5])'
        compiled_pattern = re.compile(pattern, re.MULTILINE | re.ASCII)
        links = compiled_pattern.findall(formatted_text)

        # format links
        formatted_links = ['{}://{}{} '.format(link[0], link[1], link[2]) for link in links]

        # replace
        for link in formatted_links:
            formatted_text = formatted_text.replace(link.strip(), link)

        # get all pic's link
        image_links = []
        img_tags = soup.find_all('img')
        for img_tag in img_tags:
            if 'src' in img_tag.attrs:
                image_links.append(img_tag['src'])

        embed = discord.Embed(title="爬蟲結果", description=f'新聞ID: {公告id}', colour=0x00b0f4, timestamp=datetime.now())
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

        # image links
        if image_links:
            image_links_formatted = "\n".join([f"`圖片{id}` | {short_url(short_repl_it_url(f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/images?id={公告id}&name={image_filename}', os.getenv('key')), image_filename, 'image')}" for id, image_filename in enumerate(image_links, start=1)])
            embed.add_field(name="圖片", value=image_links_formatted, inline=False)
        else:
            embed.add_field(name="圖片", value="無", inline=False)

        embed.set_footer(text="黑色麻中", icon_url="https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp")
        await ctx.respond(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="發生了錯誤", description=f'```{e}```', colour=0x00b0f4, timestamp=datetime.now())
        embed.set_footer(text="黑色麻中", icon_url="https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp")

        await ctx.edit(embed=embed)

async def start_timer():
    while True:
        with open('news.json', 'r', encoding='utf-8') as news_file:
            news = json.load(news_file)

        for key, value in news.items():
            if value == 'None' and int(key) > 6145 and int(key) < 6200:
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
                        attached_file_data = re.search(r'var g_attached_file_json_data = \'(.*?)\'', str(js_code)).group(1)
                        news_unique_id = re.search(r'var g_news_unique_id = "(.*?)"', str(js_code)).group(1)
                        resource_folder = re.search(r'var g_resource_folder = "(.*?)"', str(js_code)).group(1)
                        attached_file_json_data = json.loads(attached_file_data)
                    except:
                        raise ValueError('公告ID錯誤: 找不到該ID')

                    attachments = []
                    for file_data in attached_file_json_data:
                        file_name = unquote_unicode(file_data[2])
                        if type(file_name) == list:
                            file_name = file_name[0]
                        file_link = f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/?id={key}&news_unique_id={news_unique_id}&res_folder={resource_folder}&res_name={file_name}'
                        shorted_repl_it_url = short_repl_it_url(file_link, 'jimmyishandsome')
                        shorted_url = short_url(shorted_repl_it_url, file_name, None)
                        attachments.append(shorted_url)
                        
                    # get title
                    title_element = soup.find('h4')
                    title = title_element.text.strip()
                    news[key] = title

                    # getr info
                    info_unit = soup.find(id='info_unit').text.strip()
                    info_person = soup.find(id='info_person').text.strip()
                    info_time = soup.find(id='info_time').text.strip()
                    
                    # get content
                    content_node = soup.find('div', id='content')  
                    
                    # format content
                    formatted_text = ""
                    previous_tag_name = None

                    for tag in content_node.find_all():
                        tag_name = tag.name

                        if tag_name == 'p':
                            if previous_tag_name == 'p':
                                formatted_text += '\n'
                            formatted_text += tag.get_text(strip=True) + '\n'
                        elif tag_name == 'div':
                            if previous_tag_name == 'p':
                                formatted_text += '\n'
                            formatted_text += tag.get_text(strip=True) + '\n'
                        
                        previous_tag_name = tag_name

                    # remove spaces
                    formatted_text = formatted_text.strip()
                    formatted_text = re.sub(r'\s', '', formatted_text)

                    # regex find all links
                    pattern = r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])(?![\/u4e00\-\/u9fa5])'
                    compiled_pattern = re.compile(pattern, re.MULTILINE | re.ASCII)
                    links = compiled_pattern.findall(formatted_text)

                    # format links
                    formatted_links = ['{}://{}{} '.format(link[0], link[1], link[2]) for link in links]

                    # replace
                    for link in formatted_links:
                        formatted_text = formatted_text.replace(link.strip(), link)

                    # get all pic's link
                    image_links = []
                    img_tags = soup.find_all('img')
                    for img_tag in img_tags:
                        if 'src' in img_tag.attrs:
                            image_links.append(img_tag['src'])

                    embed = discord.Embed(title="爬蟲結果", description=f'新聞ID: {key}', colour=0x00b0f4, timestamp=datetime.now())
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

                    # image links
                    if image_links:
                        image_links_formatted = "\n".join([f"`圖片{id}` | {short_url(short_repl_it_url(f'https://unacceptableconventionalfiles.jimmy20180130.repl.co/images?id={key}&name={image_filename}', os.getenv('key')), image_filename, 'image')}" for id, image_filename in enumerate(image_links, start=1)])
                        embed.add_field(name="圖片", value=image_links_formatted, inline=False)
                    else:
                        embed.add_field(name="圖片", value="無", inline=False)

                    embed.set_footer(text="黑色麻中", icon_url="https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp")
                    
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
                        embed = discord.Embed(title="發生了錯誤", description=f'```{e}```', colour=0x00b0f4, timestamp=datetime.now())
                        embed.set_footer(text="黑色麻中", icon_url="https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp")

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
    bot.run('')