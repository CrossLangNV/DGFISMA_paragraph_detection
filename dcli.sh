#docker run -it --rm -p 5000:5000 --entrypoint /bin/bash -v $PWD:/train paragraph_annotation_app
docker run -it --rm -p 5000:5000 -v $PWD:/train paragraph_annotation_app
