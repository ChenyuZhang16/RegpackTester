#!/bin/bash

WD=$(pwd)

XSMM_REFERENCE_DIR=./../libxsmm_reference
XSMM_CUSTOM_DIR=./../libxsmm_custom
GIMMIK_DIR=./../GiMMiK

B_NUM_COL=192000

REF_IS_DENSE="0"
TEST_GIMMIK="0"
N_RUNS=3
SKIP_BENCH="0" # 0 don't skip, otherwise == timestamp of previous benchmark
N_ITER=60 # number of iterations for each run
MATRIX_SIZE=288000000 # 1500*192000 DP numbers, taking 2197.27 MB
ENVS=""
N_WIDTHS=""

while getopts ":d:g:m:t:o:p:n:s:i:e:w:" opt; do
  case $opt in
    d) REF_IS_DENSE="$OPTARG"
    ;;
    g) TEST_GIMMIK="$OPTARG"
    ;;
    m) MATS_DIR="$OPTARG"
    ;;
    t) MAT_TYPE="$OPTARG" # pyfr or synth
    ;;
    o) LOG_DIR="$OPTARG"
    ;;
    p) PLOT_DIR="$OPTARG"
    ;;
    n) N_RUNS=$OPTARG
    ;;
    s) SKIP_BENCH="$OPTARG"
    ;;
    i) N_ITER=$OPTARG
    ;;
    e) ENVS="$OPTARG"
    ;;
    w) N_WIDTHS="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

# clean binary benchmark executable file (just in case)
make clean

# run benchmark
if [ "$SKIP_BENCH" = "0" ]
then
  
  echo error!!!

else
  TIMESTAMP=$SKIP_BENCH
  LOG_DIR=$LOG_DIR/$TIMESTAMP
fi

# Sort log data and pickle for plotting
mkdir -p bin/log_data
python3 src/plot/pickle_runs.py $MAT_TYPE $N_RUNS $LOG_DIR $TIMESTAMP $TEST_GIMMIK "$N_WIDTHS" "$ENVS"

# Plot
if [ "$MAT_TYPE" = "pyfr" ]
then
  mkdir -p $PLOT_DIR/$TIMESTAMP/pyfr/quad
  mkdir -p $PLOT_DIR/$TIMESTAMP/pyfr/hex
  mkdir -p $PLOT_DIR/$TIMESTAMP/pyfr/tet
  mkdir -p $PLOT_DIR/$TIMESTAMP/pyfr/tri
  mkdir -p $PLOT_DIR/$TIMESTAMP/pyfr/roofline

  python3 src/plot/pyfr_report.py $MATS_DIR $N_RUNS $B_NUM_COL $TEST_GIMMIK $TIMESTAMP $PLOT_DIR/$TIMESTAMP "$ENVS"
  python3 src/plot/pyfr_roofline_report.py $MATS_DIR $N_RUNS $B_NUM_COL $TEST_GIMMIK $TIMESTAMP $PLOT_DIR/$TIMESTAMP $REF_IS_DENSE "$ENVS"
  # python3 src/plot/pyfr_report.py $N_RUNS $TEST_GIMMIK $TIMESTAMP "$ENVS" > $PLOT_DIR/$TIMESTAMP/summary.txt
elif [ "$MAT_TYPE" = "synth" ]
then
  echo dummy
  # mkdir -p $PLOT_DIR/$TIMESTAMP/synth
  # mkdir -p $PLOT_DIR/$TIMESTAMP/synth/roofline

  # python3 src/plot/synth.py $MATS_DIR $N_RUNS $B_NUM_COL $TEST_GIMMIK $TIMESTAMP $PLOT_DIR/$TIMESTAMP "$ENVS"
  # python3 src/plot/synth_roofline.py $MATS_DIR $N_RUNS $B_NUM_COL $TEST_GIMMIK $TIMESTAMP $PLOT_DIR/$TIMESTAMP $REF_IS_DENSE "$ENVS"
fi