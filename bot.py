import json
from khl import Message, Bot
from khl.card import CardMessage, Card, Module
import subprocess
import requests
import psutil
import re
import time

with open("config.json", "r", encoding="utf-8") as f:
    configstr = f.read().replace('\\', '!')
    configtmp = json.loads(configstr)
    config = {k: v.replace('!', '\\') for k, v in configtmp.items()}
firstloginlock=True
LOCK = False
playtime = 0
duration = 0
netease_phone = config["n_phone"]
netease_passwd = config["n_passwd"]
netease_cookie = config["n_cookie"]
qq_cookie = config["q_cookie"]
qq_id = config["q_id"]
qq_enable = config["qq_enable"]
bot = Bot(token=config["token"])
playlist = []
p=subprocess.Popen('ffmpeg')
deltatime=7
def kill():
    global p
    try:
        process = psutil.Process(p.pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()
    except Exception as e:
        print(e)

helpcm=[
  {
    "type": "card",
    "theme": "secondary",
    "size": "lg",
    "modules": [
      {
        "type": "header",
        "text": {
          "type": "plain-text",
          "content": "点歌机操作指南"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**1.  点歌   +    (平台)    +    歌名**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    将歌曲加到播放队列中\ntips:\n歌名中如果有英文引号等特殊字符，需要将歌名用英文引号括起来\n例如  **点歌 \"Rrhar'il\"**\n如果需要指定歌曲版本播放，可以在歌名后添加歌手\n例如  **点歌 勇敢勇敢-黄勇**\n现支持QQ音乐、网易云音乐、网易云音乐电台与B站，若不写平台则默认从网易云获取数据（QQ音乐需要单独安装api并在config.json中启用平台、网易云电台仅支持从节目id点播）\n例如  **点歌 qq heavensdoor**\n例如  **点歌 网易 勇敢勇敢-黄勇**\n例如  **点歌 b站 BV1qa411e7Fi**\n例如  **点歌 你看到的我**\n例如  **点歌 网易电台 2499131107**"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**2.  下一首**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    跳过当前正播放的歌曲，仅限**有特定角色的用户**使用"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**3.  歌单**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    展示播放队列内剩余的歌曲"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**4.  导入歌单       +       网易云歌单id**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    将网易云歌单中的歌曲导入到播放队列\n例如  **导入歌单 977171340**"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**5.  导入电台       +       网易云电台id**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    将网易电台中的歌曲导入到播放队列\n例如  **导入电台 972583481**"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "**6.  清空歌单**"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "kmarkdown",
          "content": "功能:    清空播放队列"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "context",
        "elements": [
          {
            "type": "plain-text",
            "content": "如有其他问题、bug或反馈建议，请私信开发人员：\nnick-haoran#0722      Gunale#2333\n特别鸣谢:        k1nbo#0001"
          }
        ]
      }
    ]
  }
]
def getCidAndTitle(bvid,p=1):
    global duration
    global deltatime
    url='https://api.bilibili.com/x/web-interface/view?bvid='+bvid
    data=requests.get(url).json()['data']
    title=data['title']
    cid=data['pages'][p-1]['cid']
    duration=data['pages'][p-1]['duration']+deltatime
    mid=str(data['owner']['mid'])
    name=data['owner']['name']
    pic=data['pic']
    print(cid,title,mid)
    return str(cid),title,mid,name,pic

def getInformation(bvid):
    bvid=bvid.replace("?p=", " ")
    item=[]
    if len(bvid) == 12:

        cid,title,mid,name,pic=getCidAndTitle(bvid[:12])
        item.append(bvid)
    else:

        cid,title,mid,name,pic=getCidAndTitle(bvid[:12],int(bvid[13:]))
        item.append(bvid[:12])
    item.append(cid)
    item.append(title)
    item.append(mid)
    item.append(name)
    item.append(pic)

    return item

def getAudio(item):
    baseUrl='http://api.bilibili.com/x/player/playurl?fnval=16&'
    bvid,cid,title,mid,name,pic=item[0],item[1],item[2],item[3],item[4],item[5]
    url=baseUrl+'bvid='+bvid+'&cid='+cid
    audioUrl=requests.get(url).json()['data']['dash']['audio'][0]['baseUrl']
    headers =  {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Range': 'bytes=0-',
        'Referer': 'https://api.bilibili.com/x/web-interface/view?bvid='+bvid,
        'Origin': 'https://www.bilibili.com',
        'Connection': 'keep-alive'
    }
    response=requests.get(url=audioUrl, headers=headers)
    open("tmp.mp3", "wb").write(response.content)
    return bvid,cid,title,mid,name,pic

@bot.command(name='导入歌单')
async def listen(msg: Message, linkid : str):
    global playlist
    url = "http://127.0.0.1:3000/playlist/track/all?id="+linkid

    songs = requests.get(url=url).json()["songs"]

    for song in songs:
        playlist.append({'name':song['name']+"-"+song['ar'][0]['name']+' '+str(song['id']),'userid':msg.author.id,'type':'网易','time':int(round(time.time() * 1000))+1000000000000})
    await msg.ctx.channel.send("导入完成")

@bot.command(name='导入电台')
async def listen(msg: Message, linkid : str):
    global playlist
    url = "http://127.0.0.1:3000/dj/program?rid="+linkid+"&limit=10000"

    programs = requests.get(url=url).json()["programs"]

    for program in programs:
        playlist.append({'name':program['mainSong']['name']+'-'+str(program['id']),'userid':msg.author.id,'type':'网易电台','time':int(round(time.time() * 1000))+1000000000000})
    await msg.ctx.channel.send("导入完成")

@bot.command(name='清空歌单')
async def listen(msg: Message):
    global playlist
    if len(playlist)>0:
        now=playlist[0]
        playlist=[]
        playlist.append(now)
    await msg.ctx.channel.send("清空完成")

@bot.command(name="下一首")
async def nextmusic(msg: Message):
    global playlist
    global playtime
    global LOCK
    global duration
    flag=True
    for role in msg.author.roles:
        print(role)
        if str(role) == config["skipper"]:
            flag=False
    if config["skipper"]=='0':
        flag=False
    if flag:
        await msg.ctx.channel.send("无权限")
        return None

    kill()
    if len(playlist)==0:
        await msg.ctx.channel.send("无下一首")
        LOCK=False
        return None
    playlist.pop(0)
    LOCK=False
    playtime=0
    duration=0
    await msg.ctx.channel.send("切换成功")


@bot.command(name="点歌")
async def addmusic(msg: Message,*args):
    global helpcm
    global qq_enable
    try:
        args=list(args)
        if msg.ctx.channel.id != config["channel"]:
            await msg.ctx.channel.send('请在指定频道中点歌')
            return
        global playlist
        typ='网易'
        song_name=''
        if args[0]=='qq' or args[0]=='网易' or args[0]=='b站'or args[0]=='网易电台':
            typ=args[0]
            args.pop(0)
            if typ=='qq' and qq_enable == '0':
                await msg.ctx.channel.send('未启用qq点歌')
                return None
        for st in args:
            song_name = song_name + st + " "
        playlist.append({'name':song_name,'userid':msg.author.id,'type':typ,'time':int(round(time.time() * 1000))})
        await msg.ctx.channel.send("已添加")
    except:
        await msg.ctx.channel.send(helpcm)


@bot.command(name="歌单")
async def prtlist(msg: Message):
    global playlist
    cm = CardMessage()
    c = Card()
    c.append(Module.Header('正在播放：'))
    if len(playlist) == 0:
        c.append(Module.Section('无'))
    i=0
    for item in playlist:
        if i==10:
            break
        c.append(Module.Section(item['name']))
        i+=1
    c.append(Module.Header('共有'+str(len(playlist))+'首歌'))
    cm.append(c)
    await msg.ctx.channel.send(cm)


@bot.command(name="帮助")
async def help(msg: Message):
    global helpcm
    await msg.ctx.channel.send(helpcm)


@bot.task.add_interval(seconds=deltatime)
async def update_played_time_and_change_music():
    global deltatime
    global playtime
    global playlist
    global LOCK
    global duration
    global p
    global netease_phone
    global netease_passwd
    global firstloginlock
    global neteasecookie
    if firstloginlock==True:
        print('login check')
        url='http://127.0.0.1:3000/login/status?timestamp='
        print(url)
        response=requests.get(url=url).json()
        print(response)
        try:
            response=response['data']['account']['status']
            if response==-10:
                url='http://127.0.0.1:3000/login/cellphone?phone='+netease_phone+'&password='+netease_passwd
                print(requests.get(url=url).json())
                print('网易云登陆成功')
        except:
            url='http://127.0.0.1:3000/login/cellphone?phone='+netease_phone+'&password='+netease_passwd
            print(requests.get(url=url).json())
            print('网易云登陆成功')
        print('网易已登录')
        url='http://127.0.0.1:3000/login/refresh'
        requests.get(url=url)
        print('刷新登录cookie')
        if qq_enable=="1":
            url='http://127.0.0.1:3300/user/setCookie'
            data={
                "data":qq_cookie
            }
            
            response=requests.post(url=url,json=data)
            print(response.text)
            url='http://127.0.0.1:3300/user/getCookie?id='+qq_id
            response=requests.get(url=url)
            print(response.text)
            print('QQ已登录')
        firstloginlock=False
    if LOCK:
        return
    else:
        LOCK = True
        if len(playlist) == 0:
            LOCK = False
            return None
        else:
            if playtime == 0:
                playlist.sort(key=lambda x: list(x.values())[3])
                song_name = playlist[0]['name']
                if song_name == "":
                    LOCK = False

                    return
                if playlist[0]['type']=='网易':
                    try:
                        headers={
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                                'Cache-Control': 'max-age=0',
                                'Connection': 'keep-alive',
                                'Cookie': netease_cookie,
                                'Host': '127.0.0.1:3000',
                                'Referer': 'https://music.163.com',
                                'If-None-Match': 'W/"722-3Oy0PoR7kMdKeuZyLO+S/tZ4B6I"',
                                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"',
                                'sec-ch-ua-mobile': '?0',
                                'sec-ch-ua-platform': "Windows",
                                'Sec-Fetch-Dest': 'document',
                                'Sec-Fetch-Mode': 'navigate',
                                'Sec-Fetch-Site': 'none',
                                'Sec-Fetch-User': '?1',
                                'Upgrade-Insecure-Requests': '1',
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33'
                            }
                        url="http://127.0.0.1:3000/cloudsearch?keywords="+song_name+"&limit=1"
                        response=requests.get(url=url,headers=headers).json()
                        musicid=str(response['result']['songs'][0]['id'])

                        url='http://127.0.0.1:3000/song/detail?ids='+musicid

                        response=requests.get(url=url,headers=headers).json()['songs'][0]
                        duration=int(response['dt']/1000)+5
                        song_name=response['name']
                        ban=re.compile('(惊雷)|(Lost Rivers)')
                        resu=ban.findall(song_name)
                        print(resu)
                        if len(resu)>0:
                            LOCK=False
                            playlist.pop(0)
                            await bot.send(
                                await bot.fetch_public_channel(
                                    config["channel"]
                                ),
                                '吃了吗，没吃吃我一拳',
                            )
                            duration=0
                            playtime=0
                            return None
                        song_url='https://music.163.com/#/song?id='+str(response['id'])
                        album_name=response['al']['name']
                        if album_name=='':
                            album_name='无专辑'
                        album_url='https://music.163.com/#/album?id='+str(response['al']['id'])
                        singer_name=response['ar'][0]['name']
                        singer_url='https://music.163.com/#/artist?id='+str(response['ar'][0]['id'])
                        pic_url=response['al']['picUrl']
                        getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['id'])+'&timestamp='+str(int(round(time.time() * 1000)))
                        
                        urlresponse=requests.get(url=getfile_url,headers=headers).json()['data'][0]['url']
                        print(urlresponse)
                        if urlresponse==None:
                            urlresponse=''
                        
                        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and (not urlresponse.endswith(".flac")):
                            getfile_url='http://127.0.0.1:3000/song/download/url?id='+str(response['id'])+'&timestamp='+str(int(round(time.time() * 1000)))
                            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data']['url']
                            print(urlresponse)
                        if urlresponse==None:
                            urlresponse=''

                        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and (not urlresponse.endswith(".flac")):
                            getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['id'])+'&br=320000&timestamp='+str(int(round(time.time() * 1000)))
                            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data'][0]['url']
                            print(urlresponse)
                        if urlresponse==None:
                            urlresponse=''

                        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and (not urlresponse.endswith(".flac")):
                            getfile_url='http://127.0.0.1:3000/song/download/url?id='+str(response['id'])+'&br=320000&timestamp='+str(int(round(time.time() * 1000)))
                            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data']['url']
                            print(urlresponse)
                        if urlresponse==None:
                            urlresponse=''

                        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and (not urlresponse.endswith(".flac")):
                            getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['id'])
                            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data'][0]['url']
                            print(urlresponse)
                        if urlresponse==None:
                            urlresponse=''

                        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and (not urlresponse.endswith(".flac")):
                            getfile_url='http://127.0.0.1:3000/song/download/url?id='+str(response['id'])
                            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data']['url']
                            print(urlresponse)
                        if urlresponse==None:
                            urlresponse=''

                        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and (not urlresponse.endswith(".flac")):
                            getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['id'])+'&br=320000'
                            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data'][0]['url']
                            print(urlresponse)
                        if urlresponse==None:
                            urlresponse=''

                        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and (not urlresponse.endswith(".flac")):
                            getfile_url='http://127.0.0.1:3000/song/download/url?id='+str(response['id'])+'&br=320000'
                            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data']['url']
                            print(urlresponse)
                        if urlresponse==None:
                            urlresponse=''
                        musicfile = requests.get(urlresponse)
                        if urlresponse.endswith("flac"):
                            open("tmp.flac", "wb").write(musicfile.content)
                            kill()
                            p = subprocess.Popen(
                                'ffmpeg -re -nostats -i "tmp.flac" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+config["port"],
                                shell=True
                            )
                        else:
                            open("tmp.mp3", "wb").write(musicfile.content)
                            kill()
                            p = subprocess.Popen(
                                'ffmpeg -re -nostats -i "tmp.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+config["port"],
                                shell=True
                            )

                        starttime=int(round(time.time() * 1000))
                        endtime=starttime+int(duration*1000)
                        playtime = 0

                        cm = [ { "type": "card", "theme": "secondary", "color": "#DD001B", "size": "lg", "modules": [ { "type": "header", "text": { "type": "plain-text", "content": "正在播放：" + song_name, }, }, { "type": "section", "text": { "type": "kmarkdown", "content":"(met)" +playlist[0]['userid']+"(met)", }, }, { "type": "context", "elements": [ { "type": "kmarkdown", "content": "歌手： [" + singer_name + "](" + singer_url + ")  —出自专辑 [" + album_name + "](" + album_url + ")", } ], }, { "type": "audio", "title": song_name, "src": urlresponse, "cover": pic_url, }, {"type": "countdown","mode": "second","startTime": starttime,"endTime": endtime},{"type": "divider"}, { "type": "context", "elements": [ { "type": "image", "src":  "https://img.kaiheila.cn/assets/2022-05/UmCnhm4mlt016016.png", }, { "type": "kmarkdown", "content": "网易云音乐  [在网页查看](" + song_url + ")", }, ], }, ], } ]
                        await bot.send(
                            await bot.fetch_public_channel(
                                config["channel"]
                            ),
                            cm,
                        )
                    except Exception as e:
                        print(str(e))
                        if str(e)=="'songs'":
                            playlist.pop(0)
                            await bot.send(
                                await bot.fetch_public_channel(
                                    config["channel"]
                                ),
                                '未检索到此歌曲',
                            )
                        else:
                            await bot.send(
                                await bot.fetch_public_channel(
                                    config["channel"]
                                ),
                                '发生错误，正在重试',
                            )
                        LOCK=False
                        duration=0
                        playtime=0
                        return None
                elif playlist[0]['type']=='b站':
                    try:
                        song_name=song_name.replace(" ", "")
                        bvid,cid,title,mid,name,pic=getAudio(getInformation(song_name))
                        starttime=int(round(time.time() * 1000))
                        endtime=starttime+int(duration*1000)
                        cm=[{"type": "card","theme": "secondary", "color": "#DD001B", "size": "lg","modules": [{"type": "section","text": {"type": "kmarkdown","content": "**标题:        ["+title+"](https://www.bilibili.com/video/"+song_name+"/)**"}},{"type": "section","text": {"type": "kmarkdown","content": "UP:         ["+name+"](https://space.bilibili.com/"+mid+"/)"}},{"type": "container","elements": [{"type": "image","src": pic}]},{"type": "countdown","mode": "second","startTime": starttime,"endTime": endtime}]}]
                        print(duration)
                        ban=re.compile('(惊雷)|(Lost Rivers)')
                        resu=ban.findall(title)
                        if len(resu)>0:
                            LOCK=False
                            playlist.pop(0)
                            await bot.send(
                                await bot.fetch_public_channel(
                                    config["channel"]
                                ),
                                '吃了吗，没吃吃我一拳',
                            )
                            duration=0
                            playtime=0
                            return None
                        playtime = 0
                        kill()
                        p = subprocess.Popen(
                            'ffmpeg -re -nostats -i "tmp.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+config["port"],
                            shell=True
                        )
                        await bot.send(
                            await bot.fetch_public_channel(
                                config["channel"]
                            ),
                            cm,
                        )
                    except:
                        await bot.send(
                            await bot.fetch_public_channel(
                                config["channel"]
                            ),
                            '发生错误，正在重试',
                        )
                        LOCK=False
                        duration=0
                        playtime=0
                        return None
                elif playlist[0]['type']=='网易电台':
                    try:
                        headers={
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                                'Cache-Control': 'max-age=0',
                                'Connection': 'keep-alive',
                                'Cookie': netease_cookie,
                                'Host': '127.0.0.1:3000',
                                'Referer': 'https://music.163.com',
                                'If-None-Match': 'W/"722-3Oy0PoR7kMdKeuZyLO+S/tZ4B6I"',
                                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"',
                                'sec-ch-ua-mobile': '?0',
                                'sec-ch-ua-platform': "Windows",
                                'Sec-Fetch-Dest': 'document',
                                'Sec-Fetch-Mode': 'navigate',
                                'Sec-Fetch-Site': 'none',
                                'Sec-Fetch-User': '?1',
                                'Upgrade-Insecure-Requests': '1',
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33'
                            }
                        song_name=song_name.replace(" ", "")
                        song_name=song_name.split('-')[-1]
                        print(song_name)
                        url='http://127.0.0.1:3000/dj/program/detail?id='+song_name
                        response=requests.get(url=url,headers=headers).json()['program']
                        duration=int(response['duration']/1000)+5
                        song_url='https://music.163.com/#/program?id='+song_name
                        song_name=response['mainSong']['name']

                        ban=re.compile('(惊雷)|(Lost Rivers)')
                        resu=ban.findall(song_name)
                        print(resu)
                        if len(resu)>0:
                            LOCK=False
                            playlist.pop(0)
                            await bot.send(
                                await bot.fetch_public_channel(
                                    config["channel"]
                                ),
                                '吃了吗，没吃吃我一拳',
                            )
                            duration=0
                            playtime=0
                            return None

                        album_name=response['radio']['name']
                        if album_name=='':
                            album_name='无专辑'
                        album_url='https://music.163.com/#/djradio?id='+str(response['radio']['id'])

                        singer_name=response['dj']['nickname']
                        singer_url='https://music.163.com/#/user/home?id='+str(response['dj']['userId'])
                        pic_url=response['radio']['picUrl']
                        getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['mainSong']['id'])
                        urlresponse=requests.get(url=getfile_url,headers=headers).json()['data'][0]['url']
                        print(urlresponse)
                        if urlresponse==None:
                            urlresponse=''
                        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and not urlresponse.endswith(".flac"):
                            getfile_url='http://127.0.0.1:3000/song/download/url?id='+str(response['mainSong']['id'])
                            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data']['url']
                            print(urlresponse)
                        if urlresponse==None:
                            urlresponse=''

                        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and not urlresponse.endswith(".flac"):
                            getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['mainSong']['id'])+'&br=2000000'
                            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data'][0]['url']
                            print(urlresponse)
                        if urlresponse==None:
                            urlresponse=''

                        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and not urlresponse.endswith(".flac"):
                            getfile_url='http://127.0.0.1:3000/song/download/url?id='+str(response['mainSong']['id'])+'&br=2000000'
                            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data']['url']
                            print(urlresponse)
                        if urlresponse==None:
                            urlresponse=''
                        if (urlresponse.startswith("http://m702") or urlresponse.startswith("http://m802") or len(urlresponse)==0)and not urlresponse.endswith(".flac"):
                            getfile_url='http://127.0.0.1:3000/song/url?id='+str(response['mainSong']['id'])+'?timestamp='
                            urlresponse=requests.get(url=getfile_url,headers=headers).json()['data'][0]['url']
                            print(urlresponse)
                        if urlresponse==None:
                            urlresponse=''
                        
                        musicfile = requests.get(urlresponse)
                        if urlresponse.endswith("flac"):
                            open("tmp.flac", "wb").write(musicfile.content)
                            kill()
                            p = subprocess.Popen(
                                'ffmpeg -re -nostats -i "tmp.flac" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+config["port"],
                                shell=True
                            )
                        else:
                            open("tmp.mp3", "wb").write(musicfile.content)
                            kill()
                            p = subprocess.Popen(
                                'ffmpeg -re -nostats -i "tmp.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+config["port"],
                                shell=True
                            )



                        playtime = 0

                        starttime=int(round(time.time() * 1000))
                        endtime=starttime+int(duration*1000)
                        cm = [ { "type": "card", "theme": "secondary", "color": "#DD001B", "size": "lg", "modules": [ { "type": "header", "text": { "type": "plain-text", "content": "正在播放：" + song_name, }, }, { "type": "section", "text": { "type": "kmarkdown", "content":"(met)" +playlist[0]['userid']+"(met)", }, }, { "type": "context", "elements": [ { "type": "kmarkdown", "content": "歌手： [" + singer_name + "](" + singer_url + ")  —出自专辑 [" + album_name + "](" + album_url + ")", } ], }, { "type": "audio", "title": song_name, "src": urlresponse, "cover": pic_url, }, {"type": "countdown","mode": "second","startTime": starttime,"endTime": endtime},{"type": "divider"}, { "type": "context", "elements": [ { "type": "image", "src":  "https://img.kaiheila.cn/assets/2022-05/UmCnhm4mlt016016.png", }, { "type": "kmarkdown", "content": "网易云音乐  [在网页查看](" + song_url + ")", }, ], }, ], } ]
                        print(duration)

                        kill()
                        p = subprocess.Popen(
                            'ffmpeg -re -nostats -i "tmp.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+config["port"],
                            shell=True
                        )
                        await bot.send(
                            await bot.fetch_public_channel(
                                config["channel"]
                            ),
                            cm,
                        )
                    except:
                        await bot.send(
                            await bot.fetch_public_channel(
                                config["channel"]
                            ),
                            '发生错误，正在重试',
                        )
                        LOCK=False
                        duration=0
                        playtime=0
                        return None
                else:
                    try:
                        url="http://127.0.0.1:3300/search?key="+song_name+"&pageSize=1"
                        response=requests.get(url=url).json()['data']['list'][0]
                        song_name=response['songname']
                        ban=re.compile('(惊雷)|(Lost Rivers)')
                        resu=ban.findall(song_name)
                        if len(resu)>0:
                            LOCK=False
                            playlist.pop(0)
                            await bot.send(
                                await bot.fetch_public_channel(
                                    config["channel"]
                                ),
                                '吃了吗，没吃吃我一拳',
                            )
                            duration=0
                            playtime=0
                            return None
                        duration=response['interval']+5
                        song_url='https://y.qq.com/n/ryqq/songDetail/'+response['songmid']
                        album_name=response['albumname']
                        if album_name=='':
                            album_name='无专辑'
                        album_url='https://y.qq.com/n/ryqq/albumDetail/'+response['albummid']
                        singer_name=response['singer'][0]['name']
                        singer_url='https://y.qq.com/n/ryqq/singer/'+response['singer'][0]['mid']
                        pic_url='https://y.gtimg.cn/music/photo_new/T002R300x300M000'+response['albummid']+'.jpg'
                        getfile_url='http://127.0.0.1:3300/song/url?id='+response['songmid']+'&mediaId='+response['strMediaMid']+'&ownCookie=1'
                        try:
                            response=requests.get(url=getfile_url).json()['data']
                        except:
                            await bot.send(
                                await bot.fetch_public_channel(
                                    config["channel"]
                                ),
                                'api cookie失效',
                            )
                            playlist.pop(0)
                            LOCK=False
                            duration=0
                            playtime=0
                            return None
                        musicfile = requests.get(response)
                        open("tmp.mp3", "wb").write(musicfile.content)
                        starttime=int(round(time.time() * 1000))
                        endtime=starttime+int(duration*1000)
                        playtime = 0
                        kill()
                        p = subprocess.Popen(
                            'ffmpeg -re -nostats -i "tmp.mp3" -acodec libopus -ab 128k -f mpegts zmq:tcp://127.0.0.1:'+config["port"],
                            shell=True
                        )
                        cm = [ { "type": "card", "theme": "secondary", "color": "#DD001B", "size": "lg", "modules": [ { "type": "header", "text": { "type": "plain-text", "content": "正在播放：" + song_name }, }, { "type": "section", "text": { "type": "kmarkdown", "content":"(met)" +playlist[0]['userid']+"(met)", }, }, { "type": "context", "elements": [ { "type": "kmarkdown", "content": "歌手： [" + singer_name + "](" + singer_url + ")  —出自专辑 [" + album_name + "](" + album_url + ")", } ], }, { "type": "audio", "title": song_name, "src": response, "cover": pic_url, }, {"type": "countdown","mode": "second","startTime": starttime,"endTime": endtime},{"type": "divider"}, { "type": "context", "elements": [ { "type": "image", "src": "https://img.kaiheila.cn/assets/2022-06/cqzmClO3Sq07s07x.png/ld", }, { "type": "kmarkdown", "content": "QQ音乐  [在网页查看](" + song_url + ")", }, ], }, ], } ]
                        await bot.send(
                            await bot.fetch_public_channel(
                                config["channel"]
                            ),
                            cm,
                        )
                    except:
                        await bot.send(
                            await bot.fetch_public_channel(
                                config["channel"]
                            ),
                            '发生错误，正在重试',
                        )
                        LOCK=False
                        duration=0
                        playtime=0
                        return None
                playtime += deltatime
                LOCK = False
                return None
            else:
                if playtime + deltatime < duration:
                    playtime += deltatime
                    LOCK = False
                    return None
                else:
                    playtime = 0
                    playlist.pop(0)
                    LOCK = False
                    return None

@bot.task.add_interval(minutes=30)
async def keep_login():
    url='http://127.0.0.1:3000/login/refresh'
    requests.get(url=url)
    print('刷新登录')

bot.command.update_prefixes("")
bot.run()
