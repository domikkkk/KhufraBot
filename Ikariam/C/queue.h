#include "Islands.h"


#define M 30


typedef struct {
    island *i;
    float t;
} miotly;

int compare_time(const void *a, const void *b);
miotly *czasy(island *is, int n, island dest);
