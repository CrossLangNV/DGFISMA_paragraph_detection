import pytest
from src.utils import concat_list_spellcheck

def test_spellcheck():
    
    test_documents=[\
                [ " test new-", ".york... more test-", "ing.." , " " , "new-", "york's", "new-", "'",  "token", "http://www.eba.be-", "2010-216", ";new-", "york'"   ],\
                ["some sentence"] ,\
                ["some sentence1", "some sentence2" ],\
                [], \
                [ "" ],\
                [ " ", "\n", "a" ] \
               ]
    
    concat_documents=[\
                  "test new- .york... more testing.. new-york's new- ' token http://www.eba.be-2010-216 ;new-york'",\
                  "some sentence", \
                  "some sentence1 some sentence2", \
                  "", \
                  "", \
                  "a" \
                 ]
    
    for sentences, text in zip( test_documents, concat_documents ):
        assert( text==concat_list_spellcheck( sentences ) )
