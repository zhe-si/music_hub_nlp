import ast
import asyncio
import json
import os
import re
import string

import aiofiles
import aiohttp
import requests

my_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 Edg/91.0.864.54'}


async def fetch(client, url, try_time=5):
    for i in range(try_time):
        try:
            async with client.get(url, params=my_headers) as resp:
                assert resp.status == 200
                return await resp.text()
        except BaseException as e:
            print(e)


async def run_fetch(urls: list):
    async with aiohttp.ClientSession() as client:
        tasks = []
        for url in urls:
            tasks.append(asyncio.create_task(fetch(client, url)))
        await asyncio.wait(tasks)
        return [t.result() for t in tasks]


async def download_and_save(client, url, save_file_path, try_time=5):
    for i in range(try_time):
        try:
            async with client.get(url, params=my_headers) as resp:
                assert resp.status == 200
                file = await resp.read()
                if is_pic(file) or is_mp3(file):
                    async with aiofiles.open(save_file_path, "wb") as f:
                        await f.write(file)
                    return
        except BaseException as e:
            print("exception: > {}".format(e))


async def run_download(urls: list, save_path: str, files_name=None):
    files_path = []
    async with aiohttp.ClientSession() as client:
        tasks = []
        for i in range(len(urls)):
            url = urls[i]
            if files_name is None:
                file_name = re.split("[/=]", url)[-1]
            else:
                file_name = files_name[i]
            file_path = os.path.join(save_path, file_name)
            files_path.append(file_path)
            tasks.append(asyncio.create_task(download_and_save(client, url, file_path)))
        await asyncio.wait(tasks)
    return files_path


music_tips = "欧美 日语 韩语 华语 粤语 " \
             "流行 摇滚 民谣 电子 舞曲 说唱 轻音乐 爵士 乡村 R%26B%2FSoul 古典 民族 英伦 金属 蓝调 雷鬼 世界音乐 拉丁 New%20Age 古风 Bossa%20Nova " \
             "清晨 夜晚 学习 工作 午休 下午茶 地铁 驾车 运动 旅行 散步 酒吧 " \
             "怀旧 清新 浪漫 伤感 治愈 放松 孤独 感动 兴奋 快乐 安静 思念 " \
             "综艺 影视原声 ACG 儿童 校园 游戏 70后 80后 90后 网络歌曲 KTV 经典 翻唱 吉他 钢琴 器乐 榜单 00后".split()


def main():
    # id，歌名，歌手名，原本歌词，翻译歌词，分类，歌曲链接
    # musics_data = {}
    musics_data = read_data_from_file("data/temp/music_100.txt")

    # 获取各分类下n首歌曲基本信息（放到musics_data中）
    # i = 0
    # while True:
    #     try:
    #         add_music_id_name_author(music_tips[i], musics_data, 100)
    #         i += 1
    #     except BaseException as e:
    #         print("\nexception > " + str(e) + " " + str(e.args))
    #         time.sleep(0.5)
    #     if i >= len(music_tips):
    #         break
    #     print("\rfetch music id: {:.4f}%".format(i / len(music_tips) * 100), end="")
    # print()

    # 得到音乐的id
    musics_id = [m_i for m_i in musics_data]

    # 下载图片、mp3等
    tar_data = "pic_url"
    fin_pos = len(musics_id) // 10 if len(musics_id) % 10 == 0 else len(musics_id) // 10 + 1
    for i in range(fin_pos):
        print(download_urls([musics_data[i][tar_data] for i in musics_id[i * 10: min(i * 10 + 10, len(musics_id))] if
                             musics_data[i][tar_data] is not None], "E:/1"))
        # save_path = r"F:\My_Resources\datasets\music"
        # id_range = musics_id[i * 10: min(i * 10 + 10, len(musics_id))]
        # id_range = [m_i for m_i in id_range if not os.path.exists(os.path.join(save_path, "{}.mp3".format(m_i)))]
        # print(download_urls([music163_song_api.format(i) for i in id_range],
        #                     save_path,
        #                     ["{}.mp3".format(m_i) for m_i in id_range]))
        # print("download {:.4f}%".format(i / fin_pos * 100))

    # 获取音乐的url（放到musics_data中）
    # add_music_url(musics_data, musics_id)

    # 获取歌词（放到musics_data中）
    # add_music_lyric(musics_data, musics_id)

    # 获取专辑封面图（放到musics_data中）
    # add_music_pic(musics_data, musics_id)

    # with open("data/music_100t.txt", "w", encoding="utf8") as f:
    #     f.write(str(musics_data))


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


