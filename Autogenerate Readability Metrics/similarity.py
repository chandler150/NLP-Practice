"""
*************************************************
* similarity.py by Chandler Jones              *
* For CSC 482, Dr. Foaad Khosmood               *
* For Laboratory 2, part 2                     *
* In our Natural Language Processing Class      *
* January 23rd, 2020                            *
*************************************************
"""


""" Write a program called similarity.py that take in two command line argument (arg1, arg2).

    If arg1 and arg2 are wordnet concepts (c1, c2),
    which are denoted by having two periods in each of them (example: 'dog.n.01', 'eat.v.01'),
    then calculate five different similarity distances between the two concepts.
    If the two arguments are two regular words
    (all alphabetic or underscore, example: 'dog', 'cat', 'run')
    then first derive the most common concepts (synsets from each),
    and then calculate the same five different similarity distances.

    The similarity distances are from figure C.7 of page 11 in JM Appendix C
    (Links to an external site.).

    Print each similarity metric on a line by itself,
    followed by ": " followed by the actual value.
    You must calculate them yourself in functions in your code.
    You may use any tool to get syllables. Use WordNet bundled by NLTK. """
from nltk import *
import sys
import math
from nltk.corpus import wordnet as wn
from nltk.corpus import brown
from nltk.corpus import stopwords
import re
import downtree
import time

path_sim = 0
resnik = 0
lin = 0
jc = 0
extended = 0

def main():
    arguments = get_args()
    arguments = syngetter(arguments)
    if arguments == "First word not in Wordnet. Try another noun.":
        print("\n\n"+"First word not in Wordnet. Try another noun."+ "\n\n")
        return
    if arguments == "Second word not in Wordnet. Try another noun.":
        print("\n\n"+ "Second word not in Wordnet. Try another noun." + "\n\n")
        return

    word1 = arguments[0]
    word2 = arguments[1]
    path_sim = Path_Similarity(word1,word2)
    nameLCS = path_sim[1]

    # If nameLCS == word1, it means the same word was entered twice, and function falls to else:
    if not nameLCS == word1:
        resnik = Resnik(nameLCS)
        lcsc1c2 = resnik[1]
        lin = Lin(word1,word2,lcsc1c2)
        Pc1 = lin[1]
        Pc2 = lin[2]
        jc = JC(lcsc1c2, Pc1, Pc2)
        extended = Extended_Lesk(word1,word2)

    # Else still gives extended lesk, but gives 1 for all other values.
    else:
        extended = Extended_Lesk(word1, word2)
        resnik =[0]
        resnik[0] = 1
        lin=[0]
        lin[0] = 1
        jc= 1

    """Once everything is counted, print in the way he wants it"""

    print(  "\n" + "\n" +
        "Path Similarity:  " + str(path_sim[0]) + "\n"
        "Resnik:           " + str(round(resnik[0],4)) + '\n'
        "Lin:              " + str(round(lin[0],4)) + '\n'
        "JC:               " + str(round(jc,4)) + '\n'
        "Extended Lesk:    " + str(extended)
            + "\n")

def get_args():
    word1 = sys.argv[1]
    word2 = sys.argv[2]
    return [word1, word2]

def syngetter(arguments):
    flag1 = (re.match('[A-Za-z]*\.[A-Za-z]*\.[0-9]',arguments[0]))         #Matches if synset input
    if not flag1:
        try:
            word1 = wn.synsets(arguments[0])[0]
        except:
            return "First word not in Wordnet. Try another noun."
    if flag1:
        try:
            word1 = wn.synset(arguments[0])
        except:
            return "First word not in Wordnet. Try another noun."
    flag2 = (re.match('[A-Za-z]*\.[A-Za-z]*\.[0-9]',arguments[1]))         #Matches if synset input
    if not flag2:
        try:
            word2 = wn.synsets(arguments[1])[0]
        except:
            return "Second word not in Wordnet. Try another noun."
    if flag2:
        try:
            word2 = wn.synset(arguments[1])
        except:
            return "Second word not in Wordnet. Try another noun."


    return word1, word2


