import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, LogFormatter
import os
import sys
import numpy as np

from tools import calc_FLOPS, load_benchmark_data, get_perf, B_TARGET_PANEL_WIDTH
from tools import calc_GFLOPs, get_AIs
from cpu_stats import xeon_8175M_stats, xeon_8124M_stats

# cpu stats
cpu_info = xeon_8124M_stats

if len(sys.argv) < 8:
    print("expected 7 arguments: mat_dir n_runs b_num_col test_gimmik TIMESTAMP plot_dir ref_is_dense")
    exit(1)

MAT_PATH = sys.argv[1]
N_RUNS = int(sys.argv[2])
B_NUM_COL = int(sys.argv[3])
TEST_GIMMIK = sys.argv[4]
TIMESTAMP = sys.argv[5]
PLOT_DIR = sys.argv[6]
REF_IS_DENSE = sys.argv[7]

LOG_DATA_DIR = "./bin/log_data"

mat_paths = sum([[os.path.join(dir, file) for file in files] \
    for dir, _, files in os.walk(MAT_PATH)], [])

mat_flops = calc_FLOPS(mat_paths, B_TARGET_PANEL_WIDTH)

runs = load_benchmark_data(N_RUNS, LOG_DATA_DIR, TIMESTAMP)

shapes = ["quad", "hex", "tet", "tri"]
shape_title = ["Quad", "Hex", "Tet", "Tri"]

for i_title, shape in enumerate(shapes):
    # get data
    # mat_names = [x for x in mat_paths if shape in x]
    data = []
    for i in range(N_RUNS):
        data.append(runs[i][shape])

    mat_names = data[0]["mat_file"]

    if TEST_GIMMIK == "1":
        custom_GFLOPs, ref_GFLOPs, gimmik_GFLOPs = \
            calc_GFLOPs(mat_flops, mat_names, data, B_NUM_COL, TEST_GIMMIK)
        if REF_IS_DENSE == "1":
            custom_AIs, ref_AIs, gimmik_AIs = get_AIs(mat_names, TEST_GIMMIK)
        else:
            custom_AIs, _, gimmik_AIs = get_AIs(mat_names, TEST_GIMMIK)
            ref_AIs = custom_AIs
    else:
        custom_GFLOPs, ref_GFLOPs = \
            calc_GFLOPs(mat_flops, mat_names, data, B_NUM_COL, TEST_GIMMIK)
        if REF_IS_DENSE == "1":
            custom_AIs, ref_AIs = get_AIs(mat_names, TEST_GIMMIK)
        else:
            custom_AIs, _ = get_AIs(mat_names, TEST_GIMMIK)
            ref_AIs = custom_AIs

    # plot rooflines
    fig = plt.figure(dpi=150)
    ax = fig.add_subplot(111)
    x = np.array([2**(-4), cpu_info["peak_flops_dp"]/cpu_info["peak_memory_bw"]])
    y = x*cpu_info["peak_memory_bw"]
    ax.plot(x, y)
    x = np.array([cpu_info["peak_flops_dp"]/cpu_info["peak_memory_bw"], 2**4])
    y = [cpu_info["peak_flops_dp"],cpu_info["peak_flops_dp"]]
    ax.plot(x, y, color='red', label="Double AVX512 Unit")
    x = np.array([(cpu_info["peak_flops_dp"]/2)/cpu_info["peak_memory_bw"], 2**4])
    y = [(cpu_info["peak_flops_dp"]/2),(cpu_info["peak_flops_dp"]/2)]
    ax.plot(x, y, color='black', label="Single AVX512 Unit")

    # plot data points
    ax.plot(custom_AIs[0], custom_GFLOPs[0], marker='x', color='limegreen', ms=1, label="Custom LIBXSMM")
    for i, mat_path in enumerate(mat_names):
        ax.plot(custom_AIs[i], custom_GFLOPs[i], marker='x', color='limegreen', ms=3)

    ax.plot(ref_AIs[0], ref_GFLOPs[0], marker='x', color='maroon', ms=1, label="Reference LIBXSMM")
    for i, mat_path in enumerate(mat_names):
        ax.plot(ref_AIs[i], ref_GFLOPs[i], marker='x', color='maroon', ms=3)

    if TEST_GIMMIK == "1":
        ax.plot(gimmik_AIs[0], gimmik_GFLOPs[0], marker='x', color='orange', ms=1, label="GiMMiK")
        for i, mat_path in enumerate(mat_names):
            ax.plot(gimmik_AIs[i], gimmik_GFLOPs[i], marker='x', color='orange', ms=3)

    # plot details
    ax.set_xscale('log', base=2)
    ax.set_yscale('log', base=2)
    ax.set_xticks([2**i for i in range(-4, 5)])
    ax.set_yticks([2**i for i in range(-2, 8)])
    #ax.xaxis.set_major_formatter(LogFormatter(base=2))
    ax.yaxis.set_major_formatter(LogFormatter(base=2))
    ax.set_xlabel('Arithmetic Intensity (FLOP/DRAM Byte)')
    ax.set_ylabel('Performance (Pseudo-GFLOP/s)')
    ax.set_title('Roofline - '+shape_title[i_title])
    plt.legend()
    plt.savefig(os.path.join(PLOT_DIR,"pyfr","roofline","{}_{}.pdf".format(shape, TIMESTAMP)), bbox_inches='tight')
