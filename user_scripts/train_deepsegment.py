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
    batch_size=( "batch size used for training", "option" )
)
def main(segments: Path,
         output_dir: Path,
         embeddings_path: Path,
         train_fraction: float = .95,
         seed: int = 1,
         save_train_test_split: int=1 ,  #TODO: make boolean (issue with plac)
         epochs: int = 20,
         batch_size: int = 64,
         ):
    
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
               
    
    x, y = generate_data( sentences[:train_size] , max_sents_per_example=6, n_examples=len( sentences[:train_size])  )
    vx, vy = generate_data( sentences[train_size:] , max_sents_per_example=6, n_examples=len( sentences[train_size:] ) )

    f = io.StringIO()
    with redirect_stdout(f):
        train(x, y, vx, vy, epochs=epochs, batch_size=batch_size, save_folder=output_dir , glove_path= embeddings_path )
    out = f.getvalue()
    
    with open( os.path.join( output_dir, "deepsegment.log" ) , "w"  ) as f:
        f.write( out )

if __name__ == "__main__":
    plac.call(main)
