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
from DeepNeuralNetwork import DeepNeuralNetwork as DNN
from LinearClassifier import LinearClassifier as LNC
from SVMLinear import SVMLinear as SVMLinear
from SVMRBF import SVMRBF as SVMRBF
from tfLinearClassifier import tfLinearClassifier as tfLinearClassifier
from FeatureCorrelation import FeatureCorrelation as FeatureCorrelation
from DataLoader import DataLoader as DataLoader
from MetricsIndicator import MetricsIndicator as MetricsIndicator


expArgNumber = 1

def FitAndPredict(X_train,y_train,X_test,y_test):
    
    
    #SVMRBF
    classifier = SVMRBF()
    indicator = MetricsIndicator(classifier)
    indicator.DoFitandPredict("SVM Guassian",X_train,y_train,X_test,y_test)

    #Adagrad
    classifier = DNN("data/dnn")
    indicator = MetricsIndicator(classifier)
    indicator.DoFitandPredict( "Tensorflow Adagrad",X_train,y_train,X_test,y_test)

    #Adadelta
    classifier = DNN(model_dir = "data/dnn" , optimization=tf.train.AdadeltaOptimizer)
    indicator = MetricsIndicator(classifier)
    indicator.DoFitandPredict("Tensorflow Adadelta",X_train,y_train,X_test,y_test)

    #Gradient Descent
    classifier = DNN(model_dir = "data/dnn" , optimization=tf.train.GradientDescentOptimizer)
    indicator = MetricsIndicator(classifier)
    indicator.DoFitandPredict( "Tensorflow GradientDescent",X_train,y_train,X_test,y_test)

    #SVMLinear
    classifier = SVMLinear()
    indicator = MetricsIndicator(classifier)
    indicator.DoFitandPredict( "SVM Linear",X_train,y_train,X_test,y_test)
    
    
    #Linear Tensor Flow
    classifier = tfLinearClassifier(model_dir = "data/linearTensorFlow")
    indicator = MetricsIndicator(classifier)
    indicator.DoFitandPredict( "Tensorflow Linear",X_train,y_train,X_test,y_test)


def FeatureAnalysis(X_train,y_train,X_test,y_test):
    featureSel = FeatureCorrelation(X_train,y_train,X_test,y_test)
    featureSel.FeatureSelection()
    featureSel.FeatureImportance()

if __name__=='__main__' :

    tf.logging.set_verbosity(tf.logging.ERROR)   #only show erros not warning messages
    expNumber = int(sys.argv[expArgNumber])

    if (expNumber == 1):
        print ("EXP 1 : Loading whole data and fitting and predicting on them")
        dataloader = DataLoader()
        X_train,y_train,X_test,y_test = dataloader.loadWholeData( "../data/DataCleanSites.txt" , "../data/DataPhishingSites.txt" , containWebsiteName =1)
        FitAndPredict(X_train,y_train,X_test,y_test)

    if (expNumber == 2):
        print ("EXP2: finding True Negative - fitting on both dataset but predicting on clean websites")
        dataloader = DataLoader()
        X_train,y_train,X_test,y_test = dataloader.UseOneLabelForPredict( "../data/DataCleanSites.txt" , "../data/DataPhishingSites.txt" , containWebsiteName =1 , PredictLabel = 0)
        FitAndPredict(X_train,y_train,X_test,y_test)

        X_train,y_train,X_test,y_test = dataloader.UseOneLabelForPredict( "../data/DataCleanSites.txt" , "../data/DataPhishingSites.txt" , containWebsiteName =1 , PredictLabel = 1)
        FitAndPredict(X_train,y_train,X_test,y_test)

    if (expNumber == 3):
        print ("Measuring feature importance")
        print ("EXP 1 : Loading whole data and fitting and predicting on them")
        dataloader = DataLoader()
        X_train,y_train,X_test,y_test = dataloader.loadWholeData( "../data/DataCleanSites.txt" , "../data/DataPhishingSites.txt" , containWebsiteName =1)
        FeatureAnalysis(X_train,y_train,X_test,y_test)

    if (expNumber == 4):
        print ("Testing PCA")
        dataloader = DataLoader()
        X_train,y_train,X_test,y_test = dataloader.loadWholeData( "../data/DataCleanSites.txt" , "../data/DataPhishingSites.txt" , containWebsiteName =1)
        featureSel = FeatureCorrelation(X_train,y_train,X_test,y_test)
        featureSel.FeatureImportance1()
        featureSel.FeatureElimination()
        
        
    if (expNumber == 5):
        a = [2,3,6,11,12,13,19,20,22,28]
        dataloader = DataLoader()
        X_train,y_train,X_test,y_test = dataloader.loadWholeData( "../data/DataCleanSites.txt" , "../data/DataPhishingSites.txt" , containWebsiteName =1)
        featureSel = FeatureCorrelation(X_train,y_train,X_test,y_test)
        featureSel.FeatureElimination()
        for i in a:
            print (featureSel.labelTitles[i-1])
        