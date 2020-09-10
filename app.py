#!/usr/local/bin/python
from flask import Flask
from flask import request
from flask import abort

import binascii
import base64

from cassis.typesystem import load_typesystem
from cassis.xmi import load_cas_from_xmi

from src.annotations import annotate_lists_eurlex_html, annotate_lists_pdf

app = Flask(__name__)
   
TYPESYSTEM_PATH="/work/typesystems/typesystem.xml"
    
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

        annotate_lists_pdf( cas )

    elif request.json[ 'content_type'] == 'html' or request.json[ 'content_type'] == 'xhtml':

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