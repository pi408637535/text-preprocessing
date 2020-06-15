import codecs
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

#chinese text最大字符编码:GB18030
def convert_files_encoding(src_parent_path, target_parent_path,
                           src_encoding='GB18030', target_encoding="utf-8", error="ignore",
                           filename_suffix=''):
    with codecs.open(src_parent_path, 'r', src_encoding, errors=error) as fin, \
            open(target_parent_path, "w", encoding=target_encoding) as fout:
        for line in fin:
            fout.write(line)

if __name__ == '__main__':
    src_parent_path = "/Users/piguanghua/Downloads/nCoV_900k_train.unlabled.csv"
    target_parent_path = "/Users/piguanghua/Downloads/nCoV_100k_train1.labled.csv"
    #convert_files_encoding(src_parent_path, target_parent_path)


    df = pd.read_csv(target_parent_path, encoding='utf-8')




    df = df[["微博id","微博中文内容"]]
    train_sentences = []
    train_labels = []
    df["情感倾向"] = np.zeros_like(df[["微博中文内容"]])
    for lidx, line in enumerate(df["微博中文内容"].tolist()):
        label, text = df["情感倾向"][lidx], line
        # print(int(label))
        try:
            int(label)
        except ValueError as err:
            label
            continue
        label = int(label)
        train_labels.append(label)
        train_sentences.append(text)
    print(len(train_labels))

