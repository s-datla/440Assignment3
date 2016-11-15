import math
import argparse
import sys
from collections import defaultdict, Counter

class documentClassifier:
	# Inits and trains class
	# 1 for Positive, -1 for Negative
	def __init__(self, trainingFile):
		self.data = {'1': defaultdict(int), '-1': defaultdict(int)}
		self.probability = {'1': defaultdict(float), '-1': defaultdict(float)}
		self.priors = {'1': 0.0, '-1': 0.0}
		self.vocabulary = []
		self.positiveVocab = []
		self.negativeVocab = []
		self.positiveLikelihood = defaultdict(float)
		self.negativeLikelihood = defaultdict(float)

		total = 0
		with open(trainingFile, 'r') as file:
			for line in file:
				dataFile = line.strip().split()
				self.priors[dataFile[0]] += 1
				total += 1

				for x in dataFile[1:]:
					word, value = x.split(':')
					self.data[dataFile[0]][word] += 1

		for i in self.priors:
			self.priors[i] /= total

		# For total vocabulary.  I.E. |V|
		for label in self.data:
			tmpDict = self.data[label]
			for word in tmpDict:
				if word not in self.vocabulary:
					self.vocabulary.append(word)

				if label == '1':
					if word not in self.positiveVocab:
						self.positiveVocab.append(word)
				else:
					if word not in self.negativeVocab:
						self.negativeVocab.append(word)

		'''
		Calculates each probability for each word given a specific label
		Calculation is done as follows:
			(occurrence of word in label + 1) / (all words in label + length of vocab)
			+1 and + length of vocab is done for Laplacian smoothing
		''' 
		for label in self.data:
			totalNumLabelWords = 0
			wordDict = self.data[label]
			for word in wordDict:
				totalNumLabelWords += 1

			for word in wordDict:
				self.probability[label][word] = wordDict[word] 
				#self.probability[label][word] = (float)(self.data[label][word] + 10) / float(totalNumLabelWords) #float(wordDict[word] + 10) / float(totalNumLabelWords + 10 * len(self.vocabulary))

			for word in self.vocabulary:
				if word not in wordDict:
					self.probability[label][word] = 2000#float(10) / float(totalNumLabelWords + 10 * len(self.vocabulary))


	# Return 1 for Positive and -1 for Negative, 0 for Confused
	# Takes in the label, calculated priors and total count, computes classification and returns the result
	def bernoulliBayes(self, fileData):
		# Compute breakdown of labels and their probabilities
		label_likelihood = {'1': 0.0, '-1': 0.0}

		for i in self.priors:
			label_likelihood[i] = self.priors[i]

		data = fileData.split()

		for i in data[1:]:
			word, value = i.split(':')

			if word in self.vocabulary:
				for label in label_likelihood:
					label_likelihood[str(label)] += float(math.log10(self.probability[label][word]))
					if label == '1':
						self.positiveLikelihood[word] += float(math.log10(self.probability[label][word]))
						if word in self.positiveVocab:
							self.positiveVocab.remove(word)
					else:
						self.negativeLikelihood[word] += float(math.log10(self.probability[label][word]))
						if word in self.negativeVocab:
							self.negativeVocab.remove(word)

		for word in self.positiveVocab:
			label_likelihood['1'] += float(1 - math.log10(self.probability['1'][word]))
		for word in self.negativeVocab:
			label_likelihood['-1'] += float(1 - math.log10(self.probability['-1'][word]))

		# Case of equal probabilities?
		if label_likelihood['1'] > label_likelihood['-1']:
			return 1
		else:
			return -1

def parse_arguments():
	parser = argparse.ArgumentParser(description="Run Text Document Classifier")
	parser.add_argument("--train", type=str, help="Training File", required=True)
	parser.add_argument("--test", type=str, help="Testing File", required=True)
	args = parser.parse_args()
	return args.train, args.test

if __name__ == "__main__":
	trainingFile, testFile = parse_arguments()

	tester = documentClassifier(trainingFile)

	rateBernoulli = 0.0
	total = 0
	rateOne = 0.0
	totalOne = 0
	rateMinus = 0.0
	totalMinus = 0
	confusionMatrix = [[0 for i in range(2)] for j in range(2)]

	with open(testFile, 'r') as file:
		for line in file:
			label, rest = line.split(' ', 1)
			total += 1
			if label == '1':
				totalOne += 1
			elif label == '-1':
				totalMinus += 1
			if label == str(tester.bernoulliBayes(line)):
				rateBernoulli += 1
				if label =='1':
					rateOne += 1
					confusionMatrix[0][0] += 1
				elif label == '-1':
					rateMinus += 1
					confusionMatrix[1][1] += 1
			else:
				if label == '1':
					confusionMatrix[0][1] += 1
				elif label == '-1':
					confusionMatrix[1][0] += 1

	for i in range(len(confusionMatrix)):
		confusionMatrix[i][0] /= float(totalOne)
		confusionMatrix[i][1] /= float(totalMinus)


	rateBernoulli /= float(total) * 0.01
	rateOne /= float(totalOne) * 0.01
	rateMinus /= float(totalMinus) * 0.01

	print 'Num Files: ' + str(total)
	print 'Accuracy 1 Label: ' + str(rateOne)
	print 'Accuracy -1 Label: ' + str(rateMinus)
	print 'Accuracy Bernoulli: ' + str(rateBernoulli)

	print "Confusion Matrix: "
	for i in range(len(confusionMatrix)):
		for j in range(len(confusionMatrix)):
			sys.stdout.write(" {0:.4f} ".format(confusionMatrix[i][j]))
		sys.stdout.write("\n")
		sys.stdout.flush()

	d = Counter(tester.positiveLikelihood)
	top10Positive = d.most_common(10)
	d = Counter(tester.negativeLikelihood)
	top10Negative = d.most_common(10)
	print "\nTop 10 Positive Likelihoods"
	print top10Positive
	print "\nTop 10 Negative Likelihoods"
	print top10Negative

	oddsRatioPTN = defaultdict(float)
	for i in tester.positiveLikelihood:
		oddsRatioPTN[i] = tester.positiveLikelihood[i] / tester.negativeLikelihood[i]
	d = Counter(oddsRatioPTN)
	print "\n Top 10 Positive / Negative Odds Ratio"
	print d.most_common(10)

	oddsRatioNTP = defaultdict(float)
	for i in tester.negativeLikelihood:
		oddsRatioNTP[i] = tester.negativeLikelihood[i] / tester.positiveLikelihood[i]
	d = Counter(oddsRatioNTP)
	print "\n Top 10 Negative / Positive Odds Ratio"
	print d.most_common(10)