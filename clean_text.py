# -*- coding: utf-8 -*-
# @Time    : 2020/6/15 17:01
# @Author  : piguanghua
# @FileName: clean_text.py
# @Software: PyCharm

import pandas as pd
import text_utils
from text_utils import clean_sentence


if __name__ == '__main__':

    target_path = "/Users/piguanghua/Downloads/chat_source.txt"
    source_file = "/Users/piguanghua/Downloads/material_new1.text"

    with open(target_path) as fin, open(source_file, "w") as fout:
        for ele in fin:
            try:
                sentence = clean_sentence(ele)
            except TypeError as e:
                continue

            sentence = clean_sentence(ele)

            if len(sentence) < 2:
                continue

            if len(sentence[0]) > 35 or len(sentence[1]) > 35:
                continue

            if len(sentence[0].strip()) <= 1 or len(sentence[1].strip()) <= 1:
                continue

            # fout.write(sentence)
            sentence = list(sentence)
            sentence[1] = sentence[1] + "\n"
            sentence = "\t".join(sentence)
            fout.write(sentence)
