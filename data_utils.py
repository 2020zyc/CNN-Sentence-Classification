import numpy as np
import os
import re
from math import ceil

def clean_string(string_list):
    ret_list = []
    for string in string_list:
        string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
        string = re.sub(r"\'s", " \'s", string)
        string = re.sub(r"\'ve", " \'ve", string)
        string = re.sub(r"n\'t", " n\'t", string)
        string = re.sub(r"\'re", " \'re", string)
        string = re.sub(r"\'d", " \'d", string)
        string = re.sub(r"\'ll", " \'ll", string)
        string = re.sub(r",", " , ", string)
        string = re.sub(r"!", " ! ", string)
        string = re.sub(r"\(", " \( ", string)
        string = re.sub(r"\)", " \) ", string)
        string = re.sub(r"\?", " \? ", string)
        string = re.sub(r"\s{2,}", " ", string)
        string = re.sub(r"[\.,-]", "", string)
        ret_list.append(string)
    return ret_list


def build_word_index(string_list):
    string_list = clean_string(string_list)
    word2idx = {}
    for line in string_list:
        for word in line.split():
            if not word in word2idx:
                word2idx[word] = len(word2idx) + 1
    return word2idx


def tokenizer(string_list, padding, word2idx):
    string_list = clean_string(string_list)
    tokenized = []
    for line in string_list:
        tokenized_line = []
        for word in line.split():
            tokenized_line.append(word2idx[word])
        k = padding - len(tokenized_line)
        tokenized_line += [0] * k
        tokenized.append(tokenized_line)
    return np.asarray(tokenized)


def get_data(paths):
    PATH_POS = paths[0]
    PATH_NEG = paths[1]
    with open(PATH_NEG) as f:
        neg_texts = f.read().splitlines()
    with open(PATH_POS) as f:
        pos_texts = f.read().splitlines()

    word2idx = build_word_index(string_list=(
        clean_string(pos_texts) + clean_string(neg_texts)))
    t_pos = tokenizer(pos_texts, 54, word2idx)
    t_neg = tokenizer(neg_texts, 54, word2idx)

    pos_labels = np.ones([t_pos.shape[0],], dtype='int32')
    neg_labels = np.zeros([t_neg.shape[0], ], dtype='int32')
    data = np.concatenate((t_pos, t_neg))
    labels = np.concatenate((pos_labels, neg_labels))
    return data, labels, word2idx

def generate_split(data, labels, val_split):
    j = np.concatenate((data, labels.reshape([-1, 1])), 1)
    np.random.shuffle(j)
    split_point = int(ceil(data.shape[0]*(1-val_split)))
    train_data = j[:split_point,:-1]
    val_data = j[split_point:,:-1]
    train_labels = j[:split_point,-1]
    val_labels = j[split_point:, -1]
    return train_data, train_labels, val_data, val_labels

def generate_batch(data, labels, batch_size):
    j = np.concatenate((data, labels.reshape([-1, 1])), 1)
    mark = np.random.randint(batch_size, j.shape[0])
    batch_data = j[mark-batch_size : mark]
    return batch_data[:,:-1], batch_data[:,-1]