import os
import random
import re

import jieba
import jieba.analyse
from gensim.models import word2vec, KeyedVectors

from data import read_data_from_file
from tools import NItem, get_not_none, make_sure_exist


"""处理音乐信息"""


def get_lrc_zh(music_data: dict):
    r = re.compile("\[.*?\]")
    if music_data["tlrc"] is not None:
        lrc = music_data["tlrc"]
    elif music_data["lrc"] is not None:
        lrc = music_data["lrc"]
    else:
        return ""
    return r.sub("", lrc)


def get_music_text(music_data: dict):
    """得到音乐的一般描述，包括曲名，歌词"""
    return "\n".join([get_not_none(music_data, "name"), get_lrc_zh(music_data)])


def get_music_all_text(music_data: dict):
    """得到音乐的完全描述，包括曲名，类别，歌手名，歌词"""
    return "\n".join([get_not_none(music_data, "name"),
                      get_not_none(music_data, "tip"),
                      get_not_none(music_data, "author_name"),
                      get_lrc_zh(music_data)])


"""计算文本关键词"""
cal_key_words_tfidf = jieba.analyse.extract_tags
cal_key_words_textrank = jieba.analyse.textrank


def get_key_words(text: str, n, cal_key_words=cal_key_words_tfidf):
    k_words = cal_key_words(text, topK=min(n, len(text) // 4), withWeight=False)
    return k_words


"""计算相似歌曲"""
RANDOM_EXPAND = 3


def cal_similar_musics_by_words(model: KeyedVectors, words: list, musics_data: dict, n):
    words = [word for word in words if word in model]
    if len(words) == 0:
        return [(i, 1) for i in random.sample(list(musics_data.keys()), n)]

    min_list = NItem(n, is_max=False, key=lambda x: x[1])
    for m_i, m_d in musics_data.items():
        m_words = [word for word in m_d["key_words"] if word in model]
        distance = model.n_similarity(words, m_words)
        min_list.add_item((m_i, distance))
    return min_list.get_list()


def cal_random_similar_musics_by_words(model: KeyedVectors, words: list, musics_data: dict, n, exclude_list=()):
    """返回（id, 相似度）"""
    similar_musics = cal_similar_musics_by_words(model, words, musics_data, n * RANDOM_EXPAND + len(exclude_list))
    similar_musics = [m for m in similar_musics if m[0] not in exclude_list]
    return random.sample(similar_musics, min(n, len(similar_musics)))


"""计算歌单标题"""


def cal_songs_list_name_sample(songs_id: list, musics_data: dict):
    """随机在歌曲关键词中选取较长的单词作为歌单题目"""
    longest_words = NItem(6, key=lambda x: len(x))
    for i in songs_id:
        longest_words.add_items(musics_data[i]["key_words"])
    return random.choice(longest_words.get_list())


"""初始化与预处理"""


def add_jieba_lexicon(musics_data):
    for m_i, m_d in musics_data.items():
        jieba.add_word(m_d["author_name"])
        jieba.add_word(m_d["tip"])


def cut_musics_all_text_save(musics_data: dict, save_path):
    with open(save_path, "w", encoding="utf8") as f:
        for m_i, m_d in musics_data.items():
            words = jieba.cut(get_music_all_text(m_d))
            f.write(" ".join(words))
            f.write("\n")
            f.flush()


def load_model(musics_data):
    make_sure_exist("model")
    make_sure_exist("data/musics_text")

    model_path = "model/music_text_word2vec.model"
    if os.path.exists(model_path):
        model = word2vec.Word2Vec.load(model_path)
        return model.wv
    else:
        m_t_path = "data/musics_text/musics_text.txt"
        if not os.path.exists(m_t_path):
            cut_musics_all_text_save(musics_data, m_t_path)

        s = word2vec.Text8Corpus(m_t_path)
        model = word2vec.Word2Vec(s, sg=1, min_count=1, window=5, vector_size=150)
        model.save(model_path)
        return model.wv


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


def load_musics_key_words(musics_data):
    musics_key_words_path = "data/music_100_key_words.txt"
    if not os.path.exists(musics_key_words_path):
        for m_i, m_d in musics_data.items():
            music_key_words = get_music_text_key_words(m_d, 20)
            m_d["key_words"] = music_key_words

        with open(musics_key_words_path, "w", encoding="utf8") as f:
            f.write(str({m_i: m_d["key_words"] for m_i, m_d in musics_data.items()}))
    else:
        musics_key_words = read_data_from_file(musics_key_words_path)
        for m_i, m_d in musics_data.items():
            m_d["key_words"] = musics_key_words[m_i]


musics_data = read_data_from_file("data/music_100.txt")
print("musics data load successful")

add_jieba_lexicon(musics_data)

model = load_model(musics_data)
print("model load successful")

load_musics_key_words(musics_data)
print("musics' key words load successful")


"""API"""
DEFAULT_MAX_NUM = 15


# api
def recommend_musics_by_musics(musics_id: list, n=DEFAULT_MAX_NUM) -> list:
    """
    根据音乐列表产生推荐音乐列表（不会有一半以上重复）
    :param musics_id: 音乐id列表
    :param n: 最大音乐数量
    :return: 推荐音乐id列表
    """
    key_words = []
    for m_i in musics_id:
        key_words.extend(musics_data[m_i]["key_words"])
    tar_ms_i = cal_random_similar_musics_by_words(model, key_words, musics_data, n,
                                                  random.sample(musics_id, max(len(musics_id) - n // 2, 0)))
    tar_ms_i = [i[0] for i in tar_ms_i]
    return tar_ms_i


# api
def make_song_list_by_words(words: list, n=DEFAULT_MAX_NUM) -> tuple[str, str, list]:
    """
    根据描述的单词列表随机产生相符的歌单
    :param words: 描述的单词列表
    :param n: 最大音乐数量
    :return: 歌单结构（歌单名，歌单描述，歌单id列表）
    """
    musics_id = [i[0] for i in cal_random_similar_musics_by_words(model, words, musics_data, n)]
    songs_list_name = cal_songs_list_name_sample(musics_id, musics_data)
    return songs_list_name, "", musics_id


# api
def search_songs_by_words(words: list, n=DEFAULT_MAX_NUM) -> list:
    """
    根据描述的单词列表随机产生音乐列表
    :param words: 描述的单词列表
    :param n: 最大音乐数量
    :return: 搜索到的音乐id列表
    """
    return [i[0] for i in cal_random_similar_musics_by_words(model, words, musics_data, n)]


def main():
    pass


if __name__ == '__main__':
    main()
