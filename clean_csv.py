
from text_utils import clean_sentence
import pandas as pd

CSV_FILE_PATH = '/Users/piguanghua/Downloads/material_new.csv'
df = pd.read_csv(CSV_FILE_PATH, header=None)

source_file = "/Users/piguanghua/Downloads/material_new.text"

i = 1
with open(source_file, "w") as fout:
    for ele in df[0]:

        try:
            sentence = clean_sentence(ele)
        except TypeError as e:
            continue

        sentence = clean_sentence(ele)

        if i == 76:
            print()

        if len(sentence) != 2:
            continue

        if len(sentence[0]) > 35 or len(sentence[1]) > 35:
            continue

        if len(sentence[0].strip()) <= 1 or len(sentence[1].strip()) <= 1:
            continue

        #fout.write(sentence)
        sentence = list(sentence)
        sentence[1] = sentence[1] + "\n"
        sentence = "\t".join(sentence)
        fout.write(sentence)

        i += 1


