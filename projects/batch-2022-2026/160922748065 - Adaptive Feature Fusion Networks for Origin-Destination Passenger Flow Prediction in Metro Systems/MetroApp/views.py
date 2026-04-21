from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from math import sqrt
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import Dropout
from keras.layers import MaxPooling2D
from keras.layers import Flatten, Bidirectional, GRU, RepeatVector, LSTM
from keras.layers import Convolution2D
from keras.models import Sequential
from keras.callbacks import ModelCheckpoint
import os

global uname
global X_train, X_test, y_train, y_test, X, Y, dataset
rmse, maps = [], []
global test_data, predict_data

dataset = pd.read_csv('Dataset/passenger_flow.csv', nrows=5000)
Y = dataset['passenger_flow'].ravel()
dataset.drop(['date_time','is_holiday','passenger_flow'], axis = 1,inplace=True)

#dataset processing like converting non-numeric data to numeric data
label_encoder = []
columns = dataset.columns
types = dataset.dtypes.values
for i in range(len(types)):
    name = types[i]
    if name == 'object': #finding column with object type
        le = LabelEncoder()
        dataset[columns[i]] = pd.Series(le.fit_transform(dataset[columns[i]].astype(str)))#encode all str columns to numeric
        label_encoder.append([columns[i], le])
dataset.fillna(0, inplace = True)
X = dataset.values
Y = Y.reshape(-1, 1)
#normalizing training features and labels
scaler = MinMaxScaler(feature_range = (0, 1))
scaler1 = MinMaxScaler(feature_range = (0, 1))
X = scaler.fit_transform(X)#normalize train features
Y = scaler1.fit_transform(Y)

X = np.reshape(X, (X.shape[0], X.shape[1], 1, 1))

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size = 0.2)

#function to calculate accuracy and prediction sales graph
def calculateMetrics(algorithm, predict, test_labels):
    rmse_value = sqrt(mean_squared_error(test_labels, predict))
    map_value = mean_absolute_error(np.asarray(test_labels), np.asarray(predict))
    rmse.append(rmse_value)
    maps.append(map_value)
    predict = predict.reshape(-1, 1)
    predict = scaler1.inverse_transform(predict)
    test_label = scaler1.inverse_transform(test_labels)
    predict = predict.ravel()
    test_label = test_label.ravel()    
    predict = predict[0:200]
    test_label = test_label[0:200]
    plt.figure(figsize=(5,3))
    plt.plot(test_label, color = 'red', label = 'True Passenger Flow')
    plt.plot(predict, color = 'green', label = 'Predicted Passenger Flow')
    plt.title(algorithm+' Origin Destination Passenger Flow Graph')
    plt.xlabel('Test Data')
    plt.ylabel('Predicted Passenger Flow')
    plt.legend()
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    img_b64 = base64.b64encode(buf.getvalue()).decode()
    return img_b64, test_label, predict

def Graphs(request):
    if request.method == 'GET':
        global rmse, maps, test_data, predict_data
        output='<table border=1 align=center width=100%><tr><th><font size="" color="black">Test Data Passenger Flow</th><th><font size="" color="black">Extension Predicted Passenger Flow</th></tr>'
        for i in range(0, 30):
            output+='<td><font size="" color="black">'+str(test_data[i])+'</td><td><font size="" color="black">'+str(predict_data[i])+'</td></tr>'
        output+= "</table></br>"
        df = pd.DataFrame([['Existing MLP','RMSE',rmse[0]],['Existing MLP','MAP',maps[0]],
                           ['Propose AFFN (EMGC-GRU)','RMSE',rmse[1]],['Propose AFFN (EMGC-GRU)','MAP',maps[1]],
                           ['Extension AFFN ((EMGC-LSTM)','RMSE',rmse[2]],['Extension AFFN ((EMGC-LSTM)','MAP',maps[2]],                           
                          ],columns=['Algorithms','Metrics','Value'])
        df.pivot_table(index="Algorithms", columns="Metrics", values="Value").plot(kind='bar', figsize=(8, 4))
        plt.title("All Algorithms RMSE & MAP Performance Graph")
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        img_b64 = base64.b64encode(buf.getvalue()).decode()    
        context= {'data':output, 'img': img_b64}
        return render(request, 'ViewResult.html', context)

