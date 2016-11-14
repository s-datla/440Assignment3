#!usr/bin/python
import argparse
from pprint import pprint as pp
import sys
import string
import math
import digitClass as dc
from collections import defaultdict

class digitBayes:
    def __init__(self,dimages,dlabels):

        self.data = {'0':None,'1':None,'2':None,'3':None,'4':None,'5':None,'6':None,'7':None,'8':None,'9':None}
        self.confusionMatrix = [[0 for i in range(10)] for j in range(10)]
        self.total = 0

        for word in self.data:
            self.data[word] = dc.digitClass(word)

        currentImage = ['' for i in range(28)]
        with open(dimages) as imagef:
            index = 0
            for i,lines in enumerate(imagef):
                lines = lines.strip('\r\t\n')
                currentImage[i % 28] = lines.split(r'(\s+)')
                if i == ((index + 1) * 28) - 1:
                    index += 1
                    self.data[currentlabel].countPixels(currentImage)
                    currentImage = ['' for i in range(28)]
                if i % 28 == 0:
                    currentlabel = self.getLabel(dlabels,index)
            self.total = index

        for word in self.data:
            self.data[word].calculatePrior(self.total)
            self.data[word].smooth(1)
            self.data[word].calculateProb()

    def getLabel(self,dlabel,index):
        with open(dlabel) as file:
            for i,lines in enumerate(file):
                if i == index:
                    lines = lines.strip()
                    return lines

    def test(self,dtest,dtlabels):
        testImage = ['' for i in range(28)]
        likely = float("-inf")
        likelyClass = '0'
        with open(dtest) as testf:
            index = 0
            for i,lines in enumerate(testf):
                lines = lines.strip('\r\t\n')
                testImage[i % 28] = lines.split(r'(\s+)')
                if i == ((index + 1) * 28) - 1:
                    index += 1
                    for word in self.data:
                        temp = self.data[word].testPixels(testImage)
                        if temp > likely:
                            likely = temp
                            likelyClass = word
                    self.confusionMatrix[int(currentlabel)][int(likelyClass)] += 1
                    testImage = ['' for i in range(28)]
                    likely = float("-inf")
                if i % 28 == 0:
                    currentlabel = self.getLabel(dtlabels,index)
        self.calculateConfusionMatrix()

    def calculateConfusionMatrix(self):
        rowtotal = 0
        for i in range(10):
            for j in range(10):
                rowtotal += self.confusionMatrix[i][j]
            for j in range(10):
                self.confusionMatrix[i][j] /= float(rowtotal)
            rowtotal = 0
        print "CONFUSION MATRIX: "
        pp(self.confusionMatrix)
        self.printEvaluation()

    def printEvaluation(self):
        pTotal = 0
        pNum = 0
        for i in range(10):
            for j in range(10):
                if i == j :
                    pTotal += self.confusionMatrix[i][j]
                    pNum += 1

        pTotal /= pNum
        print "ACCURACY: " + str(pTotal)


def parse_args():
    parser = argparse.ArgumentParser(description="Run Digit Classifier")
    parser.add_argument("--train", nargs=2,type=str, help="Digit Training Files (images + labels)", required=True)
    parser.add_argument("--test", nargs=2,type=str, help="Digit Testing Files (images + labels)", required=True)
    args = parser.parse_args()
    return args.train, args.test

if __name__ == "__main__":
    dtrain, dtest = parse_args()
    print dtrain[0],dtrain[1]
    trained = digitBayes(dtrain[0],dtrain[1])
    trained.test(dtest[0],dtest[1])
