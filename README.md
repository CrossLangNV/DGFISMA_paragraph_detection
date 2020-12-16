
Instructions
------------

use "dbuild.sh" to build the docker image <br />
use "dcli.sh" to start a docker container

Make sure to:

1) Set the path to the correct typesystem in `dbuild.sh` ( e.g. https://github.com/CrossLangNV/DGFISMA_paragraph_detection/blob/master/tests/test_files/typesystems/typesystem.xml )

2) Set the path to a pretrained deepSegment model in `dbuild.sh` ( see https://github.com/CrossLangNV/DGFISMA_paragraph_detection/releases/tag/v1.0 ).

Given a json, e.g.: https://github.com/CrossLangNV/DGFISMA_paragraph_detection/blob/master/tests/test_files/json/minus_lesser_of.json , with a "cas_content" and "content_type" field, a json with the same fields will be returned (e.g. https://github.com/CrossLangNV/DGFISMA_paragraph_detection/blob/master/tests/test_files/response_json/small_nested_tables_response.json) , but with extra annotations and/or view added. 

The "cas_content" is a UIMA CAS object, encoded in base64. The "content_type" can be "html" or "pdf". 

If the content_type is "pdf", the sofa_string in the `_ InitialView` of the CAS (output of a pdf parser, e.g. Apache Tika) will be segmented by a pretrained [DeepSegment](https://pypi.org/project/deepsegment/) model. The segmented text will be added as a new view ( `html2textView`), and segments will be annotated as `com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType` with `tagName='p'`.

If the content_type is "html", and if enumerations are found, paragraph annotations will be added to the CAS object ( `de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph` ) on the 'html2textView', with `divType="enumeration"`.

I.e.: `cas.get_view( 'html2textView' ).select( "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph" )` will return a list containing all paragraph annotations. Using the `.get_covered_text()` method will return the covered text ( e.g. `cas.get_view( 'html2textView' ).select( "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph" ))[0].get_covered_text()` ).

We refer to tests/test_files/xmi/ for example xmi's, and to be extracted enumerations. Corresponding html's and json (containing CAS objects in base64) are also provided.

Note that currently, detection of enumeration, is only supported for "html" files (i.e. "cas_content" equal to "html" ). 

## DeepSegment:

This repository contains user scripts to train a DeepSegment model (`user_scripts/train_deepsegment.py`). One can either use pretrained embeddings (e.g. Glove embeddings http://nlp.stanford.edu/data/glove.6B.zip ), or train fastText embeddings (`user_scripts/train_fastText.py`).


1) Training data fastText/DeepSegment. 

The training data consists of 3M segments scraped from the EUR-lex website. 

(see https://github.com/CrossLangNV/DGFISMA_paragraph_detection/releases/tag/v1.0)

By selecting the text in between `p`tags of these scraped html's we obtained a collection of sentences that are well segmented. As an extra cleaning step, we limited ourself to segments containing more than 2 tokens, less than 1000 characters, and containing at least on alphabetic character.

The FastText model was trained on 3M segments, and the DeepSegment model on a random subset of 1M segments. 

See https://github.com/CrossLangNV/DGFISMA_paragraph_detection/releases/tag/v1.0 for pretrained FastText and DeepSegment models.


2) Train fastText embeddings:

```
from user_scripts import train_fasttext

train_fasttext.main( "input_sentences.txt" , \
                    "fasttext_output_dir",\
                    epochs=10 )
```

Or via command line:

*python train_fasttext \
input_sentences.txt \
output_dir \
-epochs 10*

3) Train DeepSegment:

```
from user_scripts import train_deepsegment

train_deepsegment.main( "input_sentences.txt" , \
                        "deepsegment_output_dir" , \
                       "fasttext_output_dir/model.vec"  , \
                       epochs=4 ,\
                       train_fraction=0.95, \
                       save_train_test_split=1, \
                       batch_size=64 )
```

Or via command line:

*python train_deepsegment \
input_sentences.txt \
deepsegment_output_dir \
fasttext_output_dir/model.vec \
-epochs 4 \
-train_fraction 0.95, \
-batch_size=64*

4) Evaluate Deepsegment:

```
from user_scripts import evaluate_deepsegment

evaluate_deepsegment.main( "sentences_valid.txt", \
                          "deepsegment_output_dir", \
                          n_window=20 )
```
                
Or via command line:

*python evaluate_deepsegment \
sentences_valid.txt \
deepsegment_output_dir \
-n_window 20*

The sentences used for validation should be segments split via newline ("\n"). The evaluation script will convert the sentences to the BIO format (B=first token of the segment, O: all tokens following this B, e.g.: "My first test sentence\n" -> B O O O), and return f1/precision/recall scores (B = positive label).

## Spacy segmenter

We also provide support for sentence segmentation with Spacy.

Given a CAS with to be segmented text in the sofa of the OldSofaID, one can add a new view (NewSofaID) with "spacy-segmented" text via:

```
from segment import TextSegmenter
textsegmenter=TextSegmenter( 'en_core_web_lg' , segment_type='spacy' )

textsegmenter.segment_and_add_to_cas( cas, typesystem , OldSofaID="_InitialView" , NewSofaID='html2textView', \
                              value_between_tagtype="com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType", tagName='p' )
```

## Comparison Spacy versus DeepSegment:

When evaluated on 1000 held out (EURLex) segments:


DeepSegment |  | precision | recall | f1-score | support |
--- | --- | --- | --- |--- |--- |
O | | 1.00 | 1.00 | 1.00 | 31573 | 
B | | 0.95 | 0.95 | 0.95 | 1000 | 


Spacy (*en_core_web_lg*) |  | precision | recall | f1-score | support |
--- | --- | --- | --- |--- |--- |
O | | 0.99 | 0.97 | 0.98 | 36895 | 
B | | 0.38 | 0.63 | 0.47 | 1000 | 


## Unit test

For unit test, run *pytest* from command line. 

Note, unit tests will only pass if glove (http://nlp.stanford.edu/data/glove.6B.zip) embeddings are located here: *tests/test_files/models/GLOVE/glove.6B.100d.txt*. 
