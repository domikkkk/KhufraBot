#include "queue.h"
#include <malloc.h>
#include <stdlib.h>
#include <math.h>


int compare_time(const void *a, const void *b){
    const miotly *miotlya = (const miotly *)a;
    const miotly *miotlyb = (const miotly *)b;
    return miotlya->t - miotlyb->t;
}


pair czasy(island *isl, int n, island dest) {
    miotly *m = calloc(n, sizeof(miotly));
    for (int i=0;i<n;i++) {
        m[i].i = &isl[i];
        m[i].t = distance(isl[i], dest) * M;
    }
    qsort(m, n, sizeof(miotly), compare_time);
    miotly *odp = ciag(m, n);
    free(m);
    n = (int)odp->t;
    filter(odp+1, &n);
    for (int i=0; i<n; i++) {
        odp[i] = odp[i+1];
    }
    odp = realloc(odp, n * sizeof(miotly));
    pair p;
    p.m = odp;
    p.n = n;
    return p;
}


miotly *ciag(miotly *m, int n) {
    int max_n = 0;
    miotly *isl;
    for (int i=0; i<n; i++) {
        int _n = 0;
        for (int j=0; j<n; j++) {
            float odl = fabs(m[j].t - m[i].t);
            int nn = rest(odl);
            if (odl <= nn * M + E_M && odl >= nn * M - E_M) {
                _n++;
            }
        }
        if (_n > max_n) {
            isl = &m[i];
        }
        max_n = max(_n, max_n);
    }
    miotly *odp = calloc(max_n+1, sizeof(miotly));
    odp->t = (float)max_n;
    odp++;
    for (int i=0; i<n; i++) {
        float odl = fabs(isl->t - m[i].t);
        int nn = rest(odl);
        if (odl <= nn * M + E_M && odl >= nn * M - E_M) {
            odp->i = m[i].i;
            odp->t = m[i].t;  // make a copy
            odp++;
        }
    }
    return odp-max_n-1;
}


int rest(float odl) {
    if (odl > M + E_M) goto ret1;
    if (odl > M - E_M) goto ret2;
    return 0;
ret1:
    return odl / M + rest(odl / (float)M);
ret2:
    return 1;
}


void filter(miotly *m, int *n) {
    int j = 0;
    for (int i=0; i<*n-1; i++) {
        if (m[i+1].t - m[i].t > M - E_M) {
            m[j++] = m[i];
        }
    }
    m[j++] = m[*n-1];
    *n = j;
}
