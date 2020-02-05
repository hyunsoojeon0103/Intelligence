
import nltk
from nltk.corpus import brown
from nltk.tokenize import casual

import json

from gensim.models import KeyedVectors
from gensim.test.utils import datapath
import numpy as np
import gensim
from collections import Counter
import string
import scipy.sparse
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix, lil_matrix, save_npz

# global variable to be used to remove puncuations from text
puncs = dict((ord(char),None) for char in string.punctuation)
windowSize = [2,5,10]
dimension = [100,300,1000]
negativeSp = [1,5,15]
idx = 1
def load_msr(f, limit=None):
    lines = [x.strip().lower().split('\t') for x in open(f, 'r').readlines()[1:]]
    sents = [[x[3].split(), x[4].split()] for x in lines]
    labels = [int(x[0]) for x in lines]
    return sents, labels

def load_w2v(f):
    return KeyedVectors.load_word2vec_format(f, binary=f.endswith('.bin'))

def load_kv(f):
    return KeyedVectors.load(f)

def load_txt(f):
    vectors = {}
    
    for line in open(f, 'r').readlines():
        splits = line.strip().split()
        vectors[splits[0]] = np.array([float(x) for x in splits[1:]])

    return vectors

def load_model(f):
    if f.endswith('.bin'): return load_w2v(f)
    elif f.endswith('.txt'): return load_txt(f)
    else: return load_kv(f)

# count the number of occurences of each word
def singleCount(fileName):
    with open(fileName) as file:
        ctr = Counter()
        data = file.readlines()
        for line in data:
            # split each sentence by space, lowercase
            # remove words that less than 3 characters
            # remove new line
            line = line.lower().split(" ")
            line = [s.strip('\n').translate(puncs) for s in line if len(s) >= 3]
            ctr.update(line)
    return ctr
# a function that counts the number of occurences given a window size
def windowCount(fileName, window):
    with open(fileName) as file:
        ctr = Counter()
        data = file.readlines()
        for line in data:
            # split each sentence by space, lowercase
            # remove words that less than 3 characters
            # remove new line
            line = line.lower().split(" ")
            line = [s.strip("\n").translate(puncs) for s in line if len(s) >= 3]
            lst = []
            for i in range(len(line)):
                for j in range(window):
                    if i + j + 1 < len(line):
                        lst.append((line[i],line[i+j+1]))
            ctr.update(lst)
    return ctr

# returns sparse matrix 
def ppmi(coCount):
    # get the total count
    totalCtr = float(coCount.sum())
    # get the sum of each row
    rowSum = np.array(coCount.sum(axis=1),dtype=np.float64).flatten()
    # get indices of nonzeros
    ii,jj = coCount.nonzero()
    cij = np.array(coCount[ii,jj],dtype=np.float64).flatten()
    pmi = np.log(cij * totalCtr / rowSum[ii] * rowSum[jj])
    # get the positive only
    ppmi = np.maximum(0,pmi)
    res = scipy.sparse.csc_matrix((ppmi,(ii,jj)), shape=coCount.shape,dtype=np.float64)
    # eliminate zero
    res.eliminate_zeros()
    return res
# return [m,d] matrix
def SVD(X, d=2):
    transformer = TruncatedSVD(n_components=d, random_state=0)
    # normalize
    Wv = transformer.fit_transform(X)
    Wv = Wv/np.linalg.norm(Wv,axis=1).reshape([-1,1])
    print("computeed embeddings:{}".format(Wv.shape))
    return Wv

# a function that writes a word and embeddings into a txt file
def writeToTxt(fileName,voc,embed):
    with open(fileName,"w") as file:
        for i in range(len(voc)):
            if len(voc[i]) <= 1:
                continue
            file.write(voc[i])
            for e in embed[i]:
                file.write(" ")
                file.write(str(e))
            file.write('\n')

if __name__ == "__main__":
#    # create 27 models for word2vec
#    for i in windowSize:
#        for j in dimension:
#            for k in negativeSp:
#                print("model {} with windowSize = {} dimension = {} negativeSp = {}".format(idx,i,j,k))
#                model = gensim.models.Word2Vec(corpus_file="data/brown.txt",window=i,size=j,sg=1,negative=k)
#                filePath = "./save/" + str(i) + "_" + str(j) + "_" + str(k)
#                model.wv.save(filePath)
#                idx +=1
    
    # create 9 models using SVD
    fileName = "./data/brown.txt"
    wordCtr = singleCount(fileName)
    for window in windowSize:
        pairCtr = windowCount(fileName,window)
        vocab = list(zip(*pairCtr.keys()))
        vocab = list(set(vocab[0]).union(set(vocab[1])))
        w2i = {vocab[i]: i for i in range(len(vocab))}
        coCount = lil_matrix((len(vocab),len(vocab)))
        for p,c in pairCtr.items():
            coCount[w2i[p[0]], w2i[p[1]]] = c
        coCount = (coCount + coCount.T).tocsr()
        wordCount = [wordCtr[vocab[i]] for i in range(len(vocab))]
        myPpmi = ppmi(coCount)
        for dim in dimension:
            embeddings = SVD(myPpmi, d= dim)
            output = "./save/SVD_" + str(window) + "_" + str(dim) + ".txt"
            writeToTxt(output,vocab,embeddings)
