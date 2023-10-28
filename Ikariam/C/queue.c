#include "queue.h"
#include <malloc.h>
#include <stdlib.h>
#include <math.h>


int compare_time(const void *a, const void *b){
    const miotly *miotlya = (const miotly *)a;
    const miotly *miotlyb = (const miotly *)b;
    return miotlya->t - miotlyb->t;
}


miotly *czasy(island *isl, int n, island dest) {
    miotly *m = calloc(n, sizeof(miotly));
    for (int i=0;i<n;i++) {
        m[i].i = &isl[i];
        m[i].t = distance(isl[i], dest) * M;
    }
    qsort(m, n, sizeof(miotly), compare_time);
    int x = ciag(m, n);
    printf("%d\n", x);
    return m;
}


int ciag(miotly *m, int n) {
    int max_n = 0;
    for (int i=0; i<n; i++) {
        int _n = 0;
        for (int j=0; j<n; i++) {
            float odl = fabs(m[j].t - m[i].t);
            int nn = odl / M;
            if (odl <= nn * M + E_M && odl >= nn * M - E_M) {
                _n++;
            }
        }
        max_n = fmax(_n, max_n);
    }
    return max_n;
}
