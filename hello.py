import numpy as np
from matplotlib import pyplot as plt
from sklearn import svm, metrics

# dataset = np.genfromtxt("matrixJewelry.txt", delimiter=';')
# print dataset
import csv

with open("matrixJewelry.txt",'r') as dest_f:
    data_iter = csv.reader(dest_f, delimiter = ';')
    data = [data for data in data_iter]


data_array = np.array(data) 

Price = data_array[1:,0]
MeanPrice = np.mean(Price[Price!='unknown'].astype(np.float), axis=0)
Price[Price=='unknown'] = MeanPrice
Price = np.expand_dims(Price, axis=1)


target = data_array[1:,4]
dataset = np.hstack((Price, data_array[1:,5:]))


NSample = len(dataset)

np.random.seed(34567)
order = np.random.permutation(NSample)

dataset = dataset[order]
target = target[order].astype(np.float)


dataset_train = dataset[:.9 * NSample]
target_train = target[:.9 * NSample]
dataset_test = dataset[.9 * NSample:]
target_test = target[.9 * NSample:]

Classifier = svm.SVC(cache_size=1000)
Classifier.fit(dataset_train, target_train) 
Predicted = Classifier.predict(dataset_test)


print("Classification report for classifier %s:\n%s\n"
      % (Classifier, metrics.classification_report(target_test, Predicted)))
print("Confusion matrix:\n%s" % metrics.confusion_matrix(target_test, Predicted))

images_and_predictions = list(zip(target_test, Predicted))
for index, (image, prediction) in enumerate(images_and_predictions[:4]):
    plt.subplot(2, 4, index + 5)
    plt.axis('off')
    plt.imshow(image, cmap=plt.cm.gray_r, interpolation='nearest')
    plt.title('Prediction: %i' % prediction)

plt.show()

#dec = clf.decision_function([[1]])
#dec.shape[1] # 4 classes: 4*3/2 = 6

# TrainDataSet = 
# X = [[0, 0], [1, 1]]
# y = [0, 1]
# clf = svm.SVC()