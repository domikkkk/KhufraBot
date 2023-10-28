#include "Islands.h"


#define M 30
#define E_M 1


typedef struct {
    island *i;
    float t;
} miotly;

int compare_time(const void *a, const void *b);
miotly *czasy(island *isl, int n, island dest);
int ciag(miotly *m, int n);
