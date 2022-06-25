# NLP Group Assignment

## Main libraries used:
* [PySpellChecker](https://github.com/barrust/pyspellchecker)
* [SymSpell](https://github.com/wolfgarbe/symspell)
* [editdistpy](https://github.com/mammothb/editdistpy)
* [TextBlob](https://textblob.readthedocs.io/en/dev/)
* [NLTK N-gram](https://www.geeksforgeeks.org/n-gram-language-modelling-with-nltk/)

## Primary techniques used:
* Peter Norvig's [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance) algorithm
* [Frequency Distribution](https://gist.github.com/amitrani6/7f85394e7ccbec14f51968d5ac129dd7)
* [N-Gram](https://en.wikipedia.org/wiki/N-gram)

# Quick Guide

## Prerequisites
* Python 3.6+
* Java 6 and above


## Steps

* pip install tkmacosx (for mac)
* pip install textblob
* ~~pip install pyspellchecker~~ (Outdated)
* pyspellchecker
  * git clone https://github.com/barrust/pyspellchecker.git
  * cd pyspellchecker
  * python setup.py install
* python -m pip install -U symspellpy


## Common problem:
* SSL certificate error (urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate)
* Refer to following link for more information: https://stackoverflow.com/a/58525755
