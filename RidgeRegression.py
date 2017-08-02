import numpy as np
from matplotlib import pyplot as plt
from random import randint
from math import sqrt

class RidgeRegression :
	
	def fit(self, X, y, regularizationParam=0):
		B = regularizationParam * np.eye(X.shape[1])
		B[0, 0] = 0
		self.w = np.dot(np.linalg.pinv(np.dot(X.T, X) + np.dot(B.T, B)),np.dot(X.T, y))
		
	def predict(self, X):
		h= np.dot(X, self.w)
		return h
		
	def rmse(self,y,h):
		
		Ermse=0.00
		for i in range(len(y)):
			Ermse= Ermse+(y[i]-h[i])**2
		Ermse=Ermse*1/len(y)
		Ermse=sqrt(Ermse)
		return Ermse
		
	def mad(self,y,h):
		
		Emad=0.00
		for i in range(len(y)):
			Emad=Emad+abs(y[i]-h[i])
		Emad=Emad*1/len(y)
		return Emad
		
	def rec(self,E):
		
		Eprev=0.00
		correct=0.00
		acc=0.00
		X_axis,Y_axis=[],[]
		for i in range(len(E)):
			if E[i] > Eprev:
				acc=correct/len(E)
				X_axis.append(Eprev)
				Y_axis.append(acc)
				Eprev=E[i]
			correct+=1
		acc=correct/len(E)
		X_axis.append(E[len(E)-1])
		Y_axis.append(acc)
		plt.plot(X_axis, Y_axis, 'g')
		plt.show()
		
	def ImportanceOfFeature(self, feature, label):
		return np.corrcoef(feature, label)[0,1]
		
	def ImportantFeatureLeast(self):
		W= abs(self.w)
		return np.argmin(W)
