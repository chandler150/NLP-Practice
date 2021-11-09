"""
*************************************************
* Readability.py by Chandler Jones              *
* For CSC 482, Dr. Foaad Khosmood               *
* For Laboratory 2, part 1                      *
* In our Natural Language Processing Class      *
* January 23rd, 2020                            *
*************************************************
"""

"""Follows the Directions Outlined below:"""
#Write a program called readabilitypack.py to analyze a plain text file passed in from the command line, and generate the following readabilitypack metrics:

#Flesch reading ease
#Flesch-Kincade grade level
#The New Dale-Chall Readability Formula
#Gunning-Fog index
#SMOG grade

#Your output should the name of each index, followed by colon,
# one space and then the numeric value. You can assume about a 1000 words of plain text English
# in one or more paragraphs. You may use any standard Python package,
# but you must calculate each of the scores yourself from scratch in separate functions
# inside your program.

fleshscore = 0
fleshkinscore = 0
dale_challscore = 0
gunningscore = 0
smogscore = 0
import nltk
import sys
import hyphenate
import dalechall
import math
import urllib
from nltk.corpus import wordnet as wn

def main():
    """Runs only if __name__ == "__main__", and will output the readability scores
    in the correct format. Seems to be working well."""
    input = Fileimport()
    text = tokenize(input)                  # grab from his google colab
    words = text[0]                         # list with each word as elements
    wordcount = text[1]                     # single int value # of words
    if wordcount == 0:
        print("\n"+"Must Supply Suitable Text Document as Argument"+"\n")
        return
    sentence_lengths = text[2]                  # list of sentence lengths
    smogwords = text[3]
    syllable = syllable_count(words,smogwords)  # where 0 is total # of syllables, 1 is # of words with syllables > 2
    totalsyl = syllable[0]
    hardwords = syllable[1]
    smoghardwords= syllable[2]
    fleshscore = flesher(wordcount, sentence_lengths, totalsyl)
    fleshkinscore = flesherkincaid(wordcount,sentence_lengths ,totalsyl)
    dale_challscore = dale_chall(words, wordcount, sentence_lengths)
    gunningscore = gunning_fog(sentence_lengths, hardwords, wordcount)
    smogscore = smog(smoghardwords)

    """Once everything is counted, print in the way he wants it"""

    print(  "\n" +
            "Flesch reading ease:                     " + str(int(fleshscore)) +    '    (Raw Score)' + "\n"
            "Flesch-Kincade grade level:              " + str(int(fleshkinscore)) + '     (Grade Level)' +'\n'
            "The New Dale-Chall Readability Formula:  " + str(dale_challscore)  + '\n'
            "Gunning-Fog index:                       " + str(round(gunningscore,2)) +  '  (Raw Score)'+ '\n'
            "SMOG grade:                              " + str(int(smogscore)) + '     (Grade Level)' + "\n")

def Fileimport():
    """This function imports a plaintext .txt file from the command line.
        It runs in main(), and places the txt file into a string, 'data'
        Make sure to specify the whole path to your file"""
    file_name = sys.argv[1]
    f = open(file_name)
    data = f.read()
    return data
    f.close()

def tokenize(input):
    """Tokenizer Grabbed from google colab, plus slight modifications to return sentence lengths,
    as well as the first 30 sentences for use in SMOG analysis later on."""

    inText = input
    raw_paragraphs = [p.strip() for p in inText.split("\n\n")]

    # Sentence Tokenization: We want separate sentences. They could end in periond ., or "!" or "?" or "..."
    # NLTK has a number of built-in toknizers that takes all this into consideration (for English)

    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    sent = []
    for i in range(len(raw_paragraphs)):
        sent.append(sent_tokenizer.tokenize(raw_paragraphs[i]))

    sentlen = []
    words = []
    smogwords= []
    count = 0
    for i in range(len(sent)):
        for l in range(len(sent[i])):
            words += (sent[i][l].split())
            sent_seg =(sent[i][l].split())              # overwrite variable to store length of last sentence
            sentlen.append(len(sent_seg))               # appends variable to create list of sentence lengths
            count += 1
            if count < 31:
                smogwords += ((sent[i][l].split()))     #words in first 30 sentences

    return [words, len(words), sentlen, smogwords]

def syllable_count(text, smogwords):
    """Counts syllables of each word in text using Hyphenation implementation of Frank Liang's Algorithm.
    Modifications made to parse out hardwords in total text, and hardwords in first 30 sentences."""
    words = text
    smogwords= smogwords
    syllables = []
    hardwords = []
    for i in words:
        syllables.append(len(hyphenate.hyphenate_word(i)))
        if len(hyphenate.hyphenate_word(i)) > 2:
            hardwords.append(len(hyphenate.hyphenate_word(i)))
    smogsyllables = []
    smoghardwords = []
    for i in smogwords:
        smogsyllables.append(len(hyphenate.hyphenate_word(i)))
        if len(hyphenate.hyphenate_word(i)) > 2:
            smoghardwords.append(len(hyphenate.hyphenate_word(i)))
    sylcount = sum(syllables)

    return [sylcount, hardwords, smoghardwords]


def flesher(wordcount, sentence_lengths, totalsyl):
    """Creates Flesher Readability index for sample text. Uses the equation listed below to develop
    final score. """
    # needs # of words
    # needs # of sentences
    # needs # of syllables total

    wordcount = wordcount
    sentence_lengths = sentence_lengths
    totalsyl = totalsyl
    avg_sen = sum(sentence_lengths)/len(sentence_lengths)

    Readingease = 206.835 - (1.015*avg_sen) - (84.6 * totalsyl/wordcount)
    return Readingease

