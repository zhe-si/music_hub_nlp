import asyncio
import json
import time
import ast

import aiohttp
import requests

my_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 Edg/91.0.864.54'}


async def fetch(client, url):
    while True:
        try:
            async with client.get(url, params=my_headers) as resp:
                assert resp.status == 200
                return await resp.text()
        except BaseException as e:
            print(e)


async def run(urls: list):
    async with aiohttp.ClientSession() as client:
        tasks = []
        for url in urls:
            tasks.append(asyncio.create_task(fetch(client, url)))
        await asyncio.wait(tasks)
        return [t.result() for t in tasks]


music_tips = "欧美 日语 韩语 华语 粤语 " \
             "流行 摇滚 民谣 电子 舞曲 说唱 轻音乐 爵士 乡村 R%26B%2FSoul 古典 民族 英伦 金属 蓝调 雷鬼 世界音乐 拉丁 New%20Age 古风 Bossa%20Nova " \
             "清晨 夜晚 学习 工作 午休 下午茶 地铁 驾车 运动 旅行 散步 酒吧 " \
             "怀旧 清新 浪漫 伤感 治愈 放松 孤独 感动 兴奋 快乐 安静 思念 " \
             "综艺 影视原声 ACG 儿童 校园 游戏 70后 80后 90后 网络歌曲 KTV 经典 翻唱 吉他 钢琴 器乐 榜单 00后".split()


def main():
    # id，歌名，歌手名，原本歌词，翻译歌词，分类，歌曲链接
    musics_data = {}
    # musics_data = read_data_from_file("E:/t.txt")

    # 获取各分类下n首歌曲基本信息
    i = 0
    while True:
        try:
            add_music_id_name_author(music_tips[i], musics_data, 100)
            i += 1
        except BaseException as e:
            print("\nexception > " + str(e) + " " + str(e.args))
            time.sleep(0.5)
        if i >= len(music_tips):
            break
        print("\rfetch music id: {:.4f}%".format(i / len(music_tips) * 100), end="")
    print()
    # 得到音乐的id
    musics_id = [m_i for m_i in musics_data]
    # # 获取音乐的url
    add_music_url(musics_data, musics_id)

    # 获取歌词
    add_music_lyric(musics_data, musics_id)
    with open("./data/music_100.txt", "w", encoding="utf8") as f:
        f.write(str(musics_data))


def read_data_from_file(f_path: str):
    with open(f_path, "r", encoding="utf8") as f:
        s = f.read()
        musics_data = ast.literal_eval(s)
    return musics_data


def add_music_id_name_author(music_tip, musics_data, musics_num):
    music_list = request_music_list(music_tip, musics_num)
    i = 0
    search_num = music_list[0]["result"]['songCount']
    for data in music_list:
        if i >= search_num or data["result"]["songCount"] != search_num:
            break
        if "songs" not in data["result"]:
            continue
        for music_data in data["result"]["songs"]:
            music_id = music_data["id"]
            music_name = music_data["name"]
            music_author_name = music_data["artists"][0]["name"]
            musics_data[music_id] = {"name": music_name, "author_name": music_author_name, "tip": music_tip}
            i += 1


def add_music_url(musics_data, musics_id):
    musics_info = []
    fin_pos = len(musics_id) // 10 if len(musics_id) % 10 == 0 else len(musics_id) // 10 + 1
    for i in range(fin_pos):
        infos = request_music_song(musics_id[i * 10: min(i * 10 + 10, len(musics_id))])
        musics_info.extend(infos)
        print("\rfetch music url: {:.4f}%".format(i / fin_pos * 100), end="")
    for m_i in musics_info:
        music_id = m_i["data"][0]["id"]
        musics_data[music_id]["url"] = m_i["data"][0]["url"]


def add_music_lyric(musics_data, musics_id):
    musics_lyric = []
    fin_pos = len(musics_id) // 10 if len(musics_id) % 10 == 0 else len(musics_id) // 10 + 1
    for i in range(fin_pos):
        musics_lyric.extend(request_music_lyric(musics_id[i * 10: min(i * 10 + 10, len(musics_id))]))
        print("\rfetch music lyric: {:.4f}%".format(i / fin_pos * 100), end="")
    for i in range(len(musics_id)):
        music_id = musics_id[i]
        music_lyric_data = musics_lyric[i]
        if "lrc" in music_lyric_data and "lyric" in music_lyric_data["lrc"]:
            musics_data[music_id]["lrc"] = music_lyric_data["lrc"]["lyric"]
        else:
            musics_data[music_id]["lrc"] = None

        if "tlyric" in music_lyric_data and "lyric" in music_lyric_data["tlyric"]:
            musics_data[music_id]["tlrc"] = music_lyric_data["tlyric"]["lyric"]
        else:
            musics_data[music_id]["tlrc"] = None


music163_api = "https://api.imjad.cn/cloudmusic/?type={}&id={}"
api_types = ["song", "lyric", "detail", "playlist", "comments"]


def request_music_list(music_tip, music_num):
    playlist_api = "https://music.163.com/api/playlist/detail?id={}"
    search_api_1 = "http://music.163.com/api/search/get/web?" \
                   "csrf_token=hlpretag=&hlposttag=&s={}&type=1&offset={}&total=true&limit=20"
    search_api_2 = "https://api.imjad.cn/cloudmusic/?type={}&search_type={}&s={}"
    data = []
    limit_size = 20
    urls = [search_api_1.format(music_tip, i * limit_size) for i in range(max(music_num // limit_size, 1))]
    responds = fetch_urls(urls)
    for respond in responds:
        data.append(json.loads(respond))
    return data


def request_music_song(music_ids):
    return request_music_data(music_ids, api_types[0])


def request_music_lyric(music_ids):
    return request_music_data(music_ids, api_types[1])


def request_music_details(music_ids):
    return request_music_data(music_ids, api_types[2])


def request_music_data(music_ids, request_type):
    data = []
    urls = [music163_api.format(request_type, music_id) for music_id in music_ids]
    responds = fetch_urls(urls)
    for respond in responds:
        data.append(json.loads(respond))
    return data


def fetch_urls(urls):
    loop = asyncio.get_event_loop()
    responds = loop.run_until_complete(run(urls))
    for r_id in range(len(urls)):
        r = responds[r_id]
        if r.find("460") != -1:
            responds[r_id] = requests.get(urls[r_id], headers=my_headers).text
    return responds


if __name__ == '__main__':
    main()
