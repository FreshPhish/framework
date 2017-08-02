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
from DataLoader import DataLoader as DataLoader



def GridSearch(X_train,y_train,X_test,y_test,X_clean=None,X_phish=None,optimization=None):
    print("*********************************************")
    print("Using Grid search to calculate optimal kernel.")
    print("*********************************************")
    y_ravel = np.ravel(y_train)
    cv = cross_validation.StratifiedKFold(y_ravel, 5, shuffle=True, random_state=0)
    C_range = np.logspace(-3, 5, 9)
    Gamma_range = np.logspace(-9, 3, 9)
    param_grid = [
        {'C': C_range, 'gamma': Gamma_range, 'kernel': ['rbf']}
    ]
    classifier = GridSearchCV(estimator=svm.SVC(), param_grid=param_grid, verbose=100)
    print("Train Clissifier")
    classifier.fit(X_train, y_ravel)
    kernel_name = classifier.best_params_['kernel']
    cost = classifier.best_params_['C']
    gamma = classifier.best_params_['gamma']
    print ("Best Cost: {}".format(cost))
    print ("Best Gamma: {}".format(gamma))

    
if __name__=='__main__' :
    dataloader = DataLoader()
    X_train,y_train,X_test,y_test = dataloader.loadWholeData( "../data/DataCleanSites.txt" , "../data/DataPhishingSites.txt" , containWebsiteName =1)
    GridSearch(X_train,y_train,X_test,y_test)