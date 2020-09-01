
Instructions
------------

use "dbuild.sh" to build the docker image <br />
use "dcli.sh" to start a docker container

Make sure to set the path to the correct typesystem in dbuild.sh ( e.g. https://github.com/CrossLangNV/DGFISMA_paragraph_detection/blob/master/tests/test_files/typesystems/typesystem.xml )

Given a json, e.g.: https://github.com/CrossLangNV/DGFISMA_paragraph_detection/blob/master/tests/test_files/json/minus_lesser_of.json , with a "cas_content" and "content_type" field, a json with the same fields will be returned, but with paragraph annotations added. 

The "cas_content" is a UIMA CAS object, encoded in base64. The "content_type" can be "html" or "pdf". 

If lists/sublists are found, paragraph annotations will be added to the Cas object ( "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph" ) on the 'html2textView', with divType="enumeration".

I.e.: cas.get_view( 'html2textView' ).select( "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph" ) will return a generator containing all paragraph annotations. Using the .get_covered_text() method will return the covered text ( e.g. List(cas.get_view( 'html2textView' ).select( "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph" ))[0].get_covered_text() ).

We refer to tests/test_files/xmi/ for example xmi's, and to be extracted lists and sublists. Corresponding html's and json (containing Cas objects in base64) are also provided.