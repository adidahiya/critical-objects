#!/bin/bash

training_output="$(pwd)/../tensorflow/training-2"

tflite_convert \
  --graph_def_file=$training_output/output_graph.pb \
  --output_file=$training_output/optimized_graph.tflite \
  --input_format=TENSORFLOW_GRAPHDEF \
  --output_format=TFLITE \
  --input_shape=1,224,224,3 \
  --input_array=Placeholder \
  --output_array=final_result \
  --inference_type=FLOAT \
  --input_data_type=FLOAT
