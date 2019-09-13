"""
A class to analyze sentiments of the comments from LOU redistricting survey.

The SentiWordNet 3.0 dataset has been preprocessed before the analyses
by removing all description at the beginning of the data as well as
empty space in the end of it.

Building a SentiWordNet is adopted from Anela Chan with some modifications:
https://github.com/anelachan/sentimentanalysis

"""

import re

class SentiAnalysis:

    def __init__(self, base = 'SentiWordNet.txt'):

        self.base = base
        self.swnAll = {}
        self.makeSWN(base)

    def makeSWN(self, base):

        records = [line.split('\t') for line in open(self.base)]

        for rec in records:
            word = rec[4].split('#')[0]
            pScore = rec[2]
            nScore = rec[3]

            if word not in self.swnAll:
                self.swnAll[word] = {}
                self.swnAll[word]['score'] = float(pScore) - float(nScore)

    def weighting(self, m, s):

        if m == 'arithmetic':
            scores = 0
            for score in s:
                scores += score
            weighted_sum = scores/len(s)
        elif m == 'geometric':
            weighted_sum = 0
            num = 1
            for score in s:
                weighted_sum += (score * (1/2**num))
                num += 1
        elif m == 'harmonic':
            weighted_sum = 0
            num = 2
            for score in s:
                weighted_sum += (score *(1/num))
                num +=1
        return weighted_sum

    def cleanText(self, filename):

        if '.txt' in filename or '.csv' in filename:
            textsCleanAll = []
            texts = [line.rsplit() for line in open(filename, encoding = 'utf8')]
            try:
                for line in texts:
                    for text in line:
                        textClean = text.lower()
                        textClean = re.sub('[.?!;:@#$%^&*()-_+={}[]|\>/’"]', '', textClean)
                        textsCleanAll.append(textClean)
                return textsCleanAll
            except:
                return "name error"
        else:
            try:
                textClean = filename.lower()
                textClean = re.sub('[.?!;:@#$%^&*()-_+={}[]|\>/’"]', '', textClean).split()
                return textClean
            except:
                return "name error"

    def scoreText(self, text):

        scoresAll = []
        scores = 0
        count = 0
        pCount = 0
        nCount = 0
        finalScore = {}

        methodNames = ['arithmetic', 'geometric', 'harmonic']

        textSet = set(self.cleanText(text))
        keySet = set(self.swnAll.keys())

        for word in textSet.intersection(keySet):
            singleScore = self.swnAll[word]['score']
            if singleScore > 0:
                pCount += 1
            elif singleScore < 0:
                nCount += 1

                count += 1
                scoresAll.append(singleScore)

        if count >= 1:
            for method in methodNames:
                finalScore[method] = round(self.weighting(method, scoresAll), 3)

            positive = round(pCount/count, 3)
            negative = round(nCount/count, 3)
            neutral = 1 - positive - negative

            return (list(finalScore.values()), positive, negative, neutral, scoresAll)
        else:
            return 0
