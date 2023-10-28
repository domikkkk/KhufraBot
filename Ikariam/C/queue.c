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
    return m;
}


island *ciag(miotly *m, int n) {
    for (int i=0; i<n; i++) {
        int max_n = 0;
        for (int j=0; j<n; i++) {
            int odl = fabs(m[j].t - m[i].t) / M;
            // if ()
        }
    }
}