def Path_Similarity(word1, word2):
    """ equation is 1/ pathlen(c1, c2)"""

    # Initial test to confirm unique nouns, otherwise passes back 1

    if word1 == word2:
        return 1, word1

    # Sets up Initial Variables & Dictionaries

    stepup1 = [word1]
    stepup2 = [word2]
    dict1= {}
    dict2= {}
    currentstep1 = []
    currentstep2 = []

    # Iterates through a loop an arbitrary # of times, adding new hypernyms
    # for each word to individual dictionaries with the number of iterations
    # as the key to the dictionary. The two dictionaries are saved perpetually

    for la in range(50):
        for i in range(len(stepup1)):
            currentstep1 += (stepup1[i].hypernyms())
        for syn in stepup1:
            dict1[syn] = la
        for i in range(len(stepup2)):
            currentstep2 = (stepup2[i].hypernyms())
        for syn in stepup2:
            dict2[syn] = la

        # Variables are reset and converted to continue the next stage of the loop

        stepup1 = currentstep1
        stepup2 = currentstep2
        currentstep1 = []
        currentstep2 = []


        # Each loop the dictionaries are checked for matches. I have confirmed that
        # checking each cycle is faster than checking at the end of an arbitrary
        # number of cycles.

    # Removes applied words as Possible Subsumers Per Fridays Clas
    dict1.pop(word1)
    dict2.pop(word2)

    #Gets possible Least Common Subsumers
    dict1Set = set(dict1)
    dict2Set = set(dict2)
    d = {}
    for name in dict1Set.intersection(dict2Set):
        d[name] = dict1[name]
    pos_lcs = [key for min_value in (min(d.values()),) for key in d if d[key] == min_value]

    #Returns Actual LCS
    key_lcs = []
    for i in pos_lcs:
        key_lcs.append(shortestPath(wn.synset('entity.n.01'),i))
    lcs = (pos_lcs[key_lcs.index(max(key_lcs))])

    #Returns path Similarity Value and Synset of LCS; Must Error Proof

    return 1/(dict1[lcs] + dict2[lcs]), lcs

def shortestPath(haystack, needle):
    """Given Via Foaad Khosmood on Google Colab. Finds the shortest distance from entity to a given word.
    In this implementation, we choose longer of n possiblities."""
    if needle == haystack:
        return 0
    hyponyms = haystack.hyponyms()
    if len(hyponyms) > 0:
        return 1 + min([shortestPath(hypo, needle) for hypo in hyponyms])
    else:
        return 1000

def sumoflemmas():
    """Program to sum the occurences of all words in wordnet in the brown corpus, beginning at entity,
    by a previously called recursive function Downtree.py, and calculated occurences using
    the sum of the frequency distribution of that set in the brown corpus."""

    wordnet_length= 74374

    wordnet_occurrences = 94949 #not unique words
    """stepdown = wn.synsets('entity')[0]
    synsets = downtree.downtree(stepdown, [])
    synsets.append(stepdown)
    synsets = set(synsets)
    #wordnet_length = len(set(synsets))

    nameset =[]
    #fdist = FreqDist(brown.words())
    for syn in synsets:
        for lem in syn.lemmas():
            nameset.append(lem.count())
            #nameset.append(lem.name())

    # for wh in set(nameset):
    #   wordnet_occurrences.append(fdist[wh])

    # Should give set of numbers, with which to sum

    # wordnet_occurrences = sum(wordnet_occurences)

    # Not sure why this returns 105000, seems like a reasonable number,
    # For example, 'dog' returns 70 instead of 42. Perhaps it uses a different
    # percentage of the wordnet corpus. Or was counted wrong. Or this one was,
    # Either way, my understanding is that since we are doing a probability with it,
    # the actual number shouldn't matter too much at these ranges, as long as both the
    # numerator and the denominator are done using the same method.


    wordnet_occurrences = sum(nameset)"""

    return wordnet_occurrences


def Resnik(name):
    """Least Common Subsumer"""
    # USE Previous Function to get LCS, above c1, c2
    print("LCS is:", name)
    # Then use down-tree recursion to find probabilities of all words below
    lcssynset = sorted(set(downtree.downtree(name, [])))


    # Then sum
    nameset = []
    for syn in lcssynset:
        for lem in syn.lemmas():
            nameset.append(lem.count())
    Numerator = sum(nameset)

    Num = Numerator
    Den = sumoflemmas()

    # then divide over all = len(words)
    # Then neg log that, Return

    Resn = math.log(Num/Den, 10)
    return -math.log(Num/Den, 10), Resn
"""equation is -logP(LCS(c1,c2)"""

