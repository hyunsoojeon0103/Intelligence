import sys
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB,GaussianNB
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC,LinearSVC
from sklearn.model_selection import KFold
from sklearn.pipeline import FeatureUnion
from sklearn.feature_selection import SelectKBest,chi2
from sklearn.metrics import f1_score
# 
def NaiveBayes(data,topic,folds = 5):
    
    print("\"" + topic + "\"")
    
    trainX = data['author'].to_numpy() # extract feature
    trainY = data['label'].to_numpy()
    
    clf = MultinomialNB() 
    kf = KFold(n_splits=folds,shuffle=True) # 5 fold cross validation
    vectorizer = CountVectorizer(binary=True,ngram_range=(1,3)) # (1,3) gram used with default settings
    
    i = 1
    resAvg = 0.0
    resFscore = 0.0
    for trainIdx, testIdx in kf.split(trainX): 
        
        accuracy = 0.0
        
        trX,tsX = trainX[trainIdx],trainX[testIdx]
        trY,tsY = trainY[trainIdx],trainY[testIdx]

        trX = vectorizer.fit_transform(trX)
        tsX = vectorizer.transform(tsX)

        clf.fit(trX, trY)
                                
        pred = clf.predict(tsX)
        accuracy = accuracy_score(tsY,pred) * 100
        # top 20 features
        kBest = SelectKBest(chi2,k=20).fit(trX,trY)
        kCols = kBest.get_support(indices=True) # get indices of the features
        
        print("Top 20 features")
        print(trainX[kCols]) # display to the screen
        
        resFscore+=f1_score(tsY,pred,average='binary',pos_label='pro') # f1 score for performance review
        resAvg += accuracy
        
        i+=1

    print("Avg F1-score of 5-fold cross validation:\t{:6f}\nAvg accuracy of 5-fold cross validation:\t{:6f}%\n"
    .format(resFscore/folds,resAvg/folds))        
if __name__ == "__main__":
    
    if len(sys.argv) == 3 and sys.argv[1] == "train-data.csv" and (sys.argv[2] == "abortion" or sys.argv[2] == "gay rights"):
        data = pd.read_csv(sys.argv[1])
        if sys.argv[1] == "abortion":
            abortion = data[data['topic'] == 'abortion']
            NaiveBayes(abortion,sys.argv[2])
        else:
            gayRight = data[data['topic'] == 'gay rights']
            NaiveBayes(gayRight,sys.argv[2])
    else:
        print("usage:python3 classify.py train-data.csv abortion | \"gay rights\"")
