# -*- coding:utf-8 -*-
# Date: 2019/7/18 14:26
# Author: xuxiaoping
# Desc: Text Prepare Utils

import os
import re
import struct

HTTP_LINK_PATTERN = r'[-a-zA-Z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)'

here = os.path.dirname(os.path.abspath(__file__))


def remove_http_link(sentence):
    return re.sub(HTTP_LINK_PATTERN, '', sentence)


def clean_sentence(sentence):
    """Clean sentence

    if sentence is chinese, do participle first.


    Args:
        sentence (str): input sentence

    Returns:
        A Generate of word_list


    Example:
    ```
        import jieba
        sentence = "如果是中文，先做分词"
        sentence = ' '.join(jieba.cut(sentence))
        word_list = clean_sentence(sentence)
    ```

    """
    sentence = re.sub(r'[^\w ]', ' ', sentence)

    sentence = sentence.lower()

    word_list = sentence.split(' ')

    word_list = filter(None, word_list)

    return word_list


class CovertT2S:
    """Covert Traditional to Simplified"""

    def __init__(self, t2s_map_file_path=None):
        if not t2s_map_file_path:
            t2s_map_file_path = os.path.join(here, 't2s.dat')

        self.t2s_map = {}
        self.set_t2s_map(t2s_map_file_path)
        self.mychr = lambda s: chr(s)

    def set_t2s_map(self, t2s_map_file_path):

        with open(t2s_map_file_path, 'rb') as fp:
            dat_size = int(os.path.getsize(t2s_map_file_path) / 8)
            temp_bytes = fp.read(4 * dat_size)
            tra = struct.unpack("<" + str(dat_size) + "i", temp_bytes)
            temp_bytes = fp.read(4 * dat_size)
            sim = struct.unpack("<" + str(dat_size) + "i", temp_bytes)
            for i in range(dat_size):
                self.t2s_map[tra[i]] = sim[i]

    def get_t2s(self, c):
        if ord(c) in self.t2s_map:
            return self.mychr(self.t2s_map[ord(c)])
        else:
            return c

    def T2S(self, sentence):
        """Traditional to Simplified"""
        new_sentence = ""
        for w in sentence:
            new_sentence += self.get_t2s(w)
        return new_sentence
