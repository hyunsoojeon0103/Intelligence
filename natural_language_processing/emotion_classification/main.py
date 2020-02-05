import nltk
import numpy as np
import pandas as pd
import pickle
from sklearn.metrics import f1_score
from sklearn.preprocessing import LabelEncoder
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

import utils
import models

# Global definitions - data
DATA_FN = 'data/crowdflower_data.csv'
LABEL_NAMES = ["happiness", "worry", "neutral", "sadness"]

EMBEDDING_DIM = 100 
BATCH_SIZE = 128
NUM_CLASSES = 4
USE_CUDA = torch.cuda.is_available()  

FRESH_START = False 
TEMP_FILE = "temporary_data.pkl"  

def train_model(model, loss_fn, optimizer, train_generator, dev_generator):
    # loop through the entire traning data
    numOfEpoch = int(len(train_generator.sampler)/BATCH_SIZE)
    patient = 0.03 # to be used for early stopping
    best = np.inf
    for epoch in range(numOfEpoch):
        
        # change to train mode
        model.train()
        for data,target in train_generator:
            # if gpu avaialbe, switch
            if USE_CUDA:
                data = data.cuda()
                target = target.cuda()
            # must zero the gradients, or else they will accumulate
            optimizer.zero_grad() 
            output = model(data)
            loss = loss_fn(output,target)
            # backprop
            loss.backward()
            optimizer.step()
        
        devLoss = 0.0
        # switch to eval mode
        model.eval()
        with torch.no_grad():
            for data,target in dev_generator:
                output = model(data)
                loss = loss_fn(output,target)
                devLoss += loss.item() * data.size(0)
        
        devLoss = devLoss / len(dev_generator.sampler)
        print('Epoch: {}\tDevelopment Loss : {:6f}'.format(epoch+1,devLoss))

        if devLoss < best:
            best = devLoss
            torch.save(model,"best.pth")

        # if loss starts to increase, stop
        if devLoss > best + patient:
            print("Stopped improving...break")
            break
    out = torch.load("best.pth")
    return out
        
def test_model(model, loss_fn, test_generator):
    gold = []
    predicted = []

    # Keep track of the loss
    loss = torch.zeros(1)  # requires_grad = False by default; float32 by default
    if USE_CUDA:
        loss = loss.cuda()

    model.eval()

    # Iterate over batches in the test dataset
    with torch.no_grad():
        for X_b, y_b in test_generator:
            # Predict
            y_pred = model(X_b)

            gold.extend(y_b.cpu().detach().numpy())
            predicted.extend(y_pred.argmax(1).cpu().detach().numpy())

            loss += loss_fn(y_pred.double(), y_b.long()).data

    # Print total loss and macro F1 score
    print("Test loss: ")
    print(loss)
    print("F-score: ")
    print(f1_score(gold, predicted, average='macro'))

#extension-grading 
def trainForExt(model,loss_fn,optimizer,train_generator,dev_generator):
    epochs = 10
    # gradient clipping
    clip = 5 
    for epoch in range(epochs):
        
        h = model.init_hidden(128)
        model.train()
        for data,target in train_generator:
            if data.shape[0] != 128:
                continue
            # new variables for hidden state to
            # prevent backpropagating through
            # entire training history
            h = tuple([each.data for each in h])
            model.zero_grad()
            output,h = model(data,h)
            loss = loss_fn(output,target)
            loss.backward()
            # prevent exploding gradient problem in rnn
            nn.utils.clip_grad_norm_(model.parameters(),clip)
            optimizer.step()
        
        devLoss = 0.0
        model.eval()
        dh = model.init_hidden(128)
        with torch.no_grad():
            for data,target in dev_generator:
                if data.shape[0] != 128:
                    continue
                dh = tuple([each.data for each in dh])
                output,dh = model(data,dh)
                loss = loss_fn(output,target)
                devLoss += loss.item() * data.size(0)
        devLoss = devLoss / len(dev_generator.sampler)
        print('Epoch: {}\tDevelopment loss : {:6f}'.format(epoch+1,devLoss))

def main():
    if FRESH_START:
        print("Preprocessing all data from scratch....")
        train, dev, test = utils.get_data(DATA_FN)
        train_generator, dev_generator, test_generator, embeddings, train_data = utils.vectorize_data(train, dev, test,
                                                                                                BATCH_SIZE,
                                                                                                EMBEDDING_DIM)

        print("Saving DataLoaders and embeddings so you don't need to create them again; you can set FRESH_START to "
              "False to load them from file....")
        with open(TEMP_FILE, "wb+") as f:
            pickle.dump((train_generator, dev_generator, test_generator, embeddings, train_data), f)
    else:
        try:
            with open(TEMP_FILE, "rb") as f:
                print("Loading DataLoaders and embeddings from file....")
                train_generator, dev_generator, test_generator, embeddings, train_data = pickle.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("You need to have saved your data with FRESH_START=True once in order to load it!")
            

    #loss_fn = nn.CrossEntropyLoss()
   
    #denseNet = models.DenseNetwork(embeddings)
    #denseOpt = optim.SGD(denseNet.parameters(), lr = 0.01)
    #train_model(denseNet,loss_fn,denseOpt,train_generator,dev_generator)
    #denseNet = torch.load("dense.pth")
    #test_model(denseNet,loss_fn,test_generator)

    #rnn = models.RecurrentNetwork(embeddings)
    #rnnOpt = optim.SGD(rnn.parameters(),lr=0.05)
    #train_model(rnn,loss_fn,rnnOpt,train_generator,dev_generator)
    #rnn = torch.load("recurrent.pth")
    #test_model(rnn,loss_fn,test_generator)
   
if __name__ == '__main__':
    main()
