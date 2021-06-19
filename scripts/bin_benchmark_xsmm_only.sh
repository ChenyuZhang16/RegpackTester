#!/usr/bin/env bash

export LD_LIBRARY_PATH=~/OpenBlas-build/lib:$LD_LIBRARY_PATH

nice -20 taskset -c 0 bin/benchmark_xsmm_only $1 $2

if [ $3 -eq 1 ]; # gimmik
then
  nice -20 taskset -c 0 bin/benchmark_gimmik $1 $2
fi
