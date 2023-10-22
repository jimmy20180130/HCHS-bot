import requests
import json
import app
from discord.ext import commands
import discord
from discord import Option, option
from discord.commands import SlashCommandGroup
from datetime import datetime
import asyncio
import tracemalloc
from func import is_string_an_url, update_news_count, detect_and_resolve_duplicates, get_anc
from url_shortener import short_88nb_cc, surl_cc, urlcc_cc, short_repl_it_url

tracemalloc.start()
intents = discord.Intents().all()
bot = discord.Bot(intents=intents)

with open('settings.json', 'r', encoding='utf-8') as settings_file:
  setting = json.load(settings_file)

TOKEN = setting['token']
SHORT_URL_KEY = setting['key']
URL_ROOT = setting['url_root']


@bot.event
async def on_ready():
  print(f'機器人已上線({bot.user})')
  await start_timer()

anc = SlashCommandGroup('公告', '關於公告的指令類別')
anc_find= anc.create_subgroup('尋找', '用id或標題尋找公告')
anc_notify= anc.create_subgroup('校網公告通知頻道', '機器人定期發送公告的頻道')


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
        choices=["surl.cc", "88nb.cc", "urlcc.cc", "機器人內建"])
@option('網址', description='想縮短的網址')
async def short_url(ctx, 服務, 網址):

  async def shorting_url():
    await ctx.defer()
    if is_string_an_url(網址) is not False:
      if 服務 == 'surl.cc':
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


@bot.command(name="關於機器人", description="黑色麻中ㄐㄐ人")
async def about_me(ctx):
  values='這個資訊比神奇的海螺還神奇所以你點到這裡幹嘛?'
  embed = discord.Embed(title="關於我", colour=0x00b0f4, timestamp=datetime.now())
  embed.add_field(name=f"我的名字", value='黑色麻中ㄐㄐ人', inline=False)
  embed.add_field(name=f"我的作者", value='<@971730686685880322>', inline=False)
  embed.add_field(name=f"版本", value='2.0', inline=False)
  embed.add_field(
      name=f"神奇的資訊",
      value=''.join([f'||{char}||' for char in values]),
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
@anc.command(name="新增點閱數", description="這是一個神奇的功能")
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
        await message.edit(content='', embed=embed)
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


@anc_notify.command(name="設定頻道", description="設定新公告發送頻道")
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


@anc_notify.command(name="移除頻道", description="移除新公告發送頻道")
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


@anc_find.command(name='標題', description="取得指定公告標題的資訊")
@option('公告標題',
        description='你要查詢的標題',
        autocomplete=discord.utils.basic_autocomplete(get_id))
async def search_title(ctx, 公告標題):
  await ctx.defer()
  message = await ctx.respond('資料處理中，請稍後')
  response = await get_anc(公告標題)
  if type(response) == discord.embeds.Embed:
    await message.edit(content="", embed=response)
  elif response.startswith('error'):
    embed = discord.Embed(title="發生了錯誤",
                          description=f'```{response[5:]}```',
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


@anc_find.command(name='id', description="取得指定公告ID的資訊")
@option('公告id',
        description='你要查詢的公告ID',
        autocomplete=discord.utils.basic_autocomplete(get_id2))
async def search(ctx, 公告id):
  await ctx.defer()
  message = await ctx.respond('資料處理中，請稍後')
  response = await get_anc(公告id)
  if type(response) == discord.embeds.Embed:
    await message.edit(content="", embed=response)
  elif response.startswith('error'):
    embed = discord.Embed(title="發生了錯誤",
                          description=f'```{response[5:]}```',
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
    with open('settings.json', 'r', encoding='utf-8') as settings:
      setting = json.load(settings)

    # 小到大排key
    sorted_data = {int(key): value for key, value in news.items()}
    sorted_data = dict(sorted(sorted_data.items()))

    # 最後一個不為None的項目
    last_non_none_item = None
    for key, value in sorted_data.items():
      if value != "None":
        last_non_none_item = key

    for key, value in news.items():
      if value == 'None' and int(key) > int(last_non_none_item) and int(
          key) < int(last_non_none_item) + 10:
        
        response = await get_anc(key, 'auto')
        if response != 'error公告ID錯誤: 找不到該ID' and type(response) != discord.embeds.Embed:
          print(0)
          print(response)
          embed = discord.Embed(title="發生了錯誤",
                                description=f'```{response}```',
                                colour=0x00b0f4,
                                timestamp=datetime.now())
          embed.set_footer(
              text="黑色麻中",
              icon_url=
              "https://cdn.discordapp.com/avatars/1146008422144290826/13051e7a68067c42c417f3aa04de2ffa.webp"
          )

          for channel_id in setting['channel_id']:
            try:
              channel = bot.get_channel(int(channel_id))
              await channel.send(embed=embed)
            except Exception as e:
              print(1)
              print(e)
              continue
        elif response == 'error公告ID錯誤: 找不到該ID':
          pass
        else:
          for channel_id in setting['channel_id']:
            try:
              channel = bot.get_channel(int(channel_id))
              await channel.send(embed=response)
            except Exception as e:
              print(2)
              print(e)
              continue

    detect_and_resolve_duplicates()

    await asyncio.sleep(3600)

bot.add_application_command(anc)

if __name__ == '__main__':
  app.keep_alive()
  bot.run(TOKEN)
