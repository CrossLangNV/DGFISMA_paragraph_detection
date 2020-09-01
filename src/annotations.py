import sys
from src.utils import find_indices_term
from typing import List, Tuple, Set

from cassis import Cas, TypeSystem

def annotate_lists_eurlex_html( cas: Cas, typesystem: TypeSystem, SofaID: str , list_of_value_between_tagtype: list ) -> Cas:

    '''
    Given a cas and its typesystem, this function annotates list and sublists. Returns the same cas object as the input cas, but now with annotations added.
    '''
    
    Paragraph=typesystem.get_type( 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph' )

    cas_view=cas.get_view( SofaID )

    paragraph_list=[]
    detected_p=None
    
    for i, tag in enumerate(list_of_value_between_tagtype):
            
        if tag.tagName =='p':
            
            #keep track of detected p's
            detected_p = tag
            continue
            
        if tag.tagName == 'table': 
            
            #if no p has been detected before, ignore this detected table
            if not detected_p:
                continue
            
            #1) check if it contains a nested table, if so, recursive function call:
            tags_covered=list(cas_view.select_covered( "com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType", tag ))
            if contains_table( tags_covered[1:] ): #this means it is a nested structure ( the first element of tags_covered is tag )
                annotate_lists_eurlex_html( cas, typesystem, SofaID, tags_covered[1:] )
            
            #2) check if it is not one of the nested tags (but don't check this for the very first detected table, when paragraph list is still empty):            
            if paragraph_list:
                if tag.begin < paragraph_list[-1].end:
                    continue              
            
            #3) start of a new list if previous tag was a <p> (structure of a list is always <p></p> <table></table> <table></table>)
            #So if there is no text between the end of the detected p and the table_tag ==> start of a new list
            if not cas_view.sofa_string[ detected_p.end:tag.begin ].strip():
                
                #but first check if the detected p is not part of the previous detected table. 
                #i.e. p's like this: <table><p></p></table><table></table>, should not start a new list
                #If so ==> no new list is detected, and table tag is just added to paragraph_list
                if paragraph_list:
                    if (detected_p.begin < paragraph_list[-1].end) and not(cas_view.sofa_string[ paragraph_list[-1].end:tag.begin ].strip() ): 
                        paragraph_list.append( tag )
                        continue
                
                #so it is indeed the start of a new list ==> add the old list as annotation to the cas
                if len(paragraph_list)>1:
                    
                    #But detected p that is located just before table tag, should also be reasonably long, to initiate new list. 
                    #E.g. this: <p> start of new list </p> <table> </table> <table></table> <p> minus the lesser of: </p> <table> </table>. 
                    #Second p should not initiate new list
                    if len( cas_view.sofa_string[ paragraph_list[-1].end:tag.begin ].split())<=5:
                        paragraph_list.append( detected_p )
                        paragraph_list.append( tag )
                        continue
                    cas_view.add_annotation( Paragraph( begin=paragraph_list[0].begin, end=paragraph_list[-1].end , divType="enumeration" ) )
                paragraph_list=[]                
                paragraph_list.append( detected_p ) #the p
                paragraph_list.append( tag )  #the table tag

            elif paragraph_list:
                 #there should not be any text between the beginning of the current and the end of the previous table tag
                if not(cas_view.sofa_string[ paragraph_list[-1].end:tag.begin ].strip() ):        
                    paragraph_list.append( tag )
        
    #add the last detected list to the cas
    if len( paragraph_list )>1:
        cas_view.add_annotation( Paragraph( begin=paragraph_list[0].begin, end=paragraph_list[-1].end , divType="enumeration" ) )
        
    return cas


def annotate_lists_pdf( cas: Cas )->Cas:
    
    "TO BE IMPLEMENTED"
    
    return cas

#helper function

def contains_table(  list_of_value_between_tagtype ):
    for tag in list_of_value_between_tagtype:
        if tag.tagName=='table':
            return True
    return False