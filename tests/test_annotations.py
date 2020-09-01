import os
import pytest

from tests.fixtures import *

from cassis.typesystem import load_typesystem
from cassis.xmi import load_cas_from_xmi

from src.annotations import annotate_lists_eurlex_html


@pytest.mark.parametrize("get_path_xmi, get_path_table, get_path_typesystem", [
                        ("small_nested_tables.xmi", "small_nested_tables_lists.txt", "typesystem.xml" ),  
                        ("minus_lesser_of.xmi", "minus_lesser_of_lists.txt", "typesystem.xml" ),
                        ("doc_bf4ef384-bd7a-51c8-8f7d-d2f61865d767.xmi", "doc_bf4ef384-bd7a-51c8-8f7d-d2f61865d767_lists.txt", "typesystem.xml" ) ] , 
                         indirect=["get_path_xmi", "get_path_table", "get_path_typesystem"  ])
def test_eurlex_annotations( get_path_xmi, get_path_table, get_path_typesystem  ):
    
    with open( get_path_typesystem , 'rb') as f:
        typesystem = load_typesystem(f)
        
    cas=load_cas_from_xmi( open( get_path_xmi , 'rb') , typesystem=typesystem )
    
    cas=annotate_lists_eurlex_html( cas, typesystem, "html2textView", list( cas.get_view(  'html2textView' ).select( "com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType" ) ) )

    all_paragraphs=list(cas.get_view( 'html2textView' ).select( "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph" ))
    
    with open( get_path_table , "r") as f:
        tables_list=f.read().strip( "_"*100+"\n"  ).split( "_"*100   )
    
    assert len(all_paragraphs)==len( tables_list )
     
    for found_list, true_list in zip( all_paragraphs, tables_list ):
        
        assert( found_list.get_covered_text().strip().replace('\r', '') ==  true_list.strip()  )
