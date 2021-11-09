import nltk
from nltk import *
from nltk.corpus import wordnet as wn
import sys
def main():
    Syn = sys.argv[1]
    print(Syn)
    Synset = wn.synsets(Syn)
    downtree(Synset[0])

def downtree(Synset, memory = []):
    """Recursive Downtree Function, Returns list of lemmas below given Synset"""
    #print(len(memory))
    for s in Synset.hyponyms():
        #print(s)
        memory.append(s)
        downtree(s, memory=memory)

    else:
        now = memory
        memory = []
        #print(now)
        return now

if __name__ == "__main__":
    main()