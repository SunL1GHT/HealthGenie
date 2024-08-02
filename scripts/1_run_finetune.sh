#!/bin/bash
# export CUDA_DEVICE_MAX_CONNECTIONS=1
DIR=`cd .. && pwd`

echo $DIR

mkdir -p $DIR/train

xtuner train $DIR/config/internlm2_5_chat_7b_qlora_alpaca_e3_med.py --work-dir $DIR/train --deepspeed deepspeed_zero2