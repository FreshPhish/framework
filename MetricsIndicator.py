from __future__ import absolute_import
from __future__ import division
from __future__ import print_function #enforces python 3 syntax
import tensorflow as tf
from tensorflow.contrib.learn.python.learn.metric_spec import MetricSpec
import numpy as np
from sklearn import datasets, metrics, preprocessing
from sklearn.preprocessing import LabelBinarizer
from sklearn import svm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime
from sklearn.grid_search import GridSearchCV
from sklearn import cross_validation
from timeit import Timer # measure time
from sklearn.metrics import roc_curve, auc
from pylab import savefig
import sys
import time

class MetricsIndicator:

    def __init__(self,classifier):
        self.classifier = classifier

    def DoFitandPredict(self, classifierName,X_train,y_train,X_test,y_test):
        
        startTime = time.time()
        self.classifier.fit(X_train,y_train)
        endTime = time.time()
        self.fitTime = endTime - startTime
        startTime = time.time()
        y_hat = self.classifier.predict(X_test)
        endTime = time.time()
        self.predictTime = endTime - startTime

        self.AccuracyMeasure(y_test,y_hat)
        print ("Classifier : {} ".format( classifierName ))
        print ("--Timing--" )
        print ("fit time {} - predict time:{} ".format( round ( self.fitTime , 2 ) , round ( self.predictTime , 2 )   ))
        print ("--Accuracy--" )
        print ("Accuracy:{}, AUC:{} ".format( round(self.accuracy_score*100, 2) , round(self.auc*100,2) ))
        print ("Legitimate Accuracy:{}, Phishing Accuracy:{} ".format( round(self.LegAcc*100, 2) , round(self.PhishAcc*100,2) ))
        print ("Drawing ROC curves...")
        self.Plot_ROC_Cureve(classifierName, y_test, y_hat)
        plt.savefig('../images/ROC.png')
        print ("saved images file")
        print ("--------")

    def AccuracyMeasure(self , y_test, y_hat ):
        
        self.LegAcc, self.PhishAcc = self.perf_measure( y_test , y_hat )
        self.accuracy_score = metrics.accuracy_score(y_test,y_hat)
        self.auc = metrics.roc_auc_score(y_test,y_hat)

        return self.accuracy_score,self.auc

    def perf_measure(self, y_test, y_hat):
        TP = 0
        FP = 0
        TN = 0
        FN = 0
        print ()
        for i in range(len(y_hat)):
            if y_test[i]==y_hat[i]==1:
               TP += 1
        for i in range(len(y_hat)):
            if y_hat[i]==1 and y_test[i]!=y_hat[i]:
               FP += 1
    
        for i in range(len(y_hat)):
            if y_test[i]==y_hat[i]==0:
               TN += 1
        for i in range(len(y_hat)):
            if y_hat[i]==0 and y_test[i]!=y_hat[i]:
               FN += 1

        return round(TP/(TP+FP) , 2),round(TN/(TN+FN) , 2)
    
    def Plot_ROC_Cureve(self,classifierName, y_test, y_hat):
        svmlx2, svmly2, _ = roc_curve(y_test, y_hat)
        plt.figure(1)
        plt.plot([0, 1], [0, 1], 'k--')
        plt.plot(svmlx2, svmly2, label=classifierName)
        plt.xlabel('')
        plt.ylabel('')
        plt.title('ROC curve')
        plt.legend(loc='best')
    
    
    
    