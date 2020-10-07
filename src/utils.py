from typing import List
import re
import string

#seekable iterator utils function, used in annotations.py

class SeekableIterator:
    def __init__(self, iterator):
        self.iterator = iterator
        self.current = None
        self.reuse = False

    def __iter__(self):
        return self
    
    def __next__(self):
        return self.next()

    def next(self):
        if self.reuse:
            self.reuse = False
        else:
            self.current = None
            self.current = next(self.iterator)
        return self.current

    def rewind(self):
        self.reuse = True

#utils function for spellcheck used in segment.py

from nltk.tokenize import word_tokenize
from spellchecker import SpellChecker

def concat_list_spellcheck( sentences: List[str] ) -> str:

    '''
    Concatenate list of strings, into one string without newlines ("i.e. \n"), taking care of words split with "-" using a spellchecker.
    
    :param sentences: list. List of sentences (string).
    :return: str. Concatenated sentences.
    '''
    
    spell=SpellChecker( distance=1 )
    
    sentences=[ sentence.strip() for sentence in sentences if sentence.strip() ]

    if not sentences:
        return ""
    
    text_concat=sentences[0]
    for i,sentence in enumerate(sentences):
        if i==0:
            continue
        previous_sentence=sentences[i-1]
        if previous_sentence[-1]=="-":
            last_word_previous=previous_sentence.split()[-1]   #check for punctuation present in the word, strip it before merging...
            first_word_current=sentence.split()[0]
            
            #note: word_tokenize of nltk does not split "-" from words ("new-" remains "new-")
            last_word_previous_tok=word_tokenize( last_word_previous )[-1] #strip stuff i.e. ;new- ==> new-
            first_word_current_tok=word_tokenize( first_word_current )[0] #strip stuff i.e. york's ==> york
        
            if "http://" == last_word_previous[:7]: #don't want http://something- to be split
                text_concat+=sentence
            elif not spell.unknown( [ last_word_previous_tok+first_word_current_tok ] ): #new-york (known word)                
                text_concat+=sentence
            elif not spell.unknown( [ last_word_previous_tok[:-1]+first_word_current_tok ] ): #test-ting==>testing (known word)
                text_concat=text_concat[:-1] #remove the - from text
                text_concat+=sentence                
            else:
                text_concat+= (" "+sentence) #both with - and without - it is not a known word
        else:
            text_concat+=(" "+sentence)
    return text_concat