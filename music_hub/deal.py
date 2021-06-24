import os
import os
import random
import re

import jieba
import jieba.analyse
from gensim.models import word2vec, KeyedVectors

from music_hub.data import read_data_from_file


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


def get_lrc_zh(music_data: dict):
    r = re.compile("\[.*?\]")
    if music_data["tlrc"] is not None:
        lrc = music_data["tlrc"]
    elif music_data["lrc"] is not None:
        lrc = music_data["lrc"]
    else:
        return ""
    return r.sub("", lrc)


def get_not_none(music_data, key):
    v = music_data[key]
    if v is None:
        return ""
    else:
        return v


def get_music_text(music_data: dict):
    """得到音乐的一般描述，包括曲名，歌词"""
    return "\n".join([get_not_none(music_data, "name"), get_lrc_zh(music_data)])


def get_music_all_text(music_data: dict):
    """得到音乐的完全描述，包括曲名，类别，歌手名，歌词"""
    return "\n".join([get_not_none(music_data, "name"),
                      get_not_none(music_data, "tip"),
                      get_not_none(music_data, "author_name"),
                      get_lrc_zh(music_data)])


cal_key_words_tfidf = jieba.analyse.extract_tags
cal_key_words_textrank = jieba.analyse.textrank


def get_key_words(text: str, n, cal_key_words=cal_key_words_tfidf):
    k_words = cal_key_words(text, topK=min(n, len(text) // 4), withWeight=False)
    return k_words


def get_music_text_key_words(music_data: dict, n):
    music_text = get_music_text(music_data)
    author_name = music_data["author_name"]
    music_tip = music_data["tip"]
    key_words = []
    if author_name is not None:
        key_words.append(author_name)
    if music_tip is not None:
        key_words.append(music_tip)
    words = get_key_words(music_text, n - len(key_words))
    key_words.extend(words)

    return key_words


def cut_musics_all_text_save(musics_data: dict, save_path):
    with open(save_path, "w", encoding="utf8") as f:
        for m_i, m_d in musics_data.items():
            words = jieba.cut(get_music_all_text(m_d))
            f.write(" ".join(words))
            f.write("\n")
            f.flush()


DEFAULT_MAX_NUM = 15


def recommend_musics_by_musics(model, musics_data, musics_id: list, n=DEFAULT_MAX_NUM) -> list:
    """
    根据音乐列表产生推荐音乐列表（不会有一半以上重复）
    :param musics_data: 所有音乐数据
    :param model: word2vec模型
    :param musics_id: 音乐id列表
    :param n: 最大音乐数量
    :return: 推荐音乐id列表
    """
    key_words = []
    for m_i in musics_id:
        key_words.extend(musics_data[m_i])
    return cal_random_similar_musics_by_words(model, key_words, musics_data, n,
                                              random.sample(musics_id, max(len(musics_id) - n // 2, 0)))


def make_song_list_by_words(model, musics_data, words: list, n=DEFAULT_MAX_NUM) -> tuple[str, str, list]:
    """
    根据描述的单词列表随机产生相符的歌单
    :param musics_data: 所有音乐数据
    :param model: word2vec模型
    :param words: 描述的单词列表
    :param n: 最大音乐数量
    :return: 歌单结构（歌单名，歌单描述，歌单id列表）
    """
    musics_id = [i[0] for i in cal_random_similar_musics_by_words(model, words, musics_data, n)]
    return "", "", musics_id


def search_songs_by_words(model, musics_data, words: list, n=DEFAULT_MAX_NUM) -> list:
    """
    根据描述的单词列表随机产生音乐列表
    :param musics_data: 所有音乐数据
    :param model: word2vec模型
    :param words: 描述的单词列表
    :param n: 最大音乐数量
    :return: 搜索到的音乐id列表
    """
    return [i[0] for i in cal_random_similar_musics_by_words(model, words, musics_data, n)]


class NItem:
    """得到最大、最小的n个数，动态添加"""

    def __init__(self, n, is_max=True, key=lambda s: s):
        self._n = n
        self._compare = (lambda x, y: x < y) if is_max else (lambda x, y: x > y)
        self._n_list = []
        self._key = key

    def add_item(self, item):
        if len(self._n_list) == 0:
            self._n_list.append(item)
        for i in range(len(self._n_list)):
            if self._compare(self._key(item), self._key(self._n_list[i])):
                self._n_list.insert(i, item)
                break
        else:
            self._n_list.append(item)
        while len(self._n_list) > self._n:
            self._n_list.pop(0)

    def get_list(self):
        return self._n_list.copy()

    def clear_list(self):
        self._n_list.clear()


RANDOM_EXPAND = 3


def cal_similar_musics_by_words(model: KeyedVectors, words: list, musics_data: dict, n):
    min_list = NItem(n, is_max=False, key=lambda x: x[1])
    for m_i, m_d in musics_data.items():
        distance = model.n_similarity(words, m_d["key_words"])
        min_list.add_item((m_i, distance))
    return min_list.get_list()


def cal_random_similar_musics_by_words(model: KeyedVectors, words: list, musics_data: dict, n, exclude_list=()):
    similar_musics = cal_similar_musics_by_words(model, words, musics_data, n * RANDOM_EXPAND + len(exclude_list))
    similar_musics = [m for m in similar_musics if m[0] not in exclude_list]
    return random.sample(similar_musics, min(n, len(similar_musics)))


def main():
    musics_data = read_data_from_file("data/music_100.txt")

    add_jieba_lexicon(musics_data)

    load_model(musics_data)

    model = load_model(musics_data)

    for m_i, m_d in musics_data.items():
        music_key_words = get_music_text_key_words(m_d, 20)
        m_d["key_words"] = music_key_words


def add_jieba_lexicon(musics_data):
    for m_i, m_d in musics_data.items():
        jieba.add_word(m_d["author_name"])
        jieba.add_word(m_d["tip"])


def load_model(musics_data):
    m_t_path = "./data/musics_text/musics_text.txt"
    if not os.path.exists(m_t_path):
        cut_musics_all_text_save(musics_data, m_t_path)
    model_path = "./model/music_text_word2vec.model"
    if not os.path.exists(model_path):
        s = word2vec.Text8Corpus(m_t_path)
        model = word2vec.Word2Vec(s, sg=1, min_count=1, window=5, vector_size=150)
        model.save(model_path)
    else:
        model = word2vec.Word2Vec.load(model_path)
    return model.wv


if __name__ == '__main__':
    # test2()
    main()
    # test()
