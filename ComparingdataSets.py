import numpy as np

#tf.logging.set_verbosity(tf.logging.ERROR)   #only show erros not warning messages

def loadData(filename ):
    '''Load 80% for training reserve 20% for Testing'''
    
    trainData = np.genfromtxt(filename,delimiter=",",dtype=int)

    y_train = trainData[:,-1:]  #last column
    y_train[y_train < 0] = 0    #convert all -1 to 0 lables
    X_train = trainData[:,:-1]  #all except last column
    X_train.tolist()
    print (len(X_train))
    X_trainZeros = []
    X_trainOnes = []
    for i in range (0 , len(y_train) -1 ):
        if y_train[i] == 0 :
            X_trainZeros.append( X_train[i] )
        if y_train[i] == 1:
            X_trainOnes.append( X_train[i] )
    return X_trainZeros , X_trainOnes


def loadMyData(filename ):
    X_train = np.genfromtxt(filename,delimiter=",",dtype=int)
    X_train.tolist()

    return X_train

def measureZerosOnes(arr):
    countOnes = np.zeros(30)
    countZeros = np.zeros(30)
    for cols in range (0,30):
        for rows in range (0, len (arr)):
            if arr[rows][cols] <= 0:
                countZeros[cols] = countZeros[cols]  + 1
            if arr[rows][cols] == 1:
                countOnes[cols] = countOnes[cols] + 1

    for i in range (0,30):
        countOnes[i] = round (countOnes[i]/len(arr) , 2)
        countZeros[i] = round (countZeros[i]/len(arr) , 2)
    
    
    print (*countZeros , sep=" , ")
    print (*countOnes , sep=" , ")
    

if __name__=='__main__' :
    """
    file_name = "../data/Phishing_Data.arff"
    X_trainZeros , X_trainOnes = loadData(file_name )

    print ("Zeros")
    measureZerosOnes (X_trainZeros)

    print ("Ones")
    measureZerosOnes (X_trainOnes)
    
    
    """
    print ("Clean Sites")
    file_name = "../data/DataCleanSites.txt"
    X_trainOnes = loadMyData(file_name)
    print ("Ones")
    measureZerosOnes (X_trainOnes)


    print ("Phishing Sites")
    file_name = "../data/DataPhishingSites.txt"
    X_trainZeros = loadMyData(file_name)
    print ("Zeros")
    measureZerosOnes (X_trainZeros)
    #"""   
    
    
    
    
    

    