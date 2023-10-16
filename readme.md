# **黑色麻中機器人** ✨

✨一個會抓取新竹高中網頁公告的機器人 (還可以把點閱數弄到99999)✨

## 各種神奇連結
[![Invite](https://img.shields.io/badge/Invite-Bot-blue)](https://discord.com/api/oauth2/authorize?client_id=1146008422144290826&permissions=40667102838353&scope=bot%20applications.commands)
[![Discord Server](https://img.shields.io/badge/Discord%20Server-Join-brightgreen)](https://discord.gg/5UrGWXf3ba)
[![YouTube Channel](https://img.shields.io/badge/YouTube-Subscribe-red)](https://www.youtube.com/@JimmyXiaoXi)

- **邀請機器人** 👉 (https://discord.com/api/oauth2/authorize?client_id=1146008422144290826&permissions=40667102838353&scope=bot%20applications.commands)
- **加入Discord伺服器** 👉 (https://discord.gg/5UrGWXf3ba)
- **訂閱我👉** (https://www.youtube.com/@JimmyXiaoXi)

## 特色/功能
- ✅ 在 Discord 就可以輕鬆看到學校的公告
- ✅ 可自動發送最新公告至你指定的頻道
- ✅ 可以透過公告 ID 或是名稱來搜尋公告
- ✅ 公告整理詳細，格式和校網差不多
- ✅ 檔案附設以縮短的連結，可輕鬆的分享給別人
- ✅ 擺脫學校網站查看檔案的限制 ([請看此影片](https://www.google.com/))
- ✅ 機器人有免費縮網址服務，並提供五種選項
- ✅ 可以新增學校公告的點閱數

## 指令列表
- `/公告 尋找 <公告標題>`
- `/公告 尋找 <公告ID>`
- `/公告 校網公告通知頻道 設定頻道 (想要設定讓公告自動發送的頻道)`
- `/公告 校網公告通知頻道 移除頻道 (想從自動發送頻道列表中刪除的頻道)`
- `/公告 新增點閱數 <公告標題> <想新增的點閱數>`
- `/縮網址 (API選項) <網址>`
- `/關於機器人`

# **不想用我的機器人? 想自己架?**

## 需求
- Python 3.11 或更高之版本
- py-cord==2.4.1
- requests==2.31.0
- flask==2.3.2
- beautifulsoup4==4.12.2
- validators==0.22.0
- lxml

## 操作方式(在自己電腦上跑)
- 請參考影片或是底下內容
1. 點右上角的 Download 按鈕，把檔案下載到您的電腦上並解壓縮
2. 輸入以下指令或是在你存放檔案資料夾裡面點右鍵 -> 在終端機中開啟
   ```bash
   cd <你的檔案存放的資料夾名稱>
3. 輸入以下指令來安裝必要之套件
   ```bash
   pip install -r requirements.txt
4. 接著使用底下的指令來執行
   ```bash
   python main.py
## 操作方式(在repl.it上跑)
- [請看此影片](https://www.google.com)