"""Reading Ease score = 206.835 − (1.015 × ASL) − (84.6 × ASW)
Where: ASL = average sentence length (number of words divided by number of sentences)
ASW = average word length in syllables (number of syllables divided by number of words)"""

def flesherkincaid(wordcount,sentence_lengths ,totalsyl):
    """Generates FlesherKincaid readability score from supplied text. Uses the equation listed at bottom
    to develop final score."""
    # needs list of total words
    # needs list of total sentences
    # needs list of total syllables

    wordcount = wordcount
    sentence_lengths = sentence_lengths
    totalsyl = totalsyl
    Ease = .39 * (wordcount/len(sentence_lengths)) + 11.8 * (totalsyl/wordcount) - 15.59

    return Ease

""".39 * (total words /total sentences) + 11.8 * (total syllables / total words) - 15.59"""

def dale_chall(words, wordcount, sentence_lengths):
    """Generates Dale_Chall formula as a function of average sentence lengths and percentage of words
    within the Dale-Chall wordlist. Wordlist was found on Github, and is imported as a .txt file.
    Output is normallized to the Dale_Chall index at bottom. """
    # needs words on dale chall word list
    # sample broken into 100 words
    # Sentence lengths

    words = words
    wordcount = wordcount
    avg_sen = sum(sentence_lengths) / len(sentence_lengths)

    # Import Dale_Chall WordList.
    dales = dalechall.run('DALELIST.txt').split(",")

    #Opting out of Request method, becuase requires pip install urllib. Works fine on my end, but maybe
    #not on yours.
    #request = urllib.request.urlopen('http://countwordsworth.com/download/DaleChallEasyWordList.txt')
    #dales = str(request.read()).split("\\n")
    #dales[0] = 'a'
    #dales[-1] = 'you\'ve'

    #print(len(dales))                      # only has 2950, gave a good search, going to run with it

    #Calculates DaleCount
    dalecount = 0
    for i in range(len(words)):
        if words[i] in dales:
            dalecount += 1

    #Calculates Dale_Chall Score:
    Raw = 0.1579 * (wordcount-dalecount)/wordcount + 0.0496*avg_sen
    if (wordcount-dalecount)/wordcount < 0.05:
        Raw = .1579*(wordcount-dalecount)/wordcount + 0.0496*avg_sen + 3.6365
        print('was')

    #Converts Score to Grade Level
    if Raw <= 4.9:
        Raw = "Grades 4 or Below"
    elif  5.9 >= Raw > 5:
        Raw = "Grades 5-6"
    elif 6.9 >= Raw > 6:
        Raw = "Grades 7–8"
    elif 7.9 >= Raw > 7:
        Raw = "Grades 9–10"
    elif 8.9 >= Raw > 8:
        Raw = "Grades 11–12"
    elif 9.9 >= Raw > 9:
        Raw = "Grades 13–15 (college)"
    elif Raw > 10:
        Raw = "Grades 16 and above."
    return Raw

"""To apply the formula:

Select several 100-word samples throughout the text.
Compute the average sentence length in words (divide the number of words by the number of sentences).
Compute the percentage of words NOT on the Dale–Chall word list of 3,000 easy words.
Compute this equation from 1948:
Raw score = 0.1579*(PDW) + 0.0496*(ASL) if the percentage of PDW is less than 5 %, otherwise compute
Raw score = 0.1579*(PDW) + 0.0496*(ASL) + 3.6365
Where:

Raw score = uncorrected reading grade of a student who can answer one-half of the test questions on a passage.
PDW = Percentage of difficult words not on the Dale–Chall word list.
ASL = Average sentence length
Finally, to compensate for the "grade-equivalent curve," apply the following chart for the Final Score:

Raw score	Final score
4.9 and below	Grade 4 and below
5.0–5.9	Grades 5–6
6.0–6.9	Grades 7–8
7.0–7.9	Grades 9–10
8.0–8.9	Grades 11–12
9.0–9.9	Grades 13–15 (college)
10 and above	Grades 16 and above.
"""

def gunning_fog(sentence_lengths, hardwords, wordcount):
    """Gunning Fog Index returns a raw score using the equation at bottom."""
    # needs average sentence length
    # needs list of words with more than two syllables
    # needs count of words
    hardwords = hardwords
    avg_sen = sum(sentence_lengths) / len(sentence_lengths)
    Grade = 0.4 * ((avg_sen)+(len(hardwords)/wordcount))

    return Grade

"""Grade level= 0.4 * ( (average sentence length) + (percentage of Hard Words) )
Where: Hard Words = words with more than two syllables.[46]"""


def smog(smoghardwords):
    """SMOG uses a specialized list outlined in the comment below to return a calculated score."""
    # needs own list of words with more than two syllables within the first 30 sentences
    smog = 3 + math.sqrt(len(smoghardwords))

    return smog

"""Harry McLaughlin determined that word length and sentence length should be multiplied rather than added as in other formulas.
In 1969, he published his SMOG (Simple Measure of Gobbledygook) formula:

SMOG grading = 3 + √(polysyllable count).
Where: polysyllable count = number of words of more than two syllables in a sample of 30 sentences.[5]
The SMOG formula correlates 0.88 with comprehension as measured by reading tests.[6] It is often recommended for use in healthcare.[49]"""

if __name__ == "__main__":
    main()