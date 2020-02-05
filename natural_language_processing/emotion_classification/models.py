import torch
import torch.nn as nn
import torch.nn.utils.rnn as rnn

class DenseNetwork(nn.Module):
    def __init__(self,embeddings):
        super(DenseNetwork, self).__init__()
        self.embedding = nn.Embedding.from_pretrained(embeddings,freeze=False)
        # embedding dimension must be 100
        self.fc1 = nn.Linear(100,128)
        # final output size 4
        self.fc2 = nn.Linear(128,4)
        self.dropout = nn.Dropout(0.4)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.embedding(x)
        # take the sum of the embeddings
        x = torch.sum(x,dim=1)
        x = self.fc1(x.float())
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x

class RecurrentNetwork(nn.Module):
    def __init__(self,embeddings):
        super(RecurrentNetwork, self).__init__()
        self.embedding = nn.Embedding.from_pretrained(embeddings,freeze=False)
        self.lstm = nn.LSTM(100,128,2,dropout=0.5,batch_first=True)
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(256,4)

    def forward(self, x):
        # get the lengths of sentences for pack_padded_sequence 
        lengths = list() 
        for each in x:
            append = False
            # traver in reverse order to find the last non-zero
            for i in range(x.shape[1]-1,0,-1):
                if each[i] != 0:
                    append = True
                    lengths.append(i+1)
                    break
            # if append is false, then it was an empty sentence
            if append == False:
                lengths.append(1)
        x = self.embedding(x)
        x = self.dropout(x)
        x = nn.utils.rnn.pack_padded_sequence(x,lengths,
                                        batch_first=True,enforce_sorted=False)
        x,(h,cell) = self.lstm(x.float())
        x,lengths = nn.utils.rnn.pad_packed_sequence(x)
        # get the final hidden state
        h = torch.cat((h[-2,:,:],h[-1,:,:]),dim =1)
        h = self.dropout(h)
        # project it to a vector of size 4
        out = self.fc(h)
        return out

class RnnExtension(nn.Module):
    def __init__(self,embeddings):
        super(RnnExtension,self).__init__()
        self.embedding = nn.Embedding.from_pretrained(embeddings,freeze=False)
        self.lstm=nn.LSTM(100,256,2,dropout=0.5,batch_first=True)
        self.dropout=nn.Dropout(0.3)
        self.fc=nn.Linear(256,4)
    
    def forward(self,x,hidden):
        batchSize = x.size(0)
        embeds = self.embedding(x)
        # pass the embeds along with hidden states that remember info
        lstmOut, hidden = self.lstm(embeds.float(),hidden)
        out = self.dropout(lstmOut)
        out = self.fc(out)
        # get last batch 
        out = out[:,-1]
        return out,hidden

    def init_hidden(self,batchSize):
        # create two tensors initalized to 0
        # for hidden state and cell state of LSTM
        weight = next(self.parameters()).data.float()
        hidden = (weight.new(2,batchSize,256).zero_(),
                    weight.new(2,batchSize,256).zero_())
        return hidden
#extension-grading
class DenseExtension(nn.Module):
    def __init__(self,embeddings):
        super(DenseExtension,self).__init__()
        # pre-trained embeddings
        self.embedding = nn.Embedding.from_pretrained(embeddings,freeze=False)
        # 5-layerd neural network
        self.fc1 = nn.Linear(100,256)
        self.fc2 = nn.Linear(256,128)
        self.fc3 = nn.Linear(128,64)
        self.fc4 = nn.Linear(64,32)
        # there are 4 labels, so output size is 4
        self.fc5 = nn.Linear(32,4)
        self.dropout = nn.Dropout(0.4)
        # activation function
        self.relu = nn.ReLU()
    
    def forward(self,x):
        x = self.embedding(x)
        x = self.dropout(x)
        x = torch.sum(x,dim=1)
        # feed it through hidden layers
        x = self.fc1(x.float())
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc3(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc4(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc5(x)
        return x

















