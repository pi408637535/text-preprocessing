import re
import jieba
from collections import Counter
import pandas as pd
from gensim.models.keyedvectors import KeyedVectors
import torch
import torch.nn as nn
import pickle as pkl

regex = re.compile(r'[^\u4e00-\u9fa5aA-Za-z0-9]')


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


def save_vocab(save_path):
    with open(save_path, 'w', encoding='utf-8') as fout:
        for idx, word in enumerate(words):
            fout.write('{}\t{}\n'.format(word, idx))
            # print('{}\t{}\n'.format(word, idx))


import numpy as np

if __name__ == '__main__':
    path = "/Users/piguanghua/data/sentiment_2/car/train.tsv"
    df = pd.read_csv(path, sep='\t')
    vocab_dir = "/Users/piguanghua/Downloads/vocab.pkl"

    train_labels = df['label'].tolist()
    train_sentences = df['text'].tolist()

    for i in range(len(train_sentences)):
        train_sentences[i] =  " ".join(word_cut(train_sentences[i]))

    # make word counter
    num_train = len(train_sentences)
    factor = 20000

    words = Counter()  # Dictionary that will map a word to the number of times it appeared in all the training sentences
    for i, sentence in enumerate(train_sentences):
        if len(sentence) < 1:
            continue
        # The sentences will be stored as a list of words/tokens

        for word in sentence.split(" "):  # Tokenizing the words
            words.update([word.lower()])  # Converting all the words to lowercase
        if i % 20000 == 0:
            print(str((i * 100) / num_train) + "% done")
    print("100% done")

    words = {k: v for k, v in words.items() if v > 10}
    words = sorted(words, key=words.get, reverse=True)
    words = ['PAD', 'UNK'] + words
    word2idx = {o: i for i, o in enumerate(words)}
    idx2word = {i: o for i, o in enumerate(words)}

    #pkl.dump(word2idx, open(vocab_dir, 'wb'))

    path = "/Users/piguanghua/Downloads/sgns.weibo.word"
    wvmodel = KeyedVectors.load_word2vec_format(path, binary=False, unicode_errors='ignore')
    vocab_size = len(words) + 1
    embed_size = 300
    weight = torch.zeros(vocab_size, embed_size)


    path = "/Users/piguanghua/Downloads/sen_text.txt"
    #save_text(path, train_sentences, train_labels)
    #save_vocab("/Users/piguanghua/Downloads/vocab.txt")

    word_to_idx = word2idx
    idx_to_word = idx2word

    for i in range(len(wvmodel.index2word)):
        try:
            index = word_to_idx[wvmodel.index2word[i]]
        except:
            continue
        weight[index, :] = torch.from_numpy(wvmodel.get_vector(
            idx_to_word[word_to_idx[wvmodel.index2word[i]]]))

    embedding = nn.Embedding.from_pretrained(weight)
    filename_trimmed_dir = "/Users/piguanghua/Downloads/embed"
    np.savez_compressed(filename_trimmed_dir, embeddings=embedding)