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


class SVMRBF:

    def __init__(self):
        # change to 1d array
        self.fit_time=0
        self.predict_time=0


    def fit(self , X_train,y_train ):

        y_ravel = np.ravel(y_train)
        cv = cross_validation.StratifiedKFold(y_ravel, 5, shuffle=True, random_state=0)

        bestCost = 100   #found by grid search
        bestGamma = 0.031622776601683791  #found by grid search

        #self.fit_time = Timer(lambda: self.classifier.fit(X_train, y_ravel))
        self.classifier = svm.SVC(kernel='rbf', gamma=bestGamma,C=bestCost)
        self.classifier.fit(X_train, y_ravel)

    def predict(self,X_test):
        return self.classifier.predict(X_test)
