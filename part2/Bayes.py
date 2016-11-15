import math
import argparse
from collections import defaultdict

class documentClassifier:
	# Inits and trains class
	# 1 for Positive, -1 for Negative
	def __init__(self, trainingFile):
		self.data = {'1': defaultdict(int), '-1': defaultdict(int)}
		self.probability = {'1': defaultdict(float), '-1': defaultdict(float)}
		self.priors = {'1': 0.0, '-1': 0.0}
		self.vocabulary = []

		total = 0
		with open(trainingFile, 'r') as file:
			for line in file:
				dataFile = line.strip().split()
				self.priors[dataFile[0]] += 1
				total += 1

				for x in dataFile[1:]:
					word, value = x.split(':')
					self.data[dataFile[0]][word] += int(value)

		for i in self.priors:
			self.priors[i] /= total

		# For total vocabulary.  I.E. |V|
		for label in self.data:
			tmpDict = self.data[label]
			for word in tmpDict:
				if word not in self.vocabulary:
					self.vocabulary.append(word)

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
				totalNumLabelWords += wordDict[word]

			for word in wordDict:
				self.probability[label][word] = float(wordDict[word] + 1) / float(totalNumLabelWords + len(self.vocabulary))

			for word in self.vocabulary:
				if word not in wordDict:
					self.probability[label][word] = float(1) / float(totalNumLabelWords + len(self.vocabulary))


	# Return 1 for Positive and -1 for Negative, 0 for Confused
	# Takes in the label, calculated priors and total count, computes classification and returns the result
	def multinomialBayes(self, fileData):
		# Compute breakdown of labels and their probabilities
		label_likelihood = {'1': 0.0, '-1': 0.0}

		for i in self.priors:
			label_likelihood[i] = self.priors[i]

		data = fileData.split()

		for i in data[1:]:
			word, value = i.split(':')
			if word in self.vocabulary:
				for label in label_likelihood:
					label_likelihood[str(label)] += (float(value) * math.log10(self.probability[label][word]))

		# Case of equal probabilities?
		if label_likelihood['1'] > label_likelihood['-1']:
			return 1
		else:
			return -1

	def bernoulliBayes(self, fileData):
		# Compute breakdown of labels and their probabilities
		label_likelihood = {'1': 0.0, '-1': 0.0}

		for i in self.priors:
			label_likelihood[i] = self.priors[i]

		data = fileData.split()

		


def parse_arguments():
	parser = argparse.ArgumentParser(description="Run Text Document Classifier")
	parser.add_argument("--train", type=str, help="Training File", required=True)
	parser.add_argument("--test", type=str, help="Testing File", required=True)
	args = parser.parse_args()
	return args.train, args.test

if __name__ == "__main__":
	trainingFile, testFile = parse_arguments()

	tester = documentClassifier(trainingFile)

	rateMultinomial = 0.0
	rateBernoulli = 0.0
	total = 0

	with open(testFile, 'r') as file:
		for line in file:
			label, rest = line.split(' ', 1)
			total += 1
			# print label
			# print tester.multinomialBayes(line)
			if label == str(tester.multinomialBayes(line)):
				rateMultinomial += 1

	print rateMultinomial
	rateMultinomial /= float(total) * 0.01

	print 'Num Files: ' + str(total)
	print 'Accuracy Multinomial: ' + str(rateMultinomial)