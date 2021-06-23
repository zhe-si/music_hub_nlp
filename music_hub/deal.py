import re

import jieba
import jieba.analyse
import paddle

from music_hub.data import read_data_from_file


def test():
    paddle.enable_static()
    jieba.enable_paddle()  # 启动paddle模式。 0.40版之后开始支持，早期版本不支持
    # strs = ["我来到北京清华大学", "他来到了网易杭研大厦", "乒乓球拍卖完了", "中国科学技术大学"]
    # for str in strs:
    #     seg_list = jieba.cut(str, use_paddle=True)  # 使用paddle模式
    #     print("Paddle Mode: " + '/'.join(list(seg_list)))
    #
    #     seg_list = jieba.cut(str)  # 默认是精确模式
    #     print("default: " + "/".join(seg_list))
    data = "素胚勾勒出青花笔锋浓转淡,瓶身描绘的牡丹一如你初妆,冉冉檀香透过窗心事我了然,宣纸上走笔至此搁一半"
    seg_list = jieba.cut(data, use_paddle=True)  # 使用paddle模式
    print("Paddle Mode: " + '/'.join(list(seg_list)))

    seg_list = jieba.cut(data)  # 默认是精确模式
    print("default: " + "/".join(seg_list))


def test2():
    data = "素胚勾勒出青花笔锋浓转淡,瓶身描绘的牡丹一如你初妆,冉冉檀香透过窗心事我了然,宣纸上走笔至此搁一半"

    seg_list_p = jieba.cut(data, use_paddle=True)  # 使用paddle模式

    seg_list = jieba.cut(data)  # 默认是精确模式

    k_words = jieba.analyse.extract_tags(data, topK=5)
    print(k_words)

    k_words = jieba.analyse.extract_tags(" ".join(seg_list_p), topK=5)
    print(k_words)

    k_words = jieba.analyse.extract_tags(" ".join(seg_list), topK=5)
    print(k_words)


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
    return "\n".join([music_data["name"], get_lrc_zh(music_data)])


def get_key_words(text: str, n):
    k_words = jieba.analyse.extract_tags(text, topK=min(n, len(text) // 4), withWeight=True)
    return k_words


def get_music_text_key_words(music_data: dict, n):
    music_text = get_music_text(music_data)
    author_name = music_data["author_name"]
    music_tip = music_data["欧美"]

    key_words = get_key_words(music_text, n - 2)
    key_words.append(author_name)
    key_words.append(music_tip)

    return key_words


def main():
    musics_data = read_data_from_file("data/temp/tt.txt")

    music_id = list(musics_data.keys())[0]
    music_data = musics_data[music_id]
    music_key_words = get_music_text_key_words(music_data, 20)
    print(music_key_words)


if __name__ == '__main__':
    # test2()
    main()
    # test()
