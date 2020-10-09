import os
import plac
from pathlib import Path

import logging
logging.basicConfig(level=logging.ERROR)
from deepsegment import DeepSegment
from sklearn.metrics import classification_report


@plac.annotations(
    #input-output:
    segments=("Path to the test data. I.e. segments (separated with newlines).",),
    model_dir=("Path to the folder where deepsegment model is located.",),
    n_window=( "Window used for segmentation with segment_long method of DeepSegment. Set n_window=0 for segmentation with segment method.", "option" ),
)
def main(segments: Path,
         model_dir: Path,
         n_window: int = 20,
         ) -> (list, list ) :
    
    '''
    Evaluate a deepsegment model. Segments will be converted to BIO fomat using utility function _convert_to_bio. 
    
    :param segments: Path. Segments.
    :param model_dir: Path. Path to the folder where deepsegment model is located.
    :param n_window: Window used for segmentation with segment_long method of DeepSegment. Set n_window=0 for segmentation with segment method.
    :
    :return Tuple. Two lists: true labels and predicted labels (BIO tagging).
    '''
    
    sentences=open( segments ).read().rstrip("\n").split("\n")
    sentences=[ sentence.strip() for sentence in sentences if sentence.strip() ]
    concat_text=" ".join( sentences )
    
    segmenter = DeepSegment(lang_code=None, checkpoint_path= os.path.join( model_dir, 'checkpoint' ), \
                        params_path=os.path.join( model_dir, 'params' ), utils_path= os.path.join(  model_dir, 'utils') , tf_serving=False, checkpoint_name=None)

    if n_window:
        predict=segmenter.segment_long( concat_text, n_window=n_window )
    else:
        predict=segmenter.segment( concat_text )
        
    y_true=_convert_to_bio( sentences )
    y_pred=_convert_to_bio( predict )

    print( classification_report( y_true, y_pred ) )
    
    return y_true, y_pred
    

def _convert_to_bio( sentences: list ) -> list:
    y=[]
    for line in sentences:
        words = line.strip().split()
        for word_i, word in enumerate(words):
            #x[-1].append(word)
            label =  0 #'O': inside of a sentence
            if word_i == 0:
                label = 1 #'B-sent': the beginning of the sentence
            y.append(label)
    return y