def TrainAFFN(request):
    if request.method == 'GET':
        global rmse, maps, X, Y
        global X_train, X_test, y_train, y_test
        affn_model = Sequential()
        affn_model.add(Convolution2D(32, (1 , 1), input_shape = (X_train.shape[1], X_train.shape[2], X_train.shape[3]), activation = 'relu'))
        affn_model.add(MaxPooling2D(pool_size = (1, 1)))
        affn_model.add(Convolution2D(32, (1, 1), activation = 'relu'))
        affn_model.add(MaxPooling2D(pool_size = (1, 1)))
        affn_model.add(Flatten())
        affn_model.add(RepeatVector(2))
        #adding bidirectional + GRU to CNN layer
        affn_model.add(Bidirectional(GRU(32, activation = 'relu')))
        affn_model.add(Dense(units = 256, activation = 'relu'))
        affn_model.add(Dense(units = 1))
        affn_model.compile(optimizer = 'adam', loss = 'mean_squared_error')
        if os.path.exists("model/affn_weights.hdf5") == False:
            model_check_point = ModelCheckpoint(filepath='model/affn_weights.hdf5', verbose = 1, save_best_only = True)
            affn_model.fit(X_train, y_train, batch_size = 8, epochs = 50, validation_data=(X_test, y_test), callbacks=[model_check_point], verbose=1)
        else:
            affn_model.load_weights("model/affn_weights.hdf5")
        predict = affn_model.predict(X_test) 
        img_b64,test_label, predict = calculateMetrics("Propose AFFN (EMGC-GRU)", predict, y_test)#call function to calculate prediction accuracy
        output='<table border=1 align=center width=100%><tr><th><font size="" color="black">Algorithm Name</th><th><font size="" color="black">RMSE</th><th><font size="" color="black">MAP</th>'
        output+='</tr>'
        algorithms = ['Existing MLP', 'Propose AFFN (EMGC-GRU)']
        for i in range(len(algorithms)):
            output+='<td><font size="" color="black">'+algorithms[i]+'</td><td><font size="" color="black">'+str(rmse[i])+'</td><td><font size="" color="black">'+str(maps[i])+'</td></tr>'
        output+= "</table></br>"
        context= {'data':output, 'img': img_b64}
        return render(request, 'ViewResult.html', context)

def TrainLSTM(request):
    if request.method == 'GET':
        global rmse, maps, X, Y
        global X_train, X_test, y_train, y_test, test_data, predict_data
        extension_model = Sequential()
        extension_model.add(Convolution2D(32, (1 , 1), input_shape = (X_train.shape[1], X_train.shape[2], X_train.shape[3]), activation = 'relu'))
        extension_model.add(MaxPooling2D(pool_size = (1, 1)))
        extension_model.add(Convolution2D(32, (1, 1), activation = 'relu'))
        extension_model.add(MaxPooling2D(pool_size = (1, 1)))
        extension_model.add(Flatten())
        extension_model.add(RepeatVector(2))
        #adding bidirectional + GRU to CNN layer
        extension_model.add(LSTM(64, activation = 'relu'))
        extension_model.add(Dense(units = 256, activation = 'relu'))
        extension_model.add(Dense(units = 1))
        extension_model.compile(optimizer = 'adam', loss = 'mean_squared_error')
        if os.path.exists("model/extension_weights.hdf5") == False:
            model_check_point = ModelCheckpoint(filepath='model/extension_weights.hdf5', verbose = 1, save_best_only = True)
            extension_model.fit(X_train, y_train, batch_size = 8, epochs = 50, validation_data=(X_test, y_test), callbacks=[model_check_point], verbose=1)
        else:
            extension_model.load_weights("model/extension_weights.hdf5")
        predict = extension_model.predict(X_test) 
        img_b64,test_data, predict_data = calculateMetrics("Extension CNN2D", predict, y_test)#call function to calculate prediction accuracy
        print(rmse)
        print(maps)
        output='<table border=1 align=center width=100%><tr><th><font size="" color="black">Algorithm Name</th><th><font size="" color="black">RMSE</th><th><font size="" color="black">MAP</th>'
        output+='</tr>'
        algorithms = ['Existing MLP', 'Propose AFFN (EMGC-GRU)', 'Extension AFFN (EMGC-LSTM)']
        for i in range(len(algorithms)):
            output+='<td><font size="" color="black">'+algorithms[i]+'</td><td><font size="" color="black">'+str(rmse[i])+'</td><td><font size="" color="black">'+str(maps[i])+'</td></tr>'
        output+= "</table></br>"
        context= {'data':output, 'img': img_b64}
        return render(request, 'ViewResult.html', context)


