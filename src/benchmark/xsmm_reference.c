#include <assert.h>
#include <cblas.h>
#include <float.h>
#include <inttypes.h>
#include <libxsmm.h>
#include <libxsmm_main.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>

#include "common.h"
#include "xsmm_common.h"

#define DEBUG 0

int main(int argc, char** argv) {
  libxsmm_dfsspmdm* xsmm_d = NULL;
  double* a_d = NULL;
  double* b_d = NULL;
  double* c_xsmm_d = NULL;
  int m = 0, n = 0, k = 0;
  int c_size = 0;

  char const* const run_type = "xsmm-reference";

  prepare_benchmark(argc, argv, &xsmm_d, &a_d, &b_d, &c_xsmm_d, &m, &n, &k,
                    &c_size, false, NULL);

  // Check kernel type
  print_kernel_type(xsmm_d, run_type);

  // flush cache
  flush_cache();

  struct benchmark_data b_data = benchmark_xsmm_1iter(b_d, c_xsmm_d, n, xsmm_d, run_type);

  printf("%s", "Done.\n");
  printf("---------------------------------------------------------------\n");
  printf("%s best execution time: %.17g\n", run_type, b_data.fastest_time);
  printf("%s avg execution time: %.17g\n", run_type, b_data.avg_iqr_time);

  free(a_d);
  free(b_d);
  free(c_xsmm_d);
}
