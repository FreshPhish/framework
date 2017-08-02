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
from sklearn import datasets
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA
from sklearn import datasets
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
from sklearn import decomposition
from sklearn import datasets
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_selection import RFECV
from sklearn.datasets import make_classification
from sklearn.feature_selection import RFECV
from sklearn.svm import SVR

class FeatureCorrelation:

    def __init__(self , X_train , y_train , X_test ,y_test):

        self.X_train = X_train
        self.y_train = y_train
        
        self.X = X_train
        self.y = y_train
        
        self.X_test = X_test
        self.y_test = y_test

        self.labelTitles = ['having IP Address' , 'URL Length', 'Shortining Service' , 'having At Symbol' , 'double slash redirecting', 'Prefix Suffix', 'having Sub Domain' , 'SSLfinal State' , 'Domain registeration length' , 'Favicon' , 'port' , 'HTTPS token' , 'Request URL' , 'URL of Anchor' , 'Links in tags' , 'SFH' , 'Submitting to email' , 'Abnormal URL' , 'Redirect' , 'on mouseover' , 'RightClick' , 'popUpWidnow' , 'Iframe' , 'age of domain' , 'DNSRecord' , 'web traffic' , 'Page Rank' , 'Google Index' , 'Links pointing to page' , 'Statistical report']


    def FeatureSelection(self):

        # Create the RFE object and compute a cross-validated score.
        svc = SVC(kernel="linear")
        # The "accuracy" scoring is proportional to the number of correct
        # classifications
        rfecv = RFECV(estimator=svc, step=1, cv=StratifiedKFold(2),
                      scoring='accuracy')
        rfecv.fit(self.X_train, self.y_train)

        print("Optimal number of features : %d" % rfecv.n_features_)

        # Plot number of features VS. cross-validation scores
        plt.figure()
        plt.xlabel("Number of features selected")
        plt.ylabel("Cross validation score (nb of correct classifications)")
        plt.plot(range(1, len(rfecv.grid_scores_) + 1), rfecv.grid_scores_)
        plt.savefig('images/FeatureSelection.png')
        plt.cla()   # Clear axis
        plt.clf() # Clear figure

    def FeatureImportance(self ):
        #plotting importance of each feature
        R=RidgeRegression();
        importance=np.zeros(len(self.X[0]))
        index = 0
        for feature in range(len(self.X[0])):
            importance[index] = R.ImportanceOfFeature(self.X[:,feature], self.y[:,0])
            index += 1

        plt.plot(range(len(self.X[0])), importance, 'db')
        plt.savefig('images/FeatureImportance.png')
        plt.cla()   # Clear axis
        plt.clf() # Clear figure
        print (self.labelTitles)
        print (importance)
        
        
    def FeatureImportance1(self):
        # Feature Importance
        from sklearn import datasets
        from sklearn import metrics
        from sklearn.ensemble import ExtraTreesClassifier
        # load the iris datasets
        #dataset = datasets.load_iris()
        # fit an Extra Trees model to the data
        model = ExtraTreesClassifier()
        model.fit(self.X_train, self.y_train)
        # display the relative importance of each attribute
        print(model.feature_importances_)
        
    def FeatureElimination(self):
        """
        model = LogisticRegression()
        # create the RFE model and select 3 attributes
        rfe = RFE(model, 1)
        rfe = rfe.fit(self.X_train, self.y_train)
        # summarize the selection of the attributes
        print(rfe.support_)
        print(rfe.ranking_)
        
        for i in range (len(self.X_train[0])):
            print (self.labelTitles[i], " , ",rfe.ranking_[i])
        """
        
        estimator = SVR(kernel="linear")
        selector = RFECV(estimator, step=1, cv=5)
        selector = selector.fit(self.X_train, self.y_train)
        print (selector.support_)
        print (selector.ranking_)

