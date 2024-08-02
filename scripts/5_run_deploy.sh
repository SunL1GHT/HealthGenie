#!/bin/bash

DIR=`cd .. && pwd`

export MKL_SERVICE_FORCE_INTEL=1
export MKL_THREADING_LAYER=GNU

lmdeploy serve api_server $DIR/internlm2_5-7b-chat --model-name genie_chat --server-port 10001
# lmdeploy serve api_server /share/new_models/Shanghai_AI_Laboratory/internlm2_5-7b-chat --model-name genie_chat --server-port 10001