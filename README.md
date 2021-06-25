# Music Hub nlp处理
- 包括网易云音乐数据爬取与nlp文本处理
- 提供搜索、歌单生成、歌曲推荐等api
- 是一个http协议的web程序
- 部署链接(有效期至2021.8.22)：http://182.92.163.69:13889/

## API
1. /api/recommend_musics_by_musics  
   - 描述：根据歌曲推荐api
   - 参数：http请求, post方法, 方法体为json, 必选参数: "musics_id"歌曲id列表, 可选参数: "max_n"最大推荐数
   - 返回：json: "result" -> 推荐歌曲id列表
   
2. /api/make_song_list_by_words
   - 描述：根据关键词生成歌单api
   - 参数：http请求, post方法, 方法体为json, 必选参数: "words"描述词列表, 可选参数: "max_n"最大推荐数
   - 返回：json: "result"歌单结构(歌单名，歌单描述，歌曲id列表)
   
3. /api/search_songs_by_words
   - 描述：根据关键词模糊搜索歌曲api
   - 参数：http请求, post方法, 方法体为json, 必选参数: "words"描述词列表, 可选参数: "max_n"最大推荐数
   - 返回：json: "result"歌曲id列表