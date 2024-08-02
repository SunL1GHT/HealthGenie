#!/bin/bash

DIR=`cd .. && pwd`

export MKL_SERVICE_FORCE_INTEL=1
export MKL_THREADING_LAYER=GNU

mkdir -p $DIR/huggingface

xtuner convert pth_to_hf $DIR/train/internlm2_5_chat_7b_qlora_alpaca_e3_med.py $DIR/train/iter_10559.pth $DIR/huggingface --max-shard-size 2GB