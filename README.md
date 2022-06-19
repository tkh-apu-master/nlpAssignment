# NLP Group Assignment

## Main libraries used:
* [PySpellChecker](https://github.com/barrust/pyspellchecker)
* [SymSpell]()

## Primary techniques used:
* Peter Norvig's [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance) algorithm
* Frequency Distribution
* [N-Gram](https://en.wikipedia.org/wiki/N-gram)
* 

# Quick Guide

## Prerequisites
* Python 3.6+
* Java 6 and above


## Steps

* pip install tkmacosx (for mac)
* pip install textblob
* pip install pyspellchecker (DONt use this command)
* git clone https://github.com/barrust/pyspellchecker.git
* cd pyspellchecker
* python setup.py install
* python -m pip install -U symspellpy
* pip install --upgrade 3to2
* pip install --upgrade language-check

## Common problem:
* SSL certificate error (urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate)
* Refer to following link for more information: https://stackoverflow.com/a/58525755
