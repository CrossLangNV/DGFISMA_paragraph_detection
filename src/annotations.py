import sys
import string
import re

from src.utils import SeekableIterator
from typing import List, Tuple, Set, Generator

from cassis import Cas, TypeSystem
    
def annotate_lists_eurlex_html( cas: Cas, typesystem: TypeSystem, SofaID:str, \
                               value_between_tagtype= "com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType", \
                               paragraph_type='de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph', \
                              ) -> Cas:
    '''
    Given a cas and its typesystem, this function annotates (as paragraph_type) lists and sublists (enumerations) using available tags ('tables', 'p' tags), and adds it to the cas.
    
    :param cas: Cas. Cas object (mutable object)
    :param typesystem: cassis.typesystem.Typesystem. Corresponding Typesystem of the cas.
    :param SofaID: String. Name of the sofa.
    :param value_between_tagtype: String.
    :param paragraph_type: String. 
    :return: Cas.
    '''
    
    value_between_tagtype_generator=cas.get_view( SofaID ).select( value_between_tagtype )        
    
    seek_vbtt=SeekableIterator( value_between_tagtype_generator )

    process_eurlex_html( cas, typesystem, SofaID, seek_vbtt , value_between_tagtype=value_between_tagtype, paragraph_type=paragraph_type  )
    
    return cas


def annotate_lists_flat_html_pdf( cas: Cas, typesystem: TypeSystem, SofaID:str, \
                               value_between_tagtype= "com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType", \
                               paragraph_type='de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph', \
                              ) -> Cas:
    '''
    Given a cas, this function will detect and annotate (as paragraph_type) all lists and sublists (enumerations) using regexes.
    If the cas contains the following 'p' tags, then they will be annotated with the paragraph_type:
    Something:
    (a) first sentence
    (b) second sentence
     
    :param cas: Cas. Cas object (mutable object)
    :param typesystem: cassis.typesystem.Typesystem. Corresponding Typesystem of the cas.
    :param SofaID: String. Name of the sofa.
    :param value_between_tagtype: String.
    :param paragraph_type: String. 
    :return: int. Position in the Seekable Iterator.
    '''
    
    value_between_tagtype_generator=get_deepest_child_tags( cas, SofaID, tagnames = set( 'p'), value_between_tagtype = value_between_tagtype ) 
    
    seek_vbtt=SeekableIterator( value_between_tagtype_generator )
    
    process_flat_html_pdf( cas, typesystem, SofaID, seek_vbtt, \
                           paragraph_type = paragraph_type, nested=False )
    
    return cas


#helper functions:

