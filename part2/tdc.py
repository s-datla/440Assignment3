import argparse
import math
from collections import defaultdict

class tdc:

    # inits and in doing so trains the class on ftrain
    # 1 for Positive, -1 for Negative
    def __init__(self, ftrain):
        self.data = { '1' :  defaultdict(int), '-1':  defaultdict(int)}
        self.prob = { '1' :  defaultdict(float), '-1':  defaultdict(float)}

        with open(ftrain, 'r') as file:
            for line in file:
                line = line.strip()
                info = line.split()
                label = info[0]

                for i in info[1:]:
                    word, val = tuple(i.split(':'))
                    self.data[ label ][ word ] += int(val)

        for label in self.data:
            nwords = 0
            wdict = self.data[label]
            # get number of words in label
            for word in wdict:
                nwords += wdict[ word ]

            # set probs
            for word in wdict:
                self.prob[ label ][ word ] = wdict[ word ] / nwords

    # returns a 1 or a -1 based on what the system thinks
    # returns 0 if indeterminate
    # inp doesn't include the 'label' from the file, else same
    def test_input(self, inp):
        prob_1 = 0.5 #init to P(class)
        prob_n1 = 0.5

        info = inp.split()
        for i in info:
            word, val = tuple(i.split(':'))
            prob_1 *= math.pow((self.prob[ '1' ][ word ]), float(val))
            prob_n1 *= math.pow((self.prob[ '-1' ][ word ]), float(val))

        if prob_1 > prob_n1:
            return '1'
        elif prob_1 < prob_n1:
            return '-1'
        else:
            return '0'

    # similar to test_input but uses brenoulli's madness
    def testb_input(self, input):
        prob_1 = 0.5
        prob_n1 = 0.5

        info = input.split()
        for i in info:
            word, val = tuple(i.split(':'))
            if self.data['1'][word] == 0:
                prob_1 *= 0
            if self.data['-1'][word] == 0:
                prob_n1 *= 0

        if prob_1 > prob_n1:
            return '1'
        elif prob_1 < prob_n1:
            return '-1'
        else:
            return '0'

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run Text Document Classifier")
    parser.add_argument("--train", type=str, help="Training File", required=True)
    parser.add_argument("--test", type=str, help="Testing File", required=True)
    args = parser.parse_args()
    return args.train, args.test

if __name__ == "__main__":
    ftrain = "E:\Git\\440Assignment3\part2\\fisher_2topic\\fisher_train_2topic.txt"
    ftest = "E:\Git\\440Assignment3\part2\\fisher_2topic\\fisher_test_2topic.txt"#parse_arguments()
    tester = tdc(ftest)

    rate_norm = 0.0
    rate_btst = 0.0
    count = 0

    with open(ftest, 'r') as file:
        for line in file:
            count += 1

            line = line.strip()
            label, rest = tuple(line.split(' ', 1))

            if label == tester.test_input(rest):
                rate_norm += 1

            if label == tester.testb_input(rest):
                rate_btst += 1

    rate_norm /= count
    rate_btst /= count

    print('Num Files: ', count)
    print('Accuracy Norm: ', rate_norm)
    print('Accuracy BTst: ', rate_btst)
