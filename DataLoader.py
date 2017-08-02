from __future__ import absolute_import
from __future__ import division
from __future__ import print_function #enforces python 3 syntax
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import LabelBinarizer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime
import numpy as np
import matplotlib.pyplot as plt
from RidgeRegression import RidgeRegression
import random

class DataLoader:

    def __init__(self ):
        print ("Initialing loading data")
        
    def FixTrainAndTest(self, trainData , testData):
        y_train = trainData[:,-1:]  #last column
        y_train[y_train < 0] = 0      #convert all -1 to 0 lables
        X_train = trainData[:,:-1]  #all except last column

        y_test = testData[:,-1:]    #last column
        y_test[y_test < 0] = 0      #convert all -1 to 0 lables
        X_test = testData[:,:-1]    #all except last column
        print ("loaded data - X_train = {} ,y_train = {} ,X_test ={} ,y_test = {}".format(X_train.shape,y_train.shape,X_test.shape,y_test.shape) )
        return X_train,y_train,X_test,y_test

    def loadWholeData(self,fileNameClean , fileNamePhishing , containWebsiteName, rowsNumber = 6000 ):
        '''Load 80% for training reserve 20% for Testing'''
        rawDataClean = np.genfromtxt(fileNameClean,delimiter=",",dtype=int) #reading from Clean file
        if (containWebsiteName == 1):
            rawDataClean = rawDataClean[:,:-1] # Removing last coloumn which is the name of website
        rawDataClean = rawDataClean[:rowsNumber,:]

        rawDataPhishing = np.genfromtxt(fileNamePhishing,delimiter=",",dtype=int) #reading from Phishing file
        if (containWebsiteName == 1):
            rawDataPhishing = rawDataPhishing[:,:-1] # Removing last coloumn which is the name of website
        rawDataPhishing = rawDataPhishing[:rowsNumber,:]

        rawData = np.concatenate((rawDataClean, rawDataPhishing), axis=0) #concat both clean and phishing dataset
        np.random.shuffle(rawData)  #shuffle whole data works in memory so no need to create a copy

        print ( "Dataloaded = " , rawData.shape)
        trainData = rawData[int(len(rawData)*.2):]  #last 80% of rows
        testData = rawData[:int(len(rawData)*.2)]  #first 20% of rows

        return self.FixTrainAndTest(trainData , testData)

    def UseOneLabelForPredict(self,fileNameClean , fileNamePhishing , containWebsiteName , PredictLabel):
        print ("Loading data for testing False negative and false positive - PredictLabel = {} ".format( PredictLabel ))
        rawDataClean = np.genfromtxt(fileNameClean,delimiter=",",dtype=int) #reading from Clean file
        if (containWebsiteName == 1):
            rawDataClean = rawDataClean[:,:-1] # Removing last coloumn which is the name of website
        rawDataClean = rawDataClean[:6000,:]

        rawDataPhishing = np.genfromtxt(fileNamePhishing,delimiter=",",dtype=int) #reading from Phishing file
        if (containWebsiteName == 1):
            rawDataPhishing = rawDataPhishing[:,:-1] # Removing last coloumn which is the name of website
        rawDataPhishing = rawDataPhishing[:6000,:]
        
        np.random.shuffle(rawDataPhishing)
        np.random.shuffle(rawDataClean)
        if (PredictLabel == 0):
            testData = rawDataClean[:int(len(rawDataClean)*.2)] #first 20% of clean rows
            trainData = rawDataPhishing
            trainData = np.concatenate((trainData, rawDataClean[int(len(rawDataClean)*.2):]), axis=0) #concat 80% of clean data with 100% of clean dataset
        else:
            testData = rawDataPhishing[:int(len(rawDataPhishing)*.2)] #first 20% of phishing rows
            trainData = rawDataClean
            trainData = np.concatenate((trainData, rawDataPhishing[int(len(rawDataPhishing)*.2):]), axis=0) #concat 80% of phishing data with 100% of clean dataset

        return self.FixTrainAndTest(trainData , testData)