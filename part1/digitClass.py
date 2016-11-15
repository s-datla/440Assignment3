#!usr/bin/python
import sys
import string
import math
from pprint import pprint as pp
from collections import defaultdict


class digitClass:
    def __init__(self,label):
        self.count = [[0 for j in range(28)] for k in range(28)]
        self.prob = [[[0.0 for i in range(2)] for j in range(28)] for k in range(28)]
        self.label = label
        self.total = 0
        self.initialProb = 0.0
        self.testHigh = float("-inf")
        self.testLow = float(0)
        self.maxImage = [[' ' for j in range(28)] for k in range(28)]
        self.minImage = [[' ' for j in range(28)] for k in range(28)]

    def countPixels(self,readLines):
        for i in range(28):
            text = str(readLines[i][0])
            for j in range(28):
                if text[j] == '+':
                    self.count[i][j] += 1
                elif text[j] == '#':
                    self.count[i][j] += 1
        self.total += 1

    def smooth(self,k):
        for i in range(28):
            for j in range(28):
                self.count[i][j] += k
        self.total += (k * 2)

    def calculateProb(self):
        prob = 0.0
        for i in range(28):
            for j in range(28):
                prob = float(self.count[i][j]) / float(self.total)
                self.prob[i][j][0] = 1 - prob
                self.prob[i][j][1] = prob

    def calculatePrior(self,newtotal):
        self.initialProb = float(self.total) / float(newtotal)

    def testPixels(self,readLines):
        currentProb = math.log(self.initialProb)
        for i in range(28):
            text = str(readLines[i][0])
            for j in range(28):
                if text[j] == ' ':
                    currentProb += math.log(self.prob[i][j][0])
                elif text[j] == '+':
                    currentProb += math.log(self.prob[i][j][1])
                elif text[j] == '#':
                    currentProb += math.log(self.prob[i][j][1])
        if currentProb > self.testHigh:
            self.maxImage = readLines
            self.testHigh = currentProb
        if currentProb < self.testLow:
            self.minImage = readLines
            self.testLow = currentProb
        return currentProb


    def printHighLow(self):
        print "Image with Highest Posterier Probability (Log) for Digit : " + str(self.label)
        print self.testHigh
        for i in range(28):
            print self.maxImage[i]
        print "Image with Lowest Posterior Probability (Log) for Digit : " + str(self.label)
        print self.testLow
        for i in range(28):
            print self.minImage[i]

    def printCount(self):
        for i in range(28):
            print self.count[i]

    def printProb(self):
        print self.prob

    def getPixelProb(self,x,y,val):
        return self.prob[x][y][val]

if __name__ == "__main__":
    digitClass(sys.argv[0],sys.argv[1],sys.argv[2])
