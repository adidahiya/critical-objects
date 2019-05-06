#!/bin/bash

label_image="/Users/adi/dev/github/open-source/tensorflow/tensorflow/tensorflow/examples/label_image/label_image.py"
training_output="$(pwd)/../tensorflow/training-1"

python3 $label_image \
    --graph=$training_output/output_graph.pb \
    --labels=$training_output/output_labels.txt \
    --input_width=224 \
    --input_height=224 \
    --input_layer=Placeholder \
    --output_layer=final_result \
    --image=test-image.jpg
