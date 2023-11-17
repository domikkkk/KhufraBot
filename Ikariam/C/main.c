#include <stdio.h>
#include "Islands.h"
#include <malloc.h>
#include <stdlib.h>


int main(int argc, char *argv[]) {
    island src;
    src.x = atoi(argv[1]);
    src.y = atoi(argv[2]);
    float time = calc_time(atoi(argv[3]), atoi(argv[4]), atoi(argv[5]));
    island *is = find(src, time);
    for (int i=0;i<200;i++){
        printf("%d %d\n", is[i].x, is[i].y);
    }
    free(is);
    return 0;
}
