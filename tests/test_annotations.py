import os
import pytest

from tests.fixtures import *

from cassis import Cas
from cassis.typesystem import load_typesystem
from cassis.xmi import load_cas_from_xmi

from src.annotations import annotate_lists_eurlex_html, annotate_lists_flat_html_pdf, is_old_eurlex


@pytest.mark.parametrize("get_path_xmi, get_path_table, get_path_typesystem", [
                        ("small_nested_tables.xmi", "small_nested_tables_lists.txt", "typesystem.xml" ),  
                        ("minus_lesser_of.xmi", "minus_lesser_of_lists.txt", "typesystem.xml" ),
                        ("doc_bf4ef384-bd7a-51c8-8f7d-d2f61865d767.xmi", "doc_bf4ef384-bd7a-51c8-8f7d-d2f61865d767_lists.txt", "typesystem.xml" ),
                        ("double_nested_list.xmi", "double_nested_list_lists.txt", "typesystem.xml" ),
                        ("doc_3b30d182-e395-5e6c-991a-b57cd01598d0.xmi", "doc_3b30d182-e395-5e6c-991a-b57cd01598d0_lists.txt", "typesystem.xml" ),
                        ("doc_03999998-5925-5d85-a3bf-2595dc008002.xmi", "doc_03999998-5925-5d85-a3bf-2595dc008002_lists.txt", "typesystem.xml" )] , 
                         indirect=["get_path_xmi", "get_path_table", "get_path_typesystem"  ])
def test_eurlex_annotations( get_path_xmi, get_path_table, get_path_typesystem  ):
    
    '''
    Unit test for annotate_list_eurlex_html and annotate_lists_flat_html_pdf
    '''
    
    with open( get_path_typesystem , 'rb') as f:
        typesystem = load_typesystem(f)
        
    cas=load_cas_from_xmi( open( get_path_xmi , 'rb') , typesystem=typesystem )
    
    if is_old_eurlex(cas, "html2textView" ):
        
        annotate_lists_flat_html_pdf( cas, typesystem, "html2textView" )
                
    else:
        
        annotate_lists_eurlex_html( cas, typesystem, "html2textView")
    
    all_paragraphs=list(cas.get_view( 'html2textView' ).select( "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph" ))
    
    with open( get_path_table , "r") as f:
        tables_list=f.read().strip( "_"*100+"\n"  ).split( "_"*100   )
    
    assert len(all_paragraphs)==len( tables_list )
     
    for found_list, true_list in zip( all_paragraphs, tables_list ):
        
        assert( found_list.get_covered_text().strip().replace('\r', '') ==  true_list.strip()  )
        

        
@pytest.mark.parametrize("get_path_txt_enumeration, get_path_txt_enumeration_tables, get_path_typesystem", [
                        ("test.txt", "test_list.txt", "typesystem.xml" ),  
                        ("test2.txt", "test2_list.txt", "typesystem.xml" ),
                        ("test5.txt", "test5_list.txt", "typesystem.xml" ),
                        ("test7.txt", "test7_list.txt", "typesystem.xml" ),
                        ("test10.txt", "test10_list.txt", "typesystem.xml" ),
                        ("test11.txt", "test11_list.txt", "typesystem.xml" ),
                        ("test12.txt", "test12_list.txt", "typesystem.xml" ) ] , 
                         indirect=["get_path_txt_enumeration", "get_path_txt_enumeration_tables", "get_path_typesystem"  ])
def test_flat_html_annotations( get_path_txt_enumeration, get_path_txt_enumeration_tables, get_path_typesystem  ):
    
    '''
    Unit test for annotate_lists_flat_html_pdf on dummy data.
    '''
    
    with open( get_path_typesystem , 'rb') as f:
        typesystem = load_typesystem(f)
        
    #first make dummy cas with some 'p' tags
        
    document=open( get_path_txt_enumeration ).read().rstrip( "\n" )

    cas = Cas( typesystem=typesystem )

    NewSofaID="html2textView" 
    cas.create_view( NewSofaID )
    cas.get_view( NewSofaID ).sofa_string = document

    value_between_tagtype="com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType"
    vbtt = typesystem.get_type( value_between_tagtype )

    #annotate the segments as p-tags
    position=0
    for segment in document.split( "\n" ):
        cas.get_view( NewSofaID ).add_annotation( vbtt( begin=position, end=position+len(segment), tagName='p' ) )
        position+=(len(segment)+1 )  
            
            
    annotate_lists_flat_html_pdf( cas, typesystem, NewSofaID , value_between_tagtype=value_between_tagtype, \
                            paragraph_type='de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph' )
                    
    #get all the annotated paragraphs
    all_paragraphs=list(cas.get_view( 'html2textView' ).select( "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph" ))
    
    #read in the gold standard
    with open( get_path_txt_enumeration_tables , "r") as f:
        tables_list=f.read().strip( "_"*100+"\n"  ).split( "_"*100   )
    
    #check if predicted enumeration matches gold standard
    assert len(all_paragraphs)==len( tables_list )
     
    for found_list, true_list in zip( all_paragraphs, tables_list ):
        
        assert( found_list.get_covered_text().strip().replace('\r', '') ==  true_list.strip()  )
