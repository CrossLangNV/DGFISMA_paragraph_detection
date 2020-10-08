import plac
import os
from pathlib import Path

import fasttext
from fasttext import load_model
from fasttext.FastText import _FastText

@plac.annotations(
    #input-output:
    data=("Path to the training data. I.e. sentences (separated with newlines).",),
    output_dir=("path to the output folder where fastText model will be saved"  ,),
    #parameters for training
    model=( "fastText architecture: 'skipgram' or 'cbow'", "option" ),
    epochs=( "number of epochs", "option" ),
    dim=( "embedding dimension", "option" ),
)
def main(data: Path,
         output_dir: Path,
         model: str = 'skipgram',
         epochs: int = 20, 
         dim: int = 100, 
         ) -> _FastText :
    '''
    Train a fastText model, and save the model both in .bin as in .vec format.
    
    :param data: Path. Path to the training data (sentences).
    :param output_dir: Path. Path to the output directory (where model.bin and model.vec will be saved).
    :param model: model architecture.
    :param epochs: number of epochs.
    :param dim: embedding dimension.
    :return model. fastText model.
    '''
    
    os.makedirs( output_dir, exist_ok=True  )

    model = fasttext.train_unsupervised(  data , model=model , epoch=epochs , dim=100 )
    model.save_model(  os.path.join( output_dir, "model.bin" ) )

    with open( os.path.join( output_dir, "model.vec" ) , "w" ) as vecfile:
        f = load_model( os.path.join( output_dir ,"model.bin" ) )
        words = f.get_words()
        vecfile.write( str(len(words)) + " " + str(f.get_dimension() ) + '\n'  )
        for w in words:
            v = f.get_word_vector(w)
            vstr = ""
            for vi in v:
                vstr += " " + str(vi)
            try:
                vecfile.write( w + vstr +"\n" )
            except IOError as e:
                if e.errno == errno.EPIPE:
                    pass
    
    return model
    
if __name__ == "__main__":
    plac.call(main)