def add_music_pic(musics_data, musics_id):
    musics_detail = []
    fin_pos = len(musics_id) // 10 if len(musics_id) % 10 == 0 else len(musics_id) // 10 + 1
    for i in range(fin_pos):
        details = request_music_details(musics_id[i * 10: min(i * 10 + 10, len(musics_id))])
        musics_detail.extend(details)
        print("\rfetch music details: {:.4f}%".format(i / fin_pos * 100), end="")
    print()
    for i in range(len(musics_id)):
        m_d = musics_detail[i]
        music_id = musics_id[i]
        if len(m_d["songs"]) == 0:
            musics_data[music_id]["pic_url"] = None
        else:
            musics_data[music_id]["pic_url"] = m_d["songs"][0]["al"]["picUrl"]


def add_music_url(musics_data, musics_id):
    musics_info = []
    fin_pos = len(musics_id) // 10 if len(musics_id) % 10 == 0 else len(musics_id) // 10 + 1
    for i in range(fin_pos):
        infos = request_music_song(musics_id[i * 10: min(i * 10 + 10, len(musics_id))])
        musics_info.extend(infos)
        print("\rfetch music url: {:.4f}%".format(i / fin_pos * 100), end="")
    print()
    for m_i in musics_info:
        music_id = m_i["data"][0]["id"]
        musics_data[music_id]["url"] = m_i["data"][0]["url"]


def add_music_lyric(musics_data, musics_id):
    musics_lyric = []
    fin_pos = len(musics_id) // 10 if len(musics_id) % 10 == 0 else len(musics_id) // 10 + 1
    for i in range(fin_pos):
        musics_lyric.extend(request_music_lyric(musics_id[i * 10: min(i * 10 + 10, len(musics_id))]))
        print("\rfetch music lyric: {:.4f}%".format(i / fin_pos * 100), end="")
    print()
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
music163_song_api = "http://music.163.com/song/media/outer/url?id={}.mp3"
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
    responds = loop.run_until_complete(run_fetch(urls))
    for r_id in range(len(urls)):
        r = responds[r_id]
        if r.find("460") != -1:
            responds[r_id] = requests.get(urls[r_id], headers=my_headers).text
    return responds


def cant_find(sentence, *words):
    for word in words:
        if sentence.find(word) != -1:
            return False
    return True


def is_mp3(bytes_data: bytes):
    if bytes_data[:3] == b"ID3" or bytes_data[-32:-35] == b"TAG":
        return True
    return False


def is_pic(bytes_data: bytes):
    if check_pic_type(bytes_data) is None:
        return False
    return True


def check_pic_type(bytes_data: bytes):
    if bytes_data[6:10] in (b'JFIF', b'Exif'):
        return 'jpeg'
    elif bytes_data.startswith(b'\211PNG\r\n\032\n'):
        return 'png'
    elif bytes_data[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    elif bytes_data[:2] in (b'MM', b'II'):
        return 'tiff'
    elif bytes_data.startswith(b'\001\332'):
        return 'rgb'
    elif len(bytes_data) >= 3 and bytes_data[0] == ord(b'P') and bytes_data[1] in b'14' and bytes_data[2] in b' \t\n\r':
        return 'pbm'
    elif len(bytes_data) >= 3 and bytes_data[0] == ord(b'P') and bytes_data[1] in b'25' and bytes_data[2] in b' \t\n\r':
        return 'pgm'
    elif len(bytes_data) >= 3 and bytes_data[0] == ord(b'P') and bytes_data[1] in b'36' and bytes_data[2] in b' \t\n\r':
        return 'ppm'
    elif bytes_data.startswith(b'\x59\xA6\x6A\x95'):
        return 'rast'
    elif bytes_data.startswith(b'#define '):
        return 'xbm'
    elif bytes_data.startswith(b'BM'):
        return 'bmp'
    elif bytes_data.startswith(b'RIFF') and bytes_data[8:12] == b'WEBP':
        return 'webp'
    elif bytes_data.startswith(b'\x76\x2f\x31\x01'):
        return 'exr'
    else:
        return None


def is_text(r_b: bytes):
    try:
        r_t = r_b[:60].decode("utf8")
    except Exception as e:
        return False

    num = 0
    for c in r_t:
        if '\u4e00' <= c <= '\u9fa5' or c in string.printable:
            num += 1
        if num > 42:
            return True
    return False


def download_urls(urls, save_path, files_name=None):
    if files_name is not None and len(urls) > len(files_name):
        files_name = None

    loop = asyncio.get_event_loop()
    files_path = loop.run_until_complete(run_download(urls, save_path, files_name))
    for r_id in range(len(urls)):
        file_p = files_path[r_id]
        if os.path.isdir(file_p):
            files_path[r_id] = None
        elif not os.path.exists(file_p):
            r = requests.get(urls[r_id], headers=my_headers)
            r_b = r.content
            if is_pic(r_b) or is_mp3(r_b):
                with open(file_p, "wb") as f:
                    f.write(r_b)
            else:
                files_path[r_id] = None
    return files_path


if __name__ == '__main__':
    main()
