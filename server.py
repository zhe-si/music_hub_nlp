import multiprocessing

from sanic import Sanic, Request
from sanic.response import file, json

import nlp

app = Sanic("music_hub_nlp_server")

header = {"Access-Control-Allow-Origin": "*"}


@app.get("/")
async def main_page(request: Request):
    return await file("html/welcome.html")


@app.post("/api/recommend_musics_by_musics")
async def recommend_musics_by_musics_service(request: Request):
    """
    根据歌曲推荐api
    :param request: http请求, post方法, 方法体为json, 必选参数: "musics_id"歌曲id列表, 可选参数: "max_n"最大推荐数
    :return: json: "result"推荐歌曲id列表
    """
    if "musics_id" in request.json:
        musics_id = request.json["musics_id"]
    else:
        return json({"error": "request arguments error"}, status=400, headers=header)
    try:
        if "max_n" in request.json:
            max_n = request.json["max_n"]
            result = nlp.recommend_musics_by_musics(musics_id, max_n)
        else:
            result = nlp.recommend_musics_by_musics(musics_id)
    except Exception as e:
        return json({"error": "request arguments error"}, status=400, headers=header)

    return json({"result": result}, headers=header)


@app.post("/api/make_song_list_by_words")
async def make_song_list_by_words_service(request: Request):
    """
    根据关键词生成歌单api
    :param request: http请求, post方法, 方法体为json, 必选参数: "words"描述词列表, 可选参数: "max_n"最大推荐数
    :return: json: "result"歌单结构(歌单名，歌单描述，歌曲id列表)
    """
    if "words" in request.json:
        words = request.json["words"]
    else:
        return json({"error": "request arguments error"}, status=400, headers=header)
    try:
        if "max_n" in request.json:
            max_n = request.json["max_n"]
            result = nlp.make_song_list_by_words(words, max_n)
        else:
            result = nlp.make_song_list_by_words(words)
    except Exception as e:
        return json({"error": "request arguments error"}, status=400, headers=header)

    return json({"result": result}, headers=header)


@app.post("/api/search_songs_by_words")
async def search_songs_by_words_service(request: Request):
    """
    根据关键词搜索歌曲api
    :param request: http请求, post方法, 方法体为json, 必选参数: "words"描述词列表, 可选参数: "max_n"最大推荐数
    :return: json: "result"歌曲id列表
    """
    if "words" in request.json:
        words = request.json["words"]
    else:
        return json({"error": "request arguments error"}, status=400, headers=header)
    try:
        if "max_n" in request.json:
            max_n = request.json["max_n"]
            result = nlp.search_songs_by_words(words, max_n)
        else:
            result = nlp.search_songs_by_words(words)
    except Exception as e:
        return json({"error": "request arguments error"}, status=400, headers=header)

    return json({"result": result}, headers=header)


def main():
    workers = multiprocessing.cpu_count()
    app.run(host="0.0.0.0", port=13889, access_log=True, workers=workers, debug=False)


if __name__ == '__main__':
    main()
