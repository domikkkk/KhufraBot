#include "queue.h"
#include <malloc.h>
#include <stdlib.h>


int compare_time(const void *a, const void *b){
    const miotly *miotlya = (const miotly *)a;
    const miotly *miotlyb = (const miotly *)b;
    return miotlyb->t - miotlya->t;
}


miotly *czasy(island *i, island dest) {
    int j = 0, l = 0;
    while (i[j++].x != '\0');
    l = j;
    miotly *m = calloc(j, sizeof(miotly));
    while (j-->0) {
        m[j].i = &i[j];
        m[j].t = distance(i[j], dest) * M;
    }
    qsort(m, l, sizeof(miotly), compare_time);
    return m;
}
