import pytest
import tempfile

from tests.fixtures import *
from user_scripts import train_deepsegment, train_fasttext
from deepsegment import DeepSegment

from fasttext.FastText import _FastText

import io
import numpy as np
from numpy import ndarray

@pytest.mark.parametrize("get_path_txt, get_path_embeddings", [
                        ("test_segments.txt", "glove.6B.100d.txt" ) ] ,
                         indirect=["get_path_txt", "get_path_embeddings" ])
def test_train_deepsegment( get_path_txt, get_path_embeddings ):
    
    with tempfile.TemporaryDirectory() as output_dir:
        #1 check if we can train a deepsegment model using Glove embeddings
        train_deepsegment.main( get_path_txt , \
                               os.path.join( output_dir ) , \
                               get_path_embeddings, \
                               epochs=4 ,\
                               train_fraction=0.9, \
                               save_train_test_split=0, \
                               batch_size=64,\
                              )

        #2 check if we can load the trained model
        segmenter = DeepSegment(lang_code=None, checkpoint_path= os.path.join( output_dir  ,  'checkpoint') , \
                            params_path=os.path.join( output_dir , 'params' ) , \
                            utils_path= os.path.join(  output_dir , 'utils' ) , tf_serving=False, checkpoint_name=None)
        
        assert isinstance(segmenter, DeepSegment)

        #3 and check if we can segment text
        test_sentence="test test"
        segments=segmenter.segment( test_sentence )
        segments_long=segmenter.segment_long( test_sentence, n_window=20 )

        assert isinstance( segments, list )
        for el in segments:
            assert isinstance( el, str )
        
        assert isinstance( segments_long, list )
        for el in segments_long:
            assert isinstance( el, str )
        
        assert " ".join( segments ) == test_sentence
        assert " ".join( segments_long ) == test_sentence
        
@pytest.mark.parametrize("get_path_txt", [
                        ("test_segments.txt" ) ] ,
                         indirect=["get_path_txt" ])  
def test_train_fasttext( get_path_txt ):
    
    with tempfile.TemporaryDirectory() as output_dir:        
        fasttext_model=train_fasttext.main( get_path_txt ,\
                           output_dir, \
                           epochs=4
                           )

        assert( isinstance( fasttext_model, _FastText ) )

        #check if we can load the vectors
        embeddings, id2word, word2id=_load_vec( os.path.join( output_dir, "model.vec" ), nmax=len( fasttext_model.get_words() ) )

        #check if the .vec model is the same as the .bin model for words that are not OOV
        for word in fasttext_model.get_words():
            assert( np.array_equal( embeddings[ word2id[ word ] ].astype( np.float32 ), fasttext_model[ word ].astype( np.float32 )  ) )


def _load_vec(emb_path: str, nmax : int =50000) -> (ndarray, dict, dict):
    
    '''
    Utility function to load .vec models
    
    :param emb_path: path to .vec file.
    :param nmax
    :return embeddings (numpy ndarray), id2word (dict) , word2id (dict).
    '''
    
    vectors = []
    word2id = {}
    with io.open(emb_path, 'r', encoding='utf-8', newline='\n', errors='ignore') as f:
        next(f)
        for i, line in enumerate(f):
            word, vect = line.rstrip().split(' ', 1)
            vect = np.fromstring(vect, sep=' ')
            assert word not in word2id, 'word found twice'
            vectors.append(vect)
            word2id[word] = len(word2id)
            if len(word2id) == nmax:
                break
    id2word = {v: k for k, v in word2id.items()}
    embeddings = np.vstack(vectors)
    return embeddings, id2word, word2id