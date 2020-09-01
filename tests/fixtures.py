import os

import pytest

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_files")
    
    
@pytest.fixture(scope='function')
def get_path_xmi( request ):
    return os.path.join( FIXTURE_DIR , "xmi", request.param )
    
@pytest.fixture(scope='function')
def get_path_table( request ):
    return os.path.join( FIXTURE_DIR , "xmi", request.param )
    
@pytest.fixture(scope='function')
def get_path_typesystem( request ):
    return os.path.join( FIXTURE_DIR , "typesystems", request.param )

