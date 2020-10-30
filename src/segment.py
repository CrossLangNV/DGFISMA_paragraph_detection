import os
from cassis import Cas
from cassis.typesystem import TypeSystem

import logging
logging.basicConfig(level=logging.ERROR) #fix loggin issue with deepsegment
from deepsegment import DeepSegment
import spacy

from src.utils import concat_list_spellcheck

class TextSegmenter():
    
    '''
    Segment the sofa of a Cas.
    '''
        
    def __init__( self, cas: Cas, segment_path: str, segment_type: str= 'deepsegment' ):
        
        '''
        :param cas: Cas. Cas object (mutable object).
        :param segment_path. Str. Path to the segmentation model/name of the spacy model.
        :param segment_type. Str. Type of segmentation model used: deepsegment or spacy.
        '''
        
        self.cas=cas
        self.segment_path=segment_path
        if segment_type not in [ 'deepsegment', 'spacy' ]:
            raise ValueError(f"segment type {self.segment_type} not supported. Only 'deepsegment' and 'spacy' segmenters are supported.")
        else:
            self.segment_type=segment_type
        
        
    def segment_and_add_to_cas( self, typesystem: TypeSystem , OldSofaID: str="_InitialView" , NewSofaID: str='html2textView', value_between_tagtype: \
                            str="com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType", tagName:str='p' ):
        
        '''
        Create new view (sofa) and add segments to the view as value_between_tagtype, with tagName.

        :param typesystem: cassis.typesystem.Typesystem. Corresponding Typesystem of the cas.
        :param OldSofaID: String. Name of the old sofa.
        :param NewSofaID: String. Name of the new sofa.
        :param value_between_tagtype: String. 
        :param tagname: String.
        :return: None.        
        '''
        
        if self.segment_type=='deepsegment':
            self.load_deepsegment()
            self.segment_deepsegment()
        elif self.segment_type=='spacy':
            self.load_spacy_model()
            self.segment_spacy()
        else:
            raise ValueError(f"segment type {self.segment_type} not supported. Only 'deepsegment' and 'spacy' segmenters are supported.")
            
        self.add_segments_to_cas( typesystem, OldSofaID=OldSofaID, NewSofaID=NewSofaID, value_between_tagtype=value_between_tagtype, tagName=tagName )
        
        
    def load_deepsegment( self ):
        
        '''
        Load deepsegment model.
        
        :return: None.
        '''
        
        if not hasattr(self, 'segmenter'):
            print( f"loading deepsegment from {self.segment_path}" )
            self.segmenter = DeepSegment(lang_code=None, checkpoint_path= os.path.join( self.segment_path, 'checkpoint') , params_path=os.path.join( self.segment_path, 'params' ) , utils_path= os.path.join(  self.segment_path, 'utils' ) , tf_serving=False, checkpoint_name=None)
    
    
    def segment_deepsegment( self, n_window: int = 20 ):
        
        '''
        Segment the sofa using pretrained deepsegment model.
        Function utils.concat_list_spellcheck is used to remove newlines and fix words split with "-" via a spellchecker.

        :param n_window: int. Window size.
        :return: list. List of strings (segments).     
        '''
        
        concatenated_text = concat_list_spellcheck( self.cas.sofa_string.split( "\n" ) )
        
        if not concatenated_text :
            self.segments=[""]
            return self.segments
        
        self.segments=self.segmenter.segment_long( concatenated_text, n_window=n_window )
        return self.segments
      
        
    def load_spacy_model( self ):
        
        '''
        Load spacy model.
        
        :return: None.
        '''
        
        print( f"loading spacy model {self.segment_path}" )
        self.segmenter=spacy.load( self.segment_path )
        
    def segment_spacy(self ):    
        
        '''
        Segment the sofa using spacy model.
        Function utils.concat_list_spellcheck is used to remove newlines and fix words split with "-" via a spellchecker.

        :param n_window: int. Window size.
        :return: list. List of strings (segments).     
        '''
        
        concatenated_text = concat_list_spellcheck( self.cas.sofa_string.split( "\n" ) )

        if not concatenated_text :
            self.segments=[""]
            return self.segments
        
        spacy_sentences=[]
        batch_size=self.segmenter.max_length #spacy model has a limit of 1000000 characters
        chunks = (len( concatenated_text ) - 1) // batch_size + 1  
        for i in range( chunks ):
            batch=concatenated_text[ i*batch_size:(i+1)*batch_size ]    
            spacy_sentences+=[ sentence.text for sentence in self.segmenter( batch ).sents ]

        self.segments=spacy_sentences
        
        return self.segments

     
    def add_segments_to_cas( self, typesystem: TypeSystem , OldSofaID: str="_InitialView" , NewSofaID: str='html2textView', \
                            value_between_tagtype: str="com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType", tagName: str='p' ):
        
        '''
        Create new view (sofa) and add segments (self.segments) obtained via segmenter to the view as value_between_tagtype

        :param typesystem: cassis.typesystem.Typesystem. Corresponding Typesystem of the cas.
        :param OldSofaID: String. Name of the old sofa.
        :param NewSofaID: String. Name of the new sofa.
        :param value_between_tagtype: String. 
        :param tagname: String.
        :return: None.        
        '''
                
        self.cas.create_view( NewSofaID )
        self.cas.get_view( NewSofaID ).sofa_string = "\n".join( self.segments )

        #check if provided typesystem has type value_between_tagtype
        try:
            vbtt = typesystem.get_type( value_between_tagtype )
        except Exception as error:
            print( f"value_between_tagtype ({value_between_tagtype}) should be in the provided typesystem"  )
            print( error)
            raise
            
        #check if vbtt has tagName (sanity check).
        try:
            assert( ("tagName" in [feature.name for feature in vbtt.features]) ==True )
        except AssertionError as error:
            print( f"value_between_tagtype ({value_between_tagtype}) should have a feature with name 'tagName'" )
            print( error )
            raise
            
        position=0
        for segment in self.segments:
            self.cas.get_view( NewSofaID ).add_annotation( vbtt( begin=position, end=position+len(segment), tagName='p' ) )
            position+=(len(segment)+1 )  #+1 to skip the "\n" at the end of the string
        
