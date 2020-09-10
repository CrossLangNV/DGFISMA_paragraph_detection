import sys
from src.utils import SeekableIterator
from typing import List, Tuple, Set, Generator

from cassis import Cas, TypeSystem
    
def annotate_lists_eurlex_html( cas: Cas, typesystem: TypeSystem, SofaID:str, \
                               value_between_tagtype= "com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType", \
                               paragraph_type='de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph', \
                              ) -> Cas:
        
    '''
    Given a cas and its typesystem, this function annotates lists and sublists, and adds it to the cas.
    '''
    
    value_between_tagtype_generator=cas.get_view( SofaID ).select( value_between_tagtype )        
    
    seek_vbtt=SeekableIterator( value_between_tagtype_generator )

    process_eurlex_html( cas, typesystem, SofaID, seek_vbtt , value_between_tagtype=value_between_tagtype, paragraph_type=paragraph_type  )
    
    return cas


def annotate_lists_pdf( cas: Cas )->Cas:
    
    "TO BE IMPLEMENTED"
    
    return cas

#helper functions:

def process_eurlex_html( cas: Cas, typesystem: TypeSystem, SofaID: str , value_between_tagtype_seekable_generator: Generator, \
                        value_between_tagtype= "com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType", \
                        paragraph_type='de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph', \
                        end=-1 ):

    '''
    Given a cas, its typesystem, and a SeekableIterator with valuebetweentagtype, this function annotates list and sublists, and adds it to the cas. 
    '''
    
    Paragraph=typesystem.get_type( paragraph_type )

    cas_view=cas.get_view( SofaID )
    
    paragraph_list=[]
    detected_p=None

    for tag in value_between_tagtype_seekable_generator:
        
        #first check if not exceed the span of the covering table (for nested lists), if so rewind and stop.
        if end>0 and tag.begin > end:
            
            #Add the last detected list to the cas
            if len( paragraph_list )>1:
                cas_view.add_annotation( Paragraph( begin=paragraph_list[0].begin, end=paragraph_list[-1].end , divType="enumeration" ) )     
            
            value_between_tagtype_seekable_generator.rewind()

            return
        
        if tag.tagName=="p":
            
            detected_p=tag
            continue
        
        if tag.tagName=="table":
            
            #if no p has been detected before, ignore this detected table
            if not detected_p:
                continue
                        
            tags_covered=list(cas_view.select_covered( value_between_tagtype, tag ))
            if contains_table( tags_covered[1:] ):
                #print( "table containing nested_list_detected: range", tag , tag.begin, tag.end )
                process_eurlex_html(cas, typesystem, SofaID, value_between_tagtype_seekable_generator, end=tag.end  )
                
            #2) check if it is not one of the nested tags (but don't check this for the very first detected table, when paragraph list is still empty):            
            #if paragraph_list:
            #    if tag.begin < paragraph_list[-1].end:
            #        continue              
            
            #3) start of a new list if previous tag was a <p> (structure of a list is always <p></p> <table></table> <table></table>)
            #So if there is no text between the end of the detected p and the table_tag ==> start of a new list
            if not cas_view.sofa_string[ detected_p.end:tag.begin ].strip():
                
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
      
            
def contains_table(  list_of_value_between_tagtype ):
    for tag in list_of_value_between_tagtype:
        if tag.tagName=='table':
            return True
    return False