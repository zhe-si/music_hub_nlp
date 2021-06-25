from __future__ import unicode_literals

import os
import sys

import requests

sys.path.append("/")
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser

from jieba.analyse.analyzer import ChineseAnalyzer


# def test():
#     paddle.enable_static()
#     jieba.enable_paddle()  # 启动paddle模式。 0.40版之后开始支持，早期版本不支持
#     strs = ["我来到北京清华大学", "他来到了网易杭研大厦", "乒乓球拍卖完了", "中国科学技术大学"]
#     for str in strs:
#         seg_list = jieba.cut(str, use_paddle=True)  # 使用paddle模式
#         print("Paddle Mode: " + '/'.join(list(seg_list)))
#
#         seg_list = jieba.cut(str)  # 默认是精确模式
#         print("default: " + "/".join(seg_list))
#     data = "素胚勾勒出青花笔锋浓转淡,瓶身描绘的牡丹一如你初妆,冉冉檀香透过窗心事我了然,宣纸上走笔至此搁一半"
#     seg_list = jieba.cut(data, use_paddle=True)  # 使用paddle模式
#     print("Paddle Mode: " + '/'.join(list(seg_list)))
#
#     seg_list = jieba.cut(data)  # 默认是精确模式
#     print("default: " + "/".join(seg_list))


# def test2():
#     data = "素胚勾勒出青花笔锋浓转淡,瓶身描绘的牡丹一如你初妆,冉冉檀香透过窗心事我了然,宣纸上走笔至此搁一半"
#
#     seg_list_p = jieba.cut(data, use_paddle=True)  # 使用paddle模式
#
#     seg_list = jieba.cut(data)  # 默认是精确模式
#
#     k_words = jieba.analyse.extract_tags(data, topK=5)
#     print(k_words)
#
#     k_words = jieba.analyse.extract_tags(" ".join(seg_list_p), topK=5)
#     print(k_words)
#
#     k_words = jieba.analyse.extract_tags(" ".join(seg_list), topK=5)
#     print(k_words)


# jieba搜索引擎测试
def test_search():
    analyzer = ChineseAnalyzer()

    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True, analyzer=analyzer))
    if not os.path.exists("tmp"):
        os.mkdir("tmp")

    ix = create_in("tmp", schema)  # for create new index
    # ix = open_dir("tmp") # for read only
    writer = ix.writer()

    writer.add_document(
        title="document1",
        path="/a",
        content="This is the first document we’ve added!"
    )

    writer.add_document(
        title="document2",
        path="/b",
        content="The second one 你 中文测试中文 is even more interesting! 吃水果"
    )

    writer.add_document(
        title="document3",
        path="/c",
        content="买水果然后来世博园。"
    )

    writer.add_document(
        title="document4",
        path="/c",
        content="工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作"
    )

    writer.add_document(
        title="document4",
        path="/c",
        content="咱俩交换一下吧。"
    )

    writer.commit()
    searcher = ix.searcher()
    parser = QueryParser("content", schema=ix.schema)

    for keyword in ("水果世博园", "你", "first", "中文", "交换机", "交换"):
        print("result of ", keyword)
        q = parser.parse(keyword)
        results = searcher.search(q)
        for hit in results:
            print(hit.highlights("content"))
        print("=" * 10)

    for t in analyzer("我的好朋友是李明;我爱北京天安门;IBM和Microsoft; I have a dream. this is intetesting and interested me a lot"):
        print(t.text)


def main():
    url = "http://localhost:13889/api/recommend_musics_by_musics"
    url1 = "http://localhost:13889/api/make_song_list_by_words"
    url2 = "http://localhost:13889/api/search_songs_by_words"
    # r = requests.post(url1, json={"musics_id": [31010566]})
    # r = requests.post(url1, json={"words": ["欧美", "势不可挡"]})
    r = requests.post(url2, json={"words": ["欧美", "势不可挡"]})
    print(r.text)
    pass


if __name__ == '__main__':
    main()
