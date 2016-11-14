#!usr/bin/python
import argparse
from pprint import pprint as pp
import sys
import string
import math
import digitClass as dc
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np


from plotly.graph_objs import Scatter, Figure, Layout
import plotly.plotly as py
import plotly.tools as tls
tls.set_credentials_file(username='440mp3', api_key='0itazj8d4q')

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
        for word in self.data:
            self.data[word].printHighLow()
        self.oddsRatio()

    def calculateConfusionMatrix(self):
        rowtotal = 0
        for i in range(10):
            for j in range(10):
                rowtotal += self.confusionMatrix[i][j]
            for j in range(10):
                self.confusionMatrix[i][j] /= float(rowtotal)
            rowtotal = 0
        self.printConfusion()
        self.printEvaluation()

    def printConfusion(self):
        print
        print "CONFUSION MATRIX: "
        print
        for i in range(10):
            for j in range(10):
                sys.stdout.write(" {0:.4f} ".format(self.confusionMatrix[i][j]))
            sys.stdout.write("\n")
            sys.stdout.flush()

    def printEvaluation(self):
        pTotal = 0
        pNum = 0
        for i in range(10):
            for j in range(10):
                if i == j :
                    pTotal += self.confusionMatrix[i][j]
                    pNum += 1

        pTotal /= pNum
        print
        print "ACCURACY: {0:.4f}".format(pTotal)

    def oddsRatio(self):
        highestSet = [(float("-inf"),-1,-1)]
        for i in range(10):
            for j in range(10):
                if not i == j:
                    for k in range(len(highestSet)):
                        if self.confusionMatrix[i][j] > highestSet[k][0]:
                            highestSet.insert(k,(self.confusionMatrix[i][j],i,j))
                            break

        for m in range(4):
            expectedClass = str(highestSet[m][1])
            mapClass = str(highestSet[m][2])
            expectedCount = [[0.0 for x in range(28)] for y in range(28)]
            likelyCount = [[0.0 for x in range(28)] for y in range(28)]

            pmin = float("inf")
            pmax = float("-inf")
            for i in range(28):
                for j in range(28):
                    prob = self.data[expectedClass].getPixelProb(i,j,1)
                    if prob < pmin:
                        pmin = prob
                    if prob > pmax:
                        pmax = prob
                    expectedCount[27-i][j] = prob
            self.printHeatMap(expectedCount,pmin,pmax,"Digit : " + str(expectedClass))

            for i in range(28):
                for j in range(28):
                    prob = self.data[mapClass].getPixelProb(i,j,1)
                    if prob < pmin:
                        pmin = prob
                    if prob > pmax:
                        pmax = prob
                    likelyCount[27-i][j] = prob

            self.printHeatMap(likelyCount,pmin,pmax,"Digit : " + str(mapClass))

            oddsImage = [[0.0 for x in range(28)] for y in range(28)]
            pmin = float("inf")
            pmax = float("-inf")
            for a in range(28):
                for b in range(28):
                    prob = math.log(self.data[mapClass].getPixelProb(a,b,1)) - math.log(self.data[expectedClass].getPixelProb(a,b,1))
                    if prob < pmin:
                        pmin = prob
                    if prob > pmax:
                        pmax = prob
                    oddsImage[27-a][b] = prob
            self.printHeatMap(oddsImage,pmin,pmax,"Odds Ratio: "  + str(mapClass) + " And " + str(expectedClass))


    def printHeatMap(self,heatimage,min,max,label):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title('Heatmap of ' + str(label))
        plotly_fig = tls.mpl_to_plotly( fig )
        trace = dict(z=heatimage, type="heatmap", zmin=min, zmax=max)
        plotly_fig['data'] = [trace]
        plotly_fig['layout']['xaxis'].update({'autorange':True})
        plotly_fig['layout']['yaxis'].update({'autorange':True})

        plot_url = py.plot(plotly_fig, filename='heatmap' + str(label))

def parse_args():
    parser = argparse.ArgumentParser(description="Run Digit Classifier")
    parser.add_argument("--train", nargs=2,type=str, help="Digit Training Files (images + labels)", required=True)
    parser.add_argument("--test", nargs=2,type=str, help="Digit Testing Files (images + labels)", required=True)
    args = parser.parse_args()
    return args.train, args.test

if __name__ == "__main__":
    dtrain, dtest = parse_args()
    trained = digitBayes(dtrain[0],dtrain[1])
    trained.test(dtest[0],dtest[1])