def TrainMLP(request):
    if request.method == 'GET':
        global rmse, maps, X, Y
        global X_train, X_test, y_train, y_test
        X_train1 = np.reshape(X_train, (X_train.shape[0], (X_train.shape[1] * X_train.shape[2] * X_train.shape[3])))
        X_test1 = np.reshape(X_test, (X_test.shape[0], (X_test.shape[1] * X_test.shape[2] * X_test.shape[3])))
        mlp = MLPRegressor()
        mlp.fit(X_train1, y_train.ravel())
        predict = mlp.predict(X_test1)
        img_b64, test_label, predict = calculateMetrics("MLP", predict, y_test)#call function to calculate prediction accuracy
        output='<table border=1 align=center width=100%><tr><th><font size="" color="black">Algorithm Name</th><th><font size="" color="black">RMSE</th><th><font size="" color="black">MAP</th>'
        output+='</tr>'
        algorithms = ['Existing MLP']
        for i in range(len(algorithms)):
            output+='<td><font size="" color="black">'+algorithms[i]+'</td><td><font size="" color="black">'+str(rmse[i])+'</td><td><font size="" color="black">'+str(maps[i])+'</td></tr>'
        output+= "</table></br>"
        context= {'data':output, 'img': img_b64}
        return render(request, 'ViewResult.html', context)        

def AdminLogin(request):
    if request.method == 'GET':
       return render(request, 'AdminLogin.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Aboutus(request):
    if request.method == 'GET':
       return render(request, 'Aboutus.html', {})

def LoadDataset(request):
    if request.method == 'GET':
       return render(request, 'LoadDataset.html', {})    

def AdminLoginAction(request):
    if request.method == 'POST':
        global uname
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        if username == "admin" and password == "admin":
            context= {'data':'welcome '+username}
            return render(request, 'AdminScreen.html', context)
        else:
            context= {'data':'Invalid login details'}
            return render(request, 'AdminLogin.html', context)          

def LoadDatasetAction(request):
    if request.method == 'POST':
        myfile = request.FILES['t1'].read()
        fname = request.FILES['t1'].name
        if os.path.exists("MetroApp/static/"+fname):
            os.remove("MetroApp/static/"+fname)
        with open("MetroApp/static/"+fname, "wb") as file:
            file.write(myfile)
        file.close()
        dataset = pd.read_csv("MetroApp/static/"+fname,nrows=1000)
        columns = dataset.columns
        dataset = dataset.values
        output='<table border=1 align=center width=100%><tr>'
        for i in range(len(columns)):
            output += '<th><font size="" color="black">'+columns[i]+'</th>'
        output += '</tr>'
        for i in range(len(dataset)):
            output += '<tr>'
            for j in range(len(dataset[i])):
                output += '<td><font size="" color="black">'+str(dataset[i,j])+'</td>'
            output += '</tr>'
        output+= "</table></br></br></br></br>"
        #print(output)
        context= {'data':output}
        return render(request, 'ViewResult.html', context)    







        
