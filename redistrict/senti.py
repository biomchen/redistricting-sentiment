"""
A class to analyze sentiments of the comments from LOU redistricting survey.
The SentiWordNet 3.0 dataset has been preprocessed before the analyses
by removing all description at the beginning of the data as well as
empty space in the end of it.
Building a SentiWordNet is adopted from Anela Chan with some modifications:
https://github.com/anelachan/sentimentanalysis
"""
import re


class SentimentAnalysis:

    def __init__(self, base='SentiWordNet.txt'):
        self.base = base
        self.swn_all_words = {}
        self.build_swn(base)

    def build_swn(self, base):
        records = [line.split('\t') for line in open(self.base)]
        for rec in records:
            word = rec[4].split('#')[0]
            true_score = float(rec[2]) - float(rec[3])
            if word not in self.swn_all_words:
                self.swn_all_words[word] = {}
                self.swn_all_words[word]['score'] = true_score

    def weighting(self, method, scores_list):
        if method == 'arithmetic':
            scores = 0
            for score in scores_list:
                scores += score
            weighted_sum = scores/len(scores_list)
        elif method == 'geometric':
            weighted_sum = 0
            num = 1
            for score in scores_list:
                weighted_sum += (score * (1/2**num))
                num += 1
        elif method == 'harmonic':
            weighted_sum = 0
            num = 2
            for score in scores_list:
                weighted_sum += (score * (1/num))
                num += 1
        return weighted_sum

    def clean_text(self, filename):
        if '.txt' in filename or '.csv' in filename:
            texts_clean_all = []
            data = open(filename, encoding='utf8')
            texts = [line.rsplit() for line in data]
            try:
                for line in texts:
                    for text in line:
                        text_clean = text.lower()
                        text_clean = re.sub(r'[.?!;:@#$%^&*()-_+={}[]|\>/’"]',
                                           '',
                                           text_clean)
                        texts_clean_all.append(text_clean)
                return texts_clean_all
            except Exception:
                return "name error"
        else:
            try:
                text_clean = filename.lower()
                text_clean = re.sub(r'[.?!;:@#$%^&*()-_+={}[]|\>/’"]',
                                   '',
                                   text_clean).split()
                return text_clean
            except Exception:
                return "name error"

    def score_text(self, text):
        scores_all = []
        scores = 0
        total_count = 0
        positive_count = 0
        negative_count = 0
        final_score = {}
        methods = ['arithmetic', 'geometric', 'harmonic']
        text_set = set(self.clean_text(text))
        key_set = set(self.swn_all_words.keys())

        for word in text_set.intersection(key_set):
            single_score = self.swn_all_words[word]['score']
            if single_score > 0:
                positive_count += 1
            elif single_score < 0:
                negative_count += 1
            total_count += 1
            scores_all.append(single_score)

        if total_count >= 1:
            for method in methods:
                score = self.weighting(method, scores_all)
                final_score[method] = round(score, 3)
            positive = round(positive_count/total_count, 3)
            negative = round(negative_count/total_count, 3)
            neutral = 1 - positive - negative
            return (list(final_score.values()),
                    positive,
                    negative,
                    neutral,
                    scores_all)
        else:
            return 0
