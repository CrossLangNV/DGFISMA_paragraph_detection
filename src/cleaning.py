import sys
from typing import List, Tuple, Set

from cassis import Cas


def get_text_html(  cas: Cas, SofaID: str , tagnames : Set[str] = set( 'p')  ) -> List[str] :
    
    '''
    Given a cas, and a view (SofaID), this function selects all ValueBetweenTagType elements ( with tag.tagName in the set tagnames ), extracts the covered text, and returns the list of extracted sentences.
    '''
    
    sentences=[]
    for tag in cas.get_view( SofaID ).select( "com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType" ):
        if tag.tagName in set(tagnames):
            sentence=tag.get_covered_text().strip()
            if sentence:
                sentences.append( sentence )
                
    return sentences

def get_text_pdf(  cas: Cas, SofaID: str  ) -> List[str] :
    
    '''
    Given a cas, and a view, this function should return the text we want. TO DO
    '''
    
    pass