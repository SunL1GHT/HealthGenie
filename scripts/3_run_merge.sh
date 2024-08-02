#!/bin/bash

DIR=`cd .. && pwd`

export MKL_SERVICE_FORCE_INTEL=1
export MKL_THREADING_LAYER=GNU

mkdir -p $DIR/final_model

xtuner convert merge /share/new_models/Shanghai_AI_Laboratory/internlm2_5-7b-chat $DIR/huggingface $DIR/final_model