#include "Islands.h"


#define M 30
#define E_M 3  // epsilon
#define max(a, b) ((a)>(b)?(a):(b))


typedef struct {
    island *i;
    float t;
} miotly;


typedef struct {
    miotly *m;
    int n;
} pair;


int compare_time(const void *a, const void *b);
int rest(float odl);
pair czasy(island *isl, int n, island dest);
miotly *ciag(miotly *m, int n);
void filter(miotly *m, int *n);
