import pytest
import tempfile

from tests.fixtures import *

from cassis import Cas
from cassis.typesystem import load_typesystem
from deepsegment import DeepSegment

from src.segment import TextSegmenter
from user_scripts import train_deepsegment

@pytest.mark.parametrize("get_path_txt, get_path_embeddings, get_path_typesystem", [
                        ("test_segments.txt", "glove.6B.100d.txt", "typesystem.xml" ) ] ,
                         indirect=["get_path_txt", "get_path_embeddings", "get_path_typesystem" ])
def test_text_segmenter( get_path_txt, get_path_embeddings, get_path_typesystem ):
    
    '''
    unit test for testing of the TextSegmenter
    '''
    
    test_documents=[ \
                    "This is the first sentence. This is the second sentence. And the second sentence", \
                    ""\
                   ]
    
    with open( get_path_typesystem , 'rb') as f:
        typesystem = load_typesystem(f)
            
    with tempfile.TemporaryDirectory() as output_dir:
        #1) check if we can train a deepsegment model using Glove embeddings
        train_deepsegment.main( get_path_txt , \
                               os.path.join( output_dir ) , \
                               get_path_embeddings , \
                               epochs=4 ,\
                               train_fraction=0.9, \
                               save_train_test_split=0, \
                               batch_size=64,\
                              )

        #2) check if we can load the trained model
        segmenter = DeepSegment(lang_code=None, checkpoint_path= os.path.join( output_dir  ,  'checkpoint') , \
                            params_path=os.path.join( output_dir , 'params' ) , \
                            utils_path= os.path.join(  output_dir , 'utils' ) , tf_serving=False, checkpoint_name=None)

        assert( isinstance( segmenter, DeepSegment ) )

        for document in test_documents:
        
            #3) make instance of TextSegmenter (this will load the trained DeepSegment into textsegmenter object)
            
            for segment_type in [ 'deepsegment', 'spacy' ]:
                
                cas = Cas( typesystem=typesystem )
    
                cas.sofa_string = document
                
                if segment_type=='deepsegment':
            
                    textsegmenter=TextSegmenter( cas, output_dir, segment_type=segment_type )
                
                elif segment_type=='spacy':
                    
                    textsegmenter=TextSegmenter( cas, 'en_core_web_lg' , segment_type=segment_type )

                #4) segment the sofa of the _InitialView of the cas, create html2textView, and add to Cas.
                textsegmenter.segment_and_add_to_cas( typesystem , OldSofaID="_InitialView" , NewSofaID='html2textView', \
                                              value_between_tagtype="com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType", tagName='p' )

                assert( isinstance( cas.get_view( "html2textView" ).sofa_string, str ) )

                #5) check if annotations are added correct
                segments = cas.get_view( "html2textView" ).sofa_string.split( "\n" )

                #sanity check of the segments
                assert " ".join( segments ) == document

                annotations = list( cas.get_view( "html2textView").select( "com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType" ) ) 

                assert( len( segments ) == len( annotations ) )

                for segment, annotation in zip( segments, annotations  ):
                    assert(segment == annotation.get_covered_text())
                