def process_eurlex_html( cas: Cas, typesystem: TypeSystem, SofaID: str , value_between_tagtype_seekable_generator: Generator, \
                        value_between_tagtype= "com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType", \
                        paragraph_type='de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph', \
                        end=-1 ):

    '''
    Given a cas, its typesystem, and a SeekableIterator with valuebetweentagtype, this function annotates list and sublists, and adds it to the cas. 
    
    :param cas: Cas. Cas object (mutable object)
    :param typesystem: cassis.typesystem.Typesystem. Corresponding Typesystem of the cas.
    :param SofaID: String. Name of the sofa.
    :param value_between_tagtype_seekable_generator: Generator. Seekable Iterator.
    :param value_between_tagtype: String.
    :param paragraph_type: String. 
    :param end: int. Position, needed for recursive function calls.
    :return: None.
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


def process_flat_html_pdf( cas: Cas, typesystem: TypeSystem, SofaID: str, value_between_tagtype_seekable_generator: Generator, \
                           paragraph_type: str = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph', nested: bool = False ) -> int:
    
    '''
    Given a cas, and a SeekableIterator with valuebetweentagtype, this function will detect all lists and sublists (enumerations, also nested)) using regexes (see get_enumerator).
        
    :param cas: Cas. Cas object (mutable object)
    :param typesystem: cassis.typesystem.Typesystem. Corresponding Typesystem of the cas.
    :param SofaID: String. Name of the sofa.
    :param value_between_tagtype_seekable_generator: Generator. Seekable Iterator.
    :param paragraph_type: String. 
    :param nested: bool. Needed for recursive function calls.
    :return: int. Position in the Seekable Iterator.
    '''
    
    Paragraph=typesystem.get_type( paragraph_type )
                                                          
    paragraph_list=[]
    
    current_list_type=-1
    position=0
    end_position=0

    for tag in value_between_tagtype_seekable_generator:
                
        match=''
        enumerator=''
        
        #need to check for empty strings...
        
        sentence=tag.get_covered_text().strip()
        if not sentence:
            continue
        
        enumerator, list_type = get_enumerator( sentence, current_list_type )
        #print( sentence, list_type )
                    
        if (not paragraph_list) and sentence[-1]==":": #possible start of enumeration
                            
            paragraph_list.append( tag )
                                 
        elif len( paragraph_list )>=1: #This means the start of a list was detected.
            
            if nested:

                #this to jump out of recursice call

                if enumerator: #check if you are in other list ==> if so, add annotation and rewind
                    
                    if current_list_type!=-1:
                    
                        #this means you are in some other list ==> add to cas and rewind
                        if (list_type != current_list_type):

                            if len( paragraph_list )>1:
                                
                                if paragraph_list[-1].end<=position:
                                    end_position=position
                                else:
                                    end_position=paragraph_list[-1].end                                
                                
                                cas.get_view( SofaID ).add_annotation( Paragraph( begin=paragraph_list[0].begin, end=end_position , divType="enumeration" ) )

                            value_between_tagtype_seekable_generator.rewind()
                            return end_position

                    current_list_type=list_type
                
                else:
                
                    if len( paragraph_list )>1:
                        
                        if paragraph_list[-1].end<=position:
                            end_position=position
                        else:
                            end_position=paragraph_list[-1].end 
                        
                        cas.get_view( SofaID ).add_annotation( Paragraph( begin=paragraph_list[0].begin, end=end_position , divType="enumeration" ) )

                    #too far if not an enumerator (end of nested enumeration)
                    value_between_tagtype_seekable_generator.rewind()
                    return end_position
            
            
            if enumerator and (list_type==current_list_type or current_list_type==-1):

                #add enumerator check here ( i.e. if it is of same type as previously added enumerator... )
                
                paragraph_list.append(  tag )

                if sentence[-1]==":":
                    value_between_tagtype_seekable_generator.rewind()
                    position=process_flat_html_pdf( cas, typesystem, SofaID, value_between_tagtype_seekable_generator, nested=True  )
                    #if not position:  #case where iteration stops inside a nested list, then annotate_article returns None.
                    #    position=0

                current_list_type=list_type

            else:
                
                #add annotation and empty paragraph_list. 
                #also check if length of paragraph > 1. We do not want to add paragraphs consisting of only "something:"
                if len( paragraph_list )>1:
                    
                    if paragraph_list[-1].end<=position:
                        end_position=position
                    else:
                        end_position=paragraph_list[-1].end
                                  
                    cas.get_view( SofaID ).add_annotation( Paragraph( begin=paragraph_list[0].begin, end=end_position , divType="enumeration" ) )
                 
                paragraph_list=[]
                current_list_type=-1

                if sentence[-1]==":": #possible start of new enumeration
                    paragraph_list.append(tag)
                                    
    #add the last one:
    if len( paragraph_list) > 1 :

        if paragraph_list[-1].end<=position:
            end_position=position
        else:
            end_position=paragraph_list[-1].end
        
        cas.get_view( SofaID ).add_annotation( Paragraph( begin=paragraph_list[0].begin, end=end_position , divType="enumeration" ) )
    
    return end_position



def get_deepest_child_tags(  cas: Cas, SofaID: str , tagnames : Set[str] = set( 'p'), \
                           value_between_tagtype: str = "com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType"  ) -> Generator:
    
    '''
    Given a cas, and a view (SofaID), this function selects all ValueBetweenTagType elements ( with tag.tagName in the set tagnames ), 
    and extracts only the deepest childs of the to be extracted tagnames
        
    :param cas: cassis.typesystem.Typesystem. Corresponding Typesystem of the cas.
    :param SofaID: String. Name of the sofa.
    :param tagnames: String. tagtypes to extract.
    :param value_between_tagtype: String.
    :return: Generator.
    '''
    
    def deepest_child( cas:Cas, SofaID:str , tag ,tagnames: Set[str] = set( 'p' ) ) -> bool:
        
        #helper function
        if len( [item for item in cas.get_view( SofaID ).select_covered(  value_between_tagtype , tag ) \
                 if item.tagName in tagnames ] ) > 1:
            return False
        else:
            return True

    for tag in cas.get_view( SofaID ).select( value_between_tagtype ):
        if tag.tagName in set(tagnames) and deepest_child(  cas, SofaID, tag, tagnames ):
            sentence=tag.get_covered_text().strip()
            if sentence:
                yield tag

                
                
def get_enumerator( sentence: str, list_type: int = -1 ) ->Tuple[ str, int ]:

    '''
    Given a sentence, and list_type (7 list types), this function gets the enumerator, and the list type. 
    Example:
    (a) some sentence -> (a), 2
    
    :param sentence: String.
    :param list_type: int.
    :return: Tuple.
    '''
    
    enumerator=''

    alphabet_list = list( string.ascii_lowercase )

    #REGEX_OPTIONS:
    #Regex option is a tuple with a regex_rule at position 0, and a list defining how the sections follow one another.

    regex_option_1_rule=r'\d+\.( |$)'  #i.e. 1.
    regex_option_1_list=[ str( i )+'.' for i in range(1,100) ]
    regex_option_1=( regex_option_1_rule, regex_option_1_list )

    regex_option_2_rule=r'^\(\d+\)( |$)'   #i.e. (1)
    regex_option_2_list=[ '(' + str( i )+')' for i in range(1,100) ]
    regex_option_2=( regex_option_2_rule, regex_option_2_list )

    regex_option_3_rule=r'^\(([a-z])\)( |$)' #i.e. (a)
    regex_option_3_list=[f"({i})" for i in alphabet_list]
    regex_option_3=( regex_option_3_rule, regex_option_3_list )

    regex_option_4_rule= r'^(\(i\)|\(ii\)|\(iii\)|\(iv\)|\(v\)|\(vi\)|\(vii\)|\(viii\)|\(ix\)|\(x\)|\(xi\)|\(xii\)|\(xiii\)|\(xiv\)|\(xv\)|\(xvi\)|\(xvii\)|\(xviii\)|\(xviv\)|\(xvv\)|\(xvvi\)|\(xvvii\)|\(xvvviii\)|\(xix\)|\(xx\))( |$)'  
    regex_option_4_list=[ '(i)', '(ii)', '(iii)', '(iv)', '(v)', '(vi)', '(vii)', '(viii)', '(ix)', '(x)', '(xi)', '(xii)', '(xiii)', '(xiv)', '(xv)', '(xvi)', '(xvii)', \
                         '(xviii)', '(xviv)',  '(xvv)', '(xvvi)', '(xvvii)', '(xvvviii)', '(xix)', '(xx)'  ]
    regex_option_4=( regex_option_4_rule, regex_option_4_list )

    regex_option_5_rule=r'•( |$)'  #i.e. •
    regex_option_5_list=["•"]
    regex_option_5=( regex_option_5_rule, regex_option_5_list )
    
    regex_option_6_rule=r'—( |$)'  #i.e. —
    regex_option_6_list=["—"]
    regex_option_6=( regex_option_6_rule, regex_option_6_list )
    
    regex_option_7_rule=r'-( |$)'  #i.e. -
    regex_option_7_list=["-"]
    regex_option_7=( regex_option_7_rule, regex_option_7_list )
    
    #list of regexes:
    regex_list=[ regex_option_1 , regex_option_2 , regex_option_3 , regex_option_4, regex_option_5, regex_option_6, regex_option_7  ]

    detected_list_type=None  #the type of the detected enumeration (i.e. 7 types of enumerations, and return which one is detected)
    
    for i,regex in enumerate(regex_list):
        
        match=re.match( regex[0], sentence )

        if match:
            enumerator=match.group().strip()

            if enumerator=="(i)" and (list_type ==-1 and i==2  ): #if you detect (i), but you are not in list type 2, continue (i.e. probably start of list type 3)
                continue
            elif enumerator=="(v)" and (list_type == 3 and i==2 ): #you detect (v), but you are in list type 3 ==> (v) indicates continuation of list type 3
                continue
            elif enumerator=="(x)" and (list_type == 3 and i==2 ): #same
                continue
            else:
                break
                
    if enumerator:
        detected_list_type=i

    return enumerator, detected_list_type

def is_old_eurlex( cas: Cas, SofaID: str, value_between_tagtype= "com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType" ) -> bool:
    
    '''
    Given a cas, and a view (SofaID), this function decides of the html in the cas is an old eurlex, or a new eurlex document, by looking at the occurence of the txt_te tag.
        
    :param cas: cassis.typesystem.Typesystem. Corresponding Typesystem of the cas.
    :param SofaID: String. Name of the sofa.
    :param value_between_tagtype: String.
    :return: bool.
    '''
    
    for vbtt in cas.get_view( SofaID ).select( value_between_tagtype ):
        if vbtt.tagName == "txt_te":
            return True
    return False