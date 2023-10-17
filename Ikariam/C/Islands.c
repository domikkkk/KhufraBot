#include "Islands.h"
#include <stdlib.h>
#include <math.h>
#include <malloc.h>


float distance(island a, island b) {
    return sqrt(((float)a.x - (float)b.x) * ((float)a.x - (float)b.x) + ((float)a.y - (float)b.y) * ((float)a.y - (float)b.y));
}


float calc_time(int h, int min, float sec) {
    return (float)h * 60.0 + (float)min + sec/60.0;
}


int compare_t(const void *a, const void *b){
    float _a = *((float *)a);
    float _b = *((float *)b);
    if (_a < _b) return -1;
    else if (_a > _b) return 1;
    else return 0;
}


float *get_distances() {
    float *times = calloc(N, sizeof(float));
    for (int i = 0; i < 5; i++) {
        for (int j = 0; j < 5; j++){
            times[5*i + j] = (1.0 + (float)i) * (1.0 + (float)j / 6.0);
        }
    }
    qsort(times, N, sizeof(float), compare_t);
    int j = 0;
    for (int i=0; i<N-1; i++) {
        if(times[i] != times[i+1]) {
            times[j++] = times[i];
        }
    }
    times[j++] = times[N-1];
    *(times + j) = 0;
    times = realloc(times, j*sizeof(float));
    return times;
}


island *find(island isl, float time) {
    float *dists = get_distances();
    float *cp = dists;
    island *posibilities = calloc(500, sizeof(island));
    island temp;
    int l=0;
    while (*dists != 0) {
        for (int x=1; x< 100; x++) {
            for (int y=1; y<100; y++) {
                temp.x = x;
                temp.y = y;
                float t = DIST * distance(isl, temp) / (*dists);
                if (t - time < EPSI && t - time > - EPSI) {
                    posibilities[l++] = temp;
                }
            }
        }
        posibilities[l].x = -1;
        posibilities[l++].y = -1;
        dists++;
    }
    posibilities[--l].x = 0;
    posibilities[l++].y = 0;
    free(cp);
    posibilities = realloc(posibilities, l * sizeof(island));
    return posibilities;
}
