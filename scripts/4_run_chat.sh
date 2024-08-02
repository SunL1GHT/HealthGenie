#!/bin/bash

DIR=`cd .. && pwd`

export MKL_SERVICE_FORCE_INTEL=1
export MKL_THREADING_LAYER=GNU

xtuner chat $DIR/final_model --prompt-template internlm2_chat --system-template medical