import os


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

    def add_items(self, items):
        for item in items:
            self.add_item(item)

    def get_list(self):
        return self._n_list.copy()

    def clear_list(self):
        self._n_list.clear()


def get_not_none(data_dict, key):
    v = data_dict[key]
    if v is None:
        return ""
    else:
        return v


def make_sure_exist(path):
    if not os.path.exists(path):
        os.makedirs(path)
