import random
import os
from deepsegment import train, generate_data 
import os

import io
from contextlib import redirect_stdout
import plac
from pathlib import Path

@plac.annotations(
    #input-output:
    segments=("Path to the training data. I.e. segments (separated with newlines).",),
    output_dir=("path to the output folder where deepsegment model will be saved",),
    embeddings_path=("path to pretrained embeddings",),
    #parameters for training
    train_fraction=( "fraction of data used for training", "option" ),
    seed=( "seed used for random shuffling of segments", "option" ),
    save_train_test_split=( "whether to save the sentences used for training and validation", "option" ),
    epochs=( "number of epochs", "option" ),
    batch_size=( "batch size used for training", "option" ),
    max_sents_per_example=( "maximum number of sentences sampled per sentence (generation of training/validation data)", "option" )
)
def main(segments: Path,
         output_dir: Path,
         embeddings_path: Path,
         train_fraction: float = .95,
         seed: int = 1,
         save_train_test_split: int=1 ,  #TODO: make boolean (issue with plac)
         epochs: int = 20,
         batch_size: int = 64,
         max_sents_per_example: int= 6
         ):
    
    '''
    Train a deepsegment model. Input segments will be split in training and validation data. 
    
    :param segments: Path. Segments.
    :param output_dir: Path. Path to the output folder where deepsegment model will be saved 
    :param embeddings_path: Path. Path to pretrained embeddings. 
    :param train_fraction: float. Fraction of data used for training.
    :param seed: float. Seed used for random shuffling of segments.
    :param save_train_test_split: int. Whether to save the sentences used for training and validation.
    :param epochs: int. Number of epochs.
    :param batch_size: int. Batch size used for training.
    :param max_sents_per_example: int. Maximum number of sentences sampled per sentence (generation of training/validation data).
    :return None.
    '''

    os.makedirs( output_dir, exist_ok=True  )
    
    sentences=open( segments ).read().rstrip("\n").split( "\n" )
    random.seed(seed)
    random.shuffle( sentences )

    train_size=int( len( sentences )*train_fraction)
    valid_size=len(sentences)-train_size
    
    print( "train size is:", train_size )
    print( "valid size is:", valid_size )
    
    if save_train_test_split:
        
        directory=os.path.dirname(  segments )
        basename=os.path.splitext( os.path.basename( segments ) )[0]
        train_file_name=os.path.join( directory, basename+".train"+".txt" ) 
        valid_file_name=os.path.join( directory, basename+".valid"+".txt" )
        
        with open(  train_file_name , "w" ) as f:
            print( f"writing train data to {train_file_name}" )
            f.write( "\n".join( sentences[:train_size] )  )

        with open( valid_file_name , "w" ) as f:
            print( f"writing valid data to {valid_file_name}" )
            f.write( "\n".join( sentences[train_size:] )  )    
               
    
    x, y = generate_data( sentences[:train_size] , max_sents_per_example=max_sents_per_example, n_examples=len( sentences[:train_size])  )
    vx, vy = generate_data( sentences[train_size:] , max_sents_per_example=max_sents_per_example, n_examples=len( sentences[train_size:] ) )

    #Fix for problem with logging in Deepsegment library
    f = io.StringIO()
    with redirect_stdout(f):
        train(x, y, vx, vy, epochs=epochs, batch_size=batch_size, save_folder=output_dir , glove_path= embeddings_path )
    out = f.getvalue()
    
    with open( os.path.join( output_dir, "deepsegment.log" ) , "w"  ) as f:
        f.write( out )

if __name__ == "__main__":
    plac.call(main)
