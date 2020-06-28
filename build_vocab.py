import re
import jieba
from collections import Counter
import pandas as pd
from gensim.models.keyedvectors import KeyedVectors
import torch
import torch.nn as nn
import pickle as pkl
from gensim.test.utils import common_texts
from gensim.models import Word2Vec

regex = re.compile(r'[^\u4e00-\u9fa5aA-Za-z0-9]')
import spacy
spacy_en = spacy.load('en')

def tokenizer(text): # create a tokenizer function
    # 返回 a list of <class 'spacy.tokens.token.Token'>
    return [tok.text for tok in spacy_en.tokenizer(text)]


def word_cut(text):
    text = regex.sub(' ', text)
    return [word for word in jieba.cut(text) if word.strip()]

def save_text(save_path, sentences, label):
    i = 0
    with open(save_path, 'w', encoding='utf-8') as fout:
        for idx, word in enumerate(sentences):
            # print(idx, word)
            fout.write('{0}\t{1}\n'.format(label[idx], word))
            # print('{0}\t{1}\n'.format(label[idx], word))



import codecs
import numpy as np
import dill
from torchtext import data

if __name__ == '__main__':


    #pkl.dump(word2idx, open(vocab_dir, 'wb'))

    glove_path = "/Users/piguanghua/Downloads/glove.42B.300d.txt"



    path = "/Users/piguanghua/Downloads/sen_text.txt"
    #save_text(path, train_sentences, train_labels)
    #save_vocab("/Users/piguanghua/Downloads/vocab.txt")

    weight = torch.zeros(10, 300)
    word_to_idx = {",":1,'a':2,'b':3,'c':4,'d':7, "e":9}


    with codecs.open(glove_path) as fin:
        for index,line in enumerate(fin):
            word_index = len(line.split(" ")) - 300

            str_index = word_to_idx[line.split(" ")[:len(line.split(" ")) - 300][0]]
            data = line.split(" ")[str_index:]
            vector = np.array(  list( map(lambda x: float(x), data ) )   )
            weight[index, :] = torch.from_numpy( vector )

    embedding = nn.Embedding.from_pretrained(weight)
    filename_trimmed_dir = "/Users/piguanghua/Downloads/embed"
    np.savez_compressed(filename_trimmed_dir, embeddings=embedding)


