
Instructions
------------

use "dbuild.sh" to build the docker image <br />
use "dcli.sh" to start a docker container

Make sure to:

1) Set the path to the correct typesystem in dbuild.sh ( e.g. https://github.com/CrossLangNV/DGFISMA_paragraph_detection/blob/master/tests/test_files/typesystems/typesystem.xml )

2) Set the path to a pretrained deepSegment model in dbuild.sh.

Given a json, e.g.: https://github.com/CrossLangNV/DGFISMA_paragraph_detection/blob/master/tests/test_files/json/minus_lesser_of.json , with a "cas_content" and "content_type" field, a json with the same fields will be returned (e.g. https://github.com/CrossLangNV/DGFISMA_paragraph_detection/blob/master/tests/test_files/response_json/small_nested_tables_response.json) , but with paragraph annotations added. 

The "cas_content" is a UIMA CAS object, encoded in base64. The "content_type" can be "html" or "pdf". 

If the content_type is "pdf", the sofa_string in the "_ InitialView" of the cas (output of a pdf parser, e.g. Apache Tika) will be segmented by a pretrained deepSegment model https://github.com/notAI-tech/deepsegment . The segmented text will be added as new view ( 'html2textView'), and segments will be annotated as "com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType" with tagName='p'.

If lists/sublists are found, paragraph annotations will be added to the Cas object ( "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph" ) on the 'html2textView', with divType="enumeration".

I.e.: cas.get_view( 'html2textView' ).select( "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph" ) will return a generator containing all paragraph annotations. Using the .get_covered_text() method will return the covered text ( e.g. List(cas.get_view( 'html2textView' ).select( "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph" ))[0].get_covered_text() ).

We refer to tests/test_files/xmi/ for example xmi's, and to be extracted lists and sublists. Corresponding html's and json (containing Cas objects in base64) are also provided.


## DeepSegment:

This repository contains user scripts to train a DeepSegment model (user_scripts/train_deepsegment.py). One can either use pretrained embeddings (e.g. Glove embeddings http://nlp.stanford.edu/data/glove.6B.zip ), or train fastText embeddings (user_scripts/train_fastText).

1) Train fastText embeddings:

*from user_scripts import train_fasttext*

*train_fasttext.main( "input_sentences.txt" , \
                    "fasttext_output_dir",\
                    epochs=10 )*

Or via command line:

*python train_fasttext \
input_sentences.txt \
output_dir \
-epochs 10*

2) Train DeepSegment:

*from user_scripts import train_deepsegment*

*train_deepsegment.main( "input_sentences.txt" , \
                        "deepsegment_output_dir" , \
                       "fasttext_output_dir/model.vec"  , \
                       epochs=4 ,\
                       train_fraction=0.95, \
                       save_train_test_split=1, \
                       batch_size=64 )*

Or via command line:

*python train_deepsegment \
input_sentences.txt \
deepsegment_output_dir \
fasttext_output_dir/model.vec \
-epochs 4 \
-train_fraction 0.95, \
-batch_size=64*

3) Evaluate Deepsegment:

*from user_scripts import evaluate_deepsegment
evaluate_deepsegment.main( "sentences_valid.txt", \
                          "deepsegment_output_dir", \
                          n_window=20 )*
                
Or via command line:

*python evaluate_deepsegment \
sentences_valid.txt \
deepsegment_output_dir \
-n_window 20*

The sentences used for validation should be segments split via newline ("\n"). The evaluation script will convert the sentences to the BIO format (B=first token of the segment, O: all tokens following this B, e.g.: "My first test sentence\n" -> B O O O), and return f1/precision/recall scores (B = positive label).

## Spacy segmenter

We also provide support for sentence segmentation with Spacy.

Given a Cas with to be segmented text in the sofa of the OldSofaID, one can add a new view (NewSofaID). 

*from segment import TextSegmenter
textsegmenter=TextSegmenter( cas, 'en_core_web_lg' , segment_type=segment_type )

textsegmenter.segment_and_add_to_cas( typesystem , OldSofaID="_InitialView" , NewSofaID='html2textView', \
                              value_between_tagtype="com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType", tagName='p' )*


## Unit test

For unit test, run *pytest* from command line. 

Note, unit tests will only pass if glove (http://nlp.stanford.edu/data/glove.6B.zip) embeddings are located here: *tests/test_files/models/GLOVE/glove.6B.100d.txt*. 