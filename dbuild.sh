docker build \
--no-cache \
--build-arg DEEPSEGMENT_MODEL_PATH=tests/test_files/models/DEEPSEGMENT \
--build-arg TYPESYSTEM_PATH=tests/test_files/typesystems/typesystem.xml \
-t paragraph_annotation_app .

#docker build \
#--build-arg DEEPSEGMENT_MODEL_PATH=tests/test_files/models/DEEPSEGMENT \
#--build-arg TYPESYSTEM_PATH=tests/test_files/typesystems/typesystem.xml \
#-t paragraph_annotation_app .

