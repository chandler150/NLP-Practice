#*************************************************************************
#*                  Laboratory 3 PCFG Maker                              *
#*                  By: Chandler Jones                                   *
#*                  Date: February 10th, 2020                            *
#*                  For: Dr. Foaad Khosmood                              *
#*************************************************************************
import time
from nltk import *
import numpy as np
import nltk, copy, random, sys, re
#nltk.download('brown')
#nltk.download('treebank')
from nltk.corpus import treebank
import json

#*************************************************************************
#GOOGLE COLAB
#*************************************************************************
# How many files are in the NLTK sample of the Penn Treebank?
def google():
    print("Total number of files: ", len(treebank.fileids()))

    # What are the names of the files?
    print("Names of the files: ", treebank.fileids())

    treebank_file = 'wsj_0003.mrg'
    words = treebank.words(treebank_file)
    sents = treebank.sents(treebank_file)
    print("Some of the words in this file: ",words)
    print("Number of words: ",len(words), "\nNumber of sentences: ",len(sents))
    print("First sentence: ", sents[0])

    #Second by tagged words
    treebank_file = 'wsj_0001.mrg'
    tagged_words = treebank.tagged_words(treebank_file)
    print("Some of the tagged words in this file: ",tagged_words)
    print("Number of tagged words: ",len(tagged_words))

    #Finally by constituency parse trees

    treebank_file = 'wsj_0003.mrg'
    trees = treebank.parsed_sents(treebank_file)
    print("Some of the parse trees: ",trees)
    print("Number of trees in this file: ",len(trees))
    print("First full parse tree:\n", trees[0])
    text = trees[0][0].productions()

    print("\n\n*****\n",text)

#*************************************************************************

#A PCFG of Penn Treebank (NLTK supplied sample) using the exact tags.
#Include the code that generates it and the results itself in a .txt file,
#which you may also include as an appendix in your PDF. (60%)
def pcfg():
    productions = []
    wdict = {}
    for i in treebank.fileids():
        words = treebank.words(i)
        sents = treebank.sents(i)
        tagged_words = treebank.tagged_words(i)
        trees = treebank.parsed_sents(i)
        for i in trees:
            i.collapse_unary(collapsePOS=False)
            # tree.chomsky_normal_form(horzMarkov=2)
            productions += i.productions()
            for rule in i.productions():
                try:
                    wdict[rule] += 1
                except KeyError:
                    wdict[rule] = 1
    ddd = {}
    rulesum = sum(wdict.values())
    for key in sorted(wdict):
        ddd[str(key)] = str(wdict[key] / rulesum)
    with open('PCFG_Output.txt', 'w') as f:
        f.write("""PCFG:\n\n""")
        for key, values in ddd.items():
            la = key.ljust(40, ' ')
            f.write(f"{la}|     {values}\n")
        f.write("""\n\nCODE:\n\n
    productions = []
    wdict = {}
    for i in treebank.fileids():
        words = treebank.words(i)
        sents = treebank.sents(i)
        tagged_words = treebank.tagged_words(i)
        trees = treebank.parsed_sents(i)
        for i in trees:
            i.collapse_unary(collapsePOS=False)
            #tree.chomsky_normal_form(horzMarkov=2)
            productions += i.productions()
            for rule in i.productions():
                try:
                    wdict[rule] += 1
                except KeyError:
                    wdict[rule] = 1
    ddd = {}
    rulesum = sum(wdict.values())
    for key in wdict:
        ddd[str(key)] = str(wdict[key]/rulesum)
    with open('PCFG_Output.txt', 'w') as f:
        f.write("PCFG:")
        for key, values in ddd.items():
            la = key.ljust(40, ' ')
            f.write(f"{la}|     {values}")
        f.write(f"{code}")
""")
    print("PCFG:",len(wdict))
    return
#A reduced grammar version (find a small standard grammar,
#and convert the big one to it by converting the specific constituencies to general
#ones, like VB* to VB. (10%)
def redgram():

    return