def Lin(word1,word2, lcsc1c2):

    #Using the created downtree Function, derive all the hyponyms of word1 & word2
    word1down = sorted(set(downtree.downtree(word1,[])))
    word2down = sorted(set(downtree.downtree(word2,[])))

    # For each lemma of all synsets downtree of our given words, store the integer occurrences
    # (of these words in brown) in c1set & c2set respectively.
    c1set=[]
    c2set=[]
    for syn in word1down:
        for lem in syn.lemmas():
            c1set.append(lem.count())
    for syn in word2down:
        for lem in syn.lemmas():
            c2set.append(lem.count())

    # For Smoothing in case of no occurrences in brown for the entirety of the downtree lemmas, add 1
    c1 = sum(c1set)+1
    c2 = sum(c2set)+1

    #Slighly different method of counting. Disregarded due to assigned information friday.
    #Returned slightly different Answer, 10500 for total occurences of wordnet in brown,
    #70 for dog, instead of 42.
    #fdist = FreqDist(brown.words())
    #c1 = []
    #c2 = []
    #for wh in c1set:
    #    c1.append(fdist[wh])
    #for wh in c2set:
    #    c2.append(fdist[wh])
    #c1 = sum(c1)
    #c2 = sum(c2)
    #print(word1down)

    #Perform the Math to get final Lin value, as well as the Probability of C1 & the Probability of C2
    Pc1 = math.log(c1/sumoflemmas(),10)
    Pc2 = math.log(c2/sumoflemmas(),10)
    Lin = (2*lcsc1c2/(Pc1 + Pc2))


    return Lin, Pc1, Pc2

"""equation is (2* logP(LCS(c1,c2))/(logP(c1) + log P(c2))"""


def JC(lcsc1c2, Pc1, Pc2):
    """The JC, or Jiang-Conrath distance, developed in 1997, is another Similarity Functions.
    It is requrired that the previously calculated Values be calculated in a slightly different form."""

    JC = 1/(2*lcsc1c2 - (Pc1 + Pc2))
    return JC

"""equation is 1/ (2* logP(lcs(c1,c2)) - (logP(c1) + logP(c2))"""


def Extended_Lesk(word1,word2):
    """Calculates a value of similarity between two words, based upon the similarity
    of the word's definitions, as well as those definitions of their hyponyms.
    This is the Extended Lesk Method developed by Banjeree Et. Al. & modified
    slightly for use within the CSC 482 class at Cal Poly."""

    #Creates a list of the word, and one layer of hyponyms
    list1 = [word1]
    for i in word1.hyponyms():
        list1.append(i)
    list2 = [word2]
    for i in word2.hyponyms():
        list2.append(i)

    #Creates a list of each of the above words' definitions, tokenized
    words1 = []
    words2 = []
    for i in list1:
        words1.append([l for l in word_tokenize(i.definition())])
    for i in list2:
        words2.append([l for l in word_tokenize(i.definition())])

    #Calculates the Maximum length of the Longest Definition
    lengths = []
    lengths.extend(len(l) for l in words1)
    lengths.extend(len(l) for l in words2)
    maxim = max(lengths)

    igramcount = []
    igram1 = []
    igram2 = []

    # Creates N-grams for each definition for each N, from 1:max(lengths)
    for i in range(int(maxim)):
        for g in words1:
            for l in ngrams(g, i+1):
                igram1.append(l)
        for f in words2:
            for m in ngrams(f, i+1):
                igram2.append(m)

    #For Each N-gram in the first set, which matches that of the Second set,
    # Denoting a form of "Similarity" between the two definitions,
    # Record the Value of N into a new List, igramcount.
        for x in set(igram1):
            if x in set(igram2):
                igramcount.append(i + 1)

        igram1 = []
        igram2 = []

    #Square the values of igramcount, and return the sum as the value of Extended Lesk.
    squared = [number**2 for number in igramcount]
    return sum(squared)

"""Reference:
    BANERJEE, Satanjeev, and PEDERSEN, Ted.
    "An Adapted Lesk Algorithm for Word Sense Disambiguation Using WordNet."
    Lecture Notes in Computer Science (2002): 136-45. Web.

    we define an overlap between them to be the
    longest sequence of one or more consecutive words that occurs in both glosses.
    Each overlap found between two glosses contributes a score equal to the square
    of the number of words in the overlap. (Banerjee et. al.)

    Once all the gloss comparisons have been made for every pair of words in the
    window based on every given relation pair, we add all the individual scores of
    the comparisons to arrive at the combination score for this particular candidate
    combination of sense–tags. """

"""definition only (gloss = definition)
   only gloss and gloss(hyponyms), just one layer. 
   But remember that there  are typically more than one hyponym. (Dr. Foaad Khosmood)"""
"""equation is sum overlap(gloss(r(c1)),gloss(q(c2))"""

if __name__ == "__main__":
    main()