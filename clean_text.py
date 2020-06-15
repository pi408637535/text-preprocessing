# -*- coding: utf-8 -*-
# @Time    : 2020/6/15 17:01
# @Author  : piguanghua
# @FileName: clean_text.py
# @Software: PyCharm

import pandas as pd
import text_utils



if __name__ == '__main__':
    path = "/Users/piguanghua/Downloads/train.csv"
    df = pd.read_csv(path)
    train_labels = df['label'].tolist()
    train_sentences = df['review'].tolist()
    save_path = "/Users/piguanghua/Downloads/train.txt"
    with open(save_path, 'w', encoding='utf-8') as fout:
        for idx, word in enumerate(train_sentences):
            fout.write('{1}\t{0}\n'.format(train_labels[idx], word))