#Do two reduced sets.
def dotwo():
    vanilla = vanilla()
    further = evenfurther()
#One where the only allowed nonterminals are "vanilla" Penn Treebank nonterminalslike "NNP" and "VBZ".
#All symbols with ^ and "-" or "_" need to be collapsed into their vanilla versions.
def vanilla():
    wdict = {}
    for i in treebank.fileids():
        trees = treebank.parsed_sents(i)
        for i in trees:
            i.collapse_unary(collapsePOS=False)
            # tree.chomsky_normal_form(horzMarkov=2)
            productions = i.productions()
            for rule in productions:
                rule = str(rule)
                rule = re.sub('-NONE-', 'NONE', rule)
                rule = re.sub('\s-([A-Z]+)-', ' \\1', rule)
                rule = re.sub('[-_*+^][A-Z]{2,}|[-_*+=^][0-9]+|[-_*+^][A-Z]\b',
                              '', rule)
                try:
                    wdict[rule] += 1
                except KeyError:
                    wdict[rule] = 1

    ddd = {}
    rulesum = sum(wdict.values())
    for key in sorted(wdict):
        ddd[str(key)] = str(wdict[key] / rulesum)
    with open('Vanilla_Output.txt', 'w') as f:
        f.write("""PCFG:\n\n""")
        for key, values in ddd.items():
            la = key.ljust(40, ' ')
            f.write(f"{la}|     {values}\n")
        f.write("""\n\nCODE:\n\n""")

    return
#The second is even further reduced by collapsing various subforms for nouns and verbs (and others)
#into a single version "N" or "V" for example.
def evenfurther():
    wdict = {}
    for i in treebank.fileids():
        trees = treebank.parsed_sents(i)
        for i in trees:
            i.collapse_unary(collapsePOS=False)
            # tree.chomsky_normal_form(horzMarkov=2)
            productions = i.productions()
            for rule in productions:
                rule = str(rule)
                rule = re.sub('-NONE-', 'NONE', rule)
                rule = re.sub('\s-([A-Z]+)-', ' \\1', rule)
                rule = re.sub('[-\^_*+][A-Z]{2,}\b|[-\^_*+=][0-9]+|[-\^_*+][A-Z]\b', '', rule)
                rule = re.sub('([A-Z])[A-Z]+', '\\1', rule)

                try:
                    wdict[rule] += 1
                except KeyError:
                    wdict[rule] = 1

    ddd = {}
    rulesum = sum(wdict.values())
    for key in sorted(wdict):
        ddd[str(key)] = str(wdict[key] / rulesum)
    with open('Subform_Output.txt', 'w') as f:
        f.write("""PCFG:\n\n""")
        for key, values in ddd.items():
            la = key.ljust(40, ' ')
            f.write(f"{la}|     {values}\n")
        f.write("""\n\nCODE:\n\n""")

    print("EVEN_FURTHER:", len(wdict))

    return
#No need to turn in the terminal / lexicon production rules,
#just the NT -> NT * ones is fine.

#Lexicalized version of (1).
#Output only the phrase rules, ignore the lexicon rules.
#Add headwords to every NT, but adding a "-" followed by the word. (10%)

def lexicalized():
    productions = []
    wdict = {}
    for i in treebank.fileids():
        words = treebank.words(i)
        sents = treebank.sents(i)
        tagged_words = treebank.tagged_words(i)
        trees = treebank.parsed_sents(i)
        for i in trees:
            lexical = downtree(i)
        #print(lexical.productions())
    return

def downtree(trees):
    lexical = []
    for i in trees:
        if isinstance(i, str):
            trees = (trees.label()+'-'+i)
            print(trees+ ' -> ' + i)
            return (trees+ ' -> ' + i)
        downtree(i)
    return (trees)

def main():
    #google()
    pcfg()
    vanilla()
    evenfurther()
    lexicalized()
if __name__ == "__main__":
    main()