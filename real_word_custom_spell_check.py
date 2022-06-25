# A file that is used to load related corpus files and real word edit distance functions.
import itertools
import re
import os
import random
from collections import Counter

from nltk.util import ngrams
from urllib.request import urlopen

global data
correct_words = []
wrong_words = []
corpus_words = Counter()
bigrams = Counter()
correct_word_set = []
wrong_word_set = []
word_set = []


# Main Reference: https://medium.com/analytics-vidhya/real-word-spell-correction-c64a3a02c64d
# Load corpus in order for real-word spell correction
def load_local_corpus_data():
    global data
    global correct_words
    global wrong_words
    data = open('datasets/big.txt', encoding='utf-8').read()
    data = data.replace('\n', ' ').replace('\t', ' ').replace('-', ' ').replace('—', ' ')
    data = data.replace('_', '')
    data = re.sub(r'[^\w\s]', '', data)
    data = data.lower().strip().split(' ')
    data = list(filter(None, data))


def load_online_corpus_data(url):
    global correct_words
    global wrong_words

    r = urlopen(url)

    for line in r:
        string = str(line)
        string = string[2:]  # Remove b'
        string = string[:-3]  # Remove \n'
        # character of word in corpus is set pr
        if len(string) >= 3 and '_' not in string:
            if string.startswith(tuple(['$'])):
                string = string[1:]  # Remove $
                string = " ".join(re.findall("[a-zA-Z(\')]+", string))  # Remove numbers
                string = string.strip()  # Remove spaces
                correct_words.append(string)
            else:
                wrong_words.append(string)


load_local_corpus_data()

corpus_words = Counter(data)


def p(word, n=sum(corpus_words.values())):
    # Returns probability of a word in vocabulary.
    return corpus_words[word] / n


def edit_distance(str1, str2, m, n):
    dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j

            elif j == 0:
                dp[i][j] = i

            elif str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]

            else:
                dp[i][j] = min(dp[i][j - 1] + 1,  # Insert
                               dp[i - 1][j] + 1,  # Remove
                               dp[i - 1][j - 1] + 1)  # Replace

    return dp[m][n]


def word_candidates(word):
    # Returns the words that are edit distance 0,1 or 2 away from the given word. Inspired from Peter Norvig
    ed_0 = set()
    ed_1 = set()
    ed_2 = set()
    for w in corpus_words:
        ed = edit_distance(word, w, len(word), len(w))
        if ed > 2:
            continue
        elif ed == 0:
            ed_0.add(w)
        elif ed == 1:
            ed_1.add(w)
        elif ed == 2:
            ed_2.add(w)
    return [ed_0, ed_1, ed_2, {word}]


def closest_word(word):
    # Chooses the closest word according to their frequency. Highest priority given to words with the least edit
    # distance.
    for i in word_candidates(word):
        if i:
            return max(i, key=p)


bigrams = Counter(ngrams(data, 2))


# Identified problem, you cannot analyze any word that is too unknown in the corpus. (Example: lmao, lol, etc.)
def bigram_prob(sent):
    out = p(sent[0])
    for i in range(1, len(sent)):
        out *= bigrams[(sent[i - 1], sent[i])] / corpus_words[sent[i - 1]]
    return out


def sent_all_candidates(sent):
    candidates = []
    sent = sent.split()
    word_present = [s in corpus_words for s in sent]
    if all(word_present):
        for i in sent:
            wc = word_candidates(i)[1]
            wc.add(i)
            candidates.append(list(wc))
        candidates = list(itertools.product(*candidates))
    else:
        idx = word_present.index(0)
        selected_words = word_candidates(sent[idx])[1]
        for i in selected_words:
            l = sent.copy()
            l[idx] = i
            candidates.append(l)
    return candidates


def sent_candidates(sent):
    candidates = []
    sent = sent.split()
    word_present = [s in corpus_words for s in sent]
    if all(word_present):
        candidates.append(sent)
        for i in range(len(sent)):
            words = word_candidates(sent[i])[1]
            for j in words:
                l = sent.copy()
                l[i] = j
                candidates.append(l)
    else:
        idx = word_present.index(0)
        words = word_candidates(sent[idx])[1]
        for i in words:
            l = sent.copy()
            l[idx] = i
            candidates.append(l)
    return candidates


def closest_all_sent(sent):
    results = []
    for i in sent_all_candidates(sent):
        if bigram_prob(i) > 0:
            # print(i, ' Probability = ', bigram_prob(i))
            results.append(' '.join(i))
    # return ' '.join(max(sent_candidates(sent), key=bigram_prob))
    return results


def closest_sent(sent):
    results = []
    for i in sent_candidates(sent):
        if bigram_prob(i) > 0:
            # print(i, ' Probability = ', bigram_prob(i))
            results.append(' '.join(i))
    # return ' '.join(max(sent_candidates(sent), key=bigram_prob))
    return results


def save_correct_words():
    with open('datasets/correct_words.txt', 'w') as f:
        for i in correct_words:
            f.write(i + '\n')


def save_wrong_words():
    with open('datasets/wrong_words.txt', 'w') as f:
        for i in wrong_words:
            f.write(i + '\n')


def initialize():
    global correct_words
    global wrong_words
    global correct_word_set
    global wrong_word_set
    global word_set
    global corpus_words
    global data
    global bigrams

    if os.path.isfile("datasets/correct_words.txt") and os.path.isfile("datasets/wrong_words.txt"):
        correct_words = open("datasets/correct_words.txt", "r").read().splitlines()
        wrong_words = open("datasets/wrong_words.txt", "r").read().splitlines()
    else:
        # Load online corpus data, correct words and wrong words
        load_online_corpus_data('https://www.dcs.bbk.ac.uk/~ROGER/missp.dat')
        load_online_corpus_data('https://www.dcs.bbk.ac.uk/~ROGER/holbrook-missp.dat')
        load_online_corpus_data('https://www.dcs.bbk.ac.uk/~ROGER/aspell.dat')
        load_online_corpus_data('https://www.dcs.bbk.ac.uk/~ROGER/wikipedia.dat')

        save_correct_words()
        save_wrong_words()

    correct_word_set = [(word, True) for word in correct_words[:100]]
    wrong_word_set = [(word, False) for word in wrong_words[:100]]
    word_set = correct_word_set + wrong_word_set
    random.shuffle(word_set)

    print('len(correct_words): ', len(correct_words))
    print('len(wrong_words): ', len(wrong_words))
    print('len(data): ', len(data))
    print('correct_word_set: ', correct_word_set[:10])
    print('wrong_word_set: ', wrong_word_set[:10])
    print('len(word_set): ', len(word_set))

    # print(closest_word('acress'))
    # print(closest_all_sent('two of thew'))
    # print(closest_sent('i have an apply'))


initialize()
