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


def loadData(dataFileName, labelFileName):
    '''Load 80% for training reserve 20% for Testing'''

    rawData = np.genfromtxt(dataFileName,delimiter=",",dtype=int)
    np.random.shuffle(rawData)  #shuffle train data works in memory so no need to create a copy

    X = rawData[:,:-1]  #all except last column
    y = rawData[:,-1:]  #last column
    y[y < 0] = 0 #convert all -1 to 0 labels

    X_train = X[int(len(X)*.2):]  #last 80% of rows
    y_train = y[int(len(y)*.2):]  #last 80% of rows

    X_test = X[:int(len(X)*.2)]  #first 20% of rows
    y_test = y[:int(len(y)*.2)]  #first 20% of rows

    labelTitles = ['having IP Address' , 'URL Length', 'Shortining Service' , 'having At Symbol' , 'double slash redirecting', 'Prefix Suffix', 'having Sub Domain' , 'SSLfinal State' , 'Domain registeration length' , 'Favicon' , 'port' , 'HTTPS token' , 'Request URL' , 'URL of Anchor' , 'Links in tags' , 'SFH' , 'Submitting to email' , 'Abnormal URL' , 'Redirect' , 'on mouseover' , 'RightClick' , 'popUpWidnow' , 'Iframe' , 'age of domain' , 'DNSRecord' , 'web traffic' , 'Page Rank' , 'Google Index' , 'Links pointing to page' , 'Statistical report']

    return X , y , X_train,y_train,X_test,y_test , labelTitles

def FeatureSelection(X_train , y_train , X_test , y_test , labelTitles ):
    	# Incrementally removing features
    index=len(X_train[0])

    BefDelXtrain=AftXtrain=X_train
    BefDelXtest=AftXtest=X_test

    R=RidgeRegression()
    R.fit(X_train,y_train,0.01)
    RMSE = []
    indexs=[]
    while index > 1:
        LeastIndex=R.ImportantFeatureLeast()
        index-=1

        print (labelTitles[LeastIndex])
        labelTitles.remove(labelTitles[LeastIndex])
        #np.delete(labelTitles, LeastIndex, axis=1)

        AftXtrain=np.delete(BefDelXtrain, np.s_[LeastIndex], axis=1)
        AftXtest=np.delete(BefDelXtest, np.s_[LeastIndex], axis=1)

        R=RidgeRegression()
        R.fit(AftXtrain,y_train,0.01)
        h=R.predict(AftXtest)
        RMSE.append(R.rmse(y_test,h))
        indexs.append(index)

        BefDelXtrain=AftXtrain
        BefDelXtest=AftXtest

    plt.plot(indexs,RMSE,'b', label='RMSE')
    plt.legend()
    plt.savefig('images/FeatureSelection.png')
    plt.cla()   # Clear axis
    plt.clf() # Clear figure


def FeatureImportance(X , y):
    #plotting importance of each feature
    R=RidgeRegression();
    importance=np.zeros(len(X[0]))
    index = 0
    for feature in range(len(X[0])):
        importance[index] = R.ImportanceOfFeature(X[:,feature], y[:,0])
        index += 1

    plt.plot(range(len(X[0])), importance, 'db')
    #plt.plot(labelTitles, importance, 'db')
    plt.savefig('images/FeatureImportance.png')
    plt.cla()   # Clear axis
    plt.clf() # Clear figure

if __name__ == '__main__':
    dataFile_name = "Phishing_Data.arff"
    labelFile_name = "FeatureLabels.data"

    X , y , X_train,y_train,X_test,y_test , labelTitles = loadData(dataFile_name , labelFile_name)
    #print(labelTitles)
    FeatureImportance(X , y )
    FeatureSelection(X_train,y_train,X_test,y_test , labelTitles)
