#!/bin/bash


#export PATH=/u/makarov/cuda-9.0/bin:$PATH
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/u/makarov/cuda-9.0/extras/CUPTI/lib64
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/u/makarov/cuda-9.0/lib64

#source /u/makarov/rimes-testing/ENV/bin/activate

export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/local/cuda-9.0/lib64:/usr/local/cudnn-9.0-v7.1/lib64

source /u/bahar/settings/python3-returnn-tf1.9/bin/activate


python3 /u/makarov/returnn-hmm-fac/rnn.py $1


