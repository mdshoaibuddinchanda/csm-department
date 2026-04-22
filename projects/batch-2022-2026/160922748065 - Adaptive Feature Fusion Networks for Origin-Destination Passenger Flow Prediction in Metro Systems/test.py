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
X_train, X_test1, y_train, y_test1 = train_test_split(X, Y, test_size = 0.1)

#function to calculate accuracy and prediction sales graph
def calculateMetrics(algorithm, predict, test_labels):
    mse_value = sqrt(mean_squared_error(test_labels, predict))
    score = mean_absolute_error(np.asarray(test_labels), np.asarray(predict))
    #maps = mean_absolute_percentage_error(test_labels, predict)
    print(algorithm+" RMSE : "+str(mse_value)+"\n")
    print(algorithm+" mae : "+str(score)+"\n")
    #text.insert(END,algorithm+" MAP : "+str(maps)+"\n\n")
    
    predict = predict.reshape(-1, 1)
    predict = scaler1.inverse_transform(predict)
    test_label = scaler1.inverse_transform(test_labels)
    predict = predict.ravel()
    test_label = test_label.ravel()    
    
    #rmse.append(mse_value)
    #r2.append(score)
    #map_error.append(maps)
    predict = predict[0:200]
    test_label = test_label[0:200]
    for i in range(0, 20):
        print("True Observation Percent : "+str(test_label[i])+" Predicted Observation Percent : "+str(predict[i]))
    plt.figure(figsize=(5,3))
    plt.plot(test_label, color = 'red', label = 'True Energy Consumption')
    plt.plot(predict, color = 'green', label = 'Predicted Energy Consumption')
    plt.title(algorithm+' Test & Predicted Energy Consumption Graph')
    plt.xlabel('Test Data')
    plt.ylabel('Predicted Energy Consumption')
    plt.legend()
    plt.show()


cnn_model = Sequential()
cnn_model.add(Convolution2D(32, (1 , 1), input_shape = (X_train.shape[1], X_train.shape[2], X_train.shape[3]), activation = 'relu'))
cnn_model.add(MaxPooling2D(pool_size = (1, 1)))
cnn_model.add(Convolution2D(32, (1, 1), activation = 'relu'))
cnn_model.add(MaxPooling2D(pool_size = (1, 1)))
cnn_model.add(Flatten())
cnn_model.add(RepeatVector(2))
#adding bidirectional + GRU to CNN layer
cnn_model.add(Bidirectional(GRU(32, activation = 'relu')))
cnn_model.add(Dense(units = 256, activation = 'relu'))
cnn_model.add(Dense(units = 1))
cnn_model.compile(optimizer = 'adam', loss = 'mean_squared_error')
if os.path.exists("model/affn_weights.hdf5") == False:
    model_check_point = ModelCheckpoint(filepath='model/affn_weights.hdf5', verbose = 1, save_best_only = True)
    cnn_model.fit(X_train, y_train, batch_size = 8, epochs = 50, validation_data=(X_test, y_test), callbacks=[model_check_point], verbose=1)
else:
    cnn_model.load_weights("model/affn_weights.hdf5")
predict = cnn_model.predict(X_test) 
calculateMetrics("Extension CNN2D", predict, y_test)#call function to calculate prediction accuracy

cnn_model = Sequential()
cnn_model.add(Convolution2D(32, (1 , 1), input_shape = (X_train.shape[1], X_train.shape[2], X_train.shape[3]), activation = 'relu'))
cnn_model.add(MaxPooling2D(pool_size = (1, 1)))
cnn_model.add(Convolution2D(32, (1, 1), activation = 'relu'))
cnn_model.add(MaxPooling2D(pool_size = (1, 1)))
cnn_model.add(Flatten())
cnn_model.add(RepeatVector(2))
#adding bidirectional + GRU to CNN layer
cnn_model.add(LSTM(64, activation = 'relu'))
cnn_model.add(Dense(units = 256, activation = 'relu'))
cnn_model.add(Dense(units = 1))
cnn_model.compile(optimizer = 'adam', loss = 'mean_squared_error')
if os.path.exists("model/extension_weights.hdf5") == False:
    model_check_point = ModelCheckpoint(filepath='model/extension_weights.hdf5', verbose = 1, save_best_only = True)
    cnn_model.fit(X_train, y_train, batch_size = 8, epochs = 50, validation_data=(X_test, y_test), callbacks=[model_check_point], verbose=1)
else:
    cnn_model.load_weights("model/extension_weights.hdf5")
predict = cnn_model.predict(X_test) 
calculateMetrics("Extension CNN2D", predict, y_test)#call function to calculate prediction accuracy    

X_train = np.reshape(X_train, (X_train.shape[0], (X_train.shape[1] * X_train.shape[2] * X_train.shape[3])))
X_test = np.reshape(X_test, (X_test.shape[0], (X_test.shape[1] * X_test.shape[2] * X_test.shape[3])))
mlp = MLPRegressor()
mlp.fit(X_train, y_train.ravel())
predict = mlp.predict(X_test)
calculateMetrics("MLP", predict, y_test)#call function to calculate prediction accuracy  
