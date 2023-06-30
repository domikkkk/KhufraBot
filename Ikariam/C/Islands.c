#include "Islands.h"
#include "qsort.h"
#include <math.h>
#include <malloc.h>


float distance(island a, island b) {
    return sqrt(((float)a.x - (float)b.x) * ((float)a.x - (float)b.x) + ((float)a.y - (float)b.y) * ((float)a.y - (float)b.y));
}


float calc_time(int h, int min, float sec) {
    return (float)h * 60.0 + (float)min + sec/60.0;
}


float *get_distances(float time, float epsi) {
    float *times = calloc(25, sizeof(float));
    for (int i = 0; i < 5; i++) {
        for (int j = 0; j < 5; j++){
            times[5*i + j] = time * (1.0 + (float)i) * (1.0 + (float)j / 6.0) / DIST;
            times[5*i + j] *= times[5*i + j];
        }
    }
    qqsort(times, 0, 24);
    int l = 0;
    // for (int i=0; i<25; i++) {
    //     printf("%f  ", times[i]);
    // }
    for (int i = 0; i < 25; i++) {
        float x = times[i] - (int)times[i];
        if(x < epsi || x > 1 - epsi) {
            times[l++] = times[i];
        }
    }
    int j = 0;
    for (int i=0; i<l-1; i++) {
        if(times[i] != times[i+1]) {
            times[j++] = times[i];
        }
    }
    times[j++] = times[l-1];
    *(times + j) = 0;
    times = realloc(times, j*sizeof(float));
    return times;
}


island *find(island isl, float time, float epsi) {
    if (epsi < 0) epsi = EPSI;
    float *dists = get_distances(time, epsi);
    float *qq = dists;
    island *posibilities = calloc(500, sizeof(island));
    int l=0;
    while (*dists != 0) {
        for (int x=1; x< 100; x++) {
            for (int y=1; y<100; y++) {
                float aq = (x-isl.x) * (x-isl.x) + (y-isl.y) * (y-isl.y);
                if (aq - *dists < epsi && aq - *dists > - epsi) {
                    posibilities[l].x = x;
                    posibilities[l++].y = y;
                    // printf(" %d    %d\n", x, y);
                }
            }
        }
        dists++;
    }
    posibilities[l++].x = 0;
    posibilities[l].y = 0;
    free(qq);
    posibilities = realloc(posibilities, l * sizeof(island));
    return posibilities;
}
