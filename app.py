#!/usr/local/bin/python
from flask import Flask
from flask import request
from flask import abort

import binascii
import base64

from cassis.typesystem import load_typesystem
from cassis.xmi import load_cas_from_xmi

from src.annotations import annotate_lists_eurlex_html, annotate_lists_flat_html_pdf, is_old_eurlex
from src.segment import TextSegmenter

app = Flask(__name__)
   
TYPESYSTEM_PATH="/work/typesystems/typesystem.xml"
DEEPSEGMENT_MODEL_PATH="/work/deepsegment_model"
    
textsegmenter=TextSegmenter( DEEPSEGMENT_MODEL_PATH )

@app.route('/annotate_paragraphs', methods=['POST'])
def annotate_paragraphs():    
    if not request.json:
        abort(400)
    output_json={}
    
    if ('cas_content' not in request.json) or ( 'content_type' not in request.json ):
        print( "'cas_content' and/or 'content type' field missing" )
        output_json['cas_content']=''
        output_json['content_type']=''
        return output_json
        
    try:
        decoded_cas_content=base64.b64decode( request.json[ 'cas_content' ] ).decode( 'utf-8' )
    except binascii.Error:
        print( f"could not decode the 'cas_content' field. Make sure it is in base64 encoding." )
        output_json['cas_content']=''
        output_json['content_type']=request.json[ 'content_type' ]
        return output_json

    with open( TYPESYSTEM_PATH , 'rb') as f:
        typesystem = load_typesystem(f)

    #load the cas:
    cas=load_cas_from_xmi( decoded_cas_content, typesystem=typesystem  )
        
    
    if request.json[ 'content_type'] == 'pdf':
        
        
        #use deepsegment model to segment the sofa ( _InitialView, result of Apache TiKa pdfparser)
        textsegmenter.segment_and_add_to_cas( cas, typesystem , OldSofaID="_InitialView" , NewSofaID='html2textView', \
                                  value_between_tagtype="com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType", tagName='p' )
        
        #no annotation of the paragraphs for pdf (i.e. lists/sublist), would introduce too much noise

    elif request.json[ 'content_type'] == 'html' or request.json[ 'content_type'] == 'xhtml':
        
        if is_old_eurlex(cas, "html2textView" ):

            annotate_lists_flat_html_pdf( cas, typesystem, "html2textView" )

        else:

            annotate_lists_eurlex_html( cas, typesystem, "html2textView")

    else:
        print( f"content type { request.json[ 'content_type'] } not supported by paragraph annotation app" )   
        output_json['cas_content']=request.json['cas_content']
        output_json['content_type']=request.json[ 'content_type' ]
        return output_json   
    
    #.decode() because json can't serialize a bytes type object.
    output_json['cas_content']=base64.b64encode(  bytes( cas.to_xmi()  , 'utf-8' ) ).decode()   
    output_json[ 'content_type']=request.json[ 'content_type']
        
    return output_json
    
@app.route('/')
def index():
    return "Up and running"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)
