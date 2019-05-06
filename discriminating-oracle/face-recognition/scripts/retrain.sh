#!/bin/bash

tensorflow_hub_examples="/Users/adi/dev/github/open-source/tensorflow/hub/examples"
dataset="$(pwd)/../dataset-cropped"

python3 $tensorflow_hub_examples/image_retraining/retrain.py \
    --image_dir $dataset \
    --tfhub_module https://tfhub.dev/google/imagenet/mobilenet_v2_075_224_quant/feature_vector/1
