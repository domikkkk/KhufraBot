#include <stdio.h>
#include "Islands.h"
#include <malloc.h>


int main() {
    island src;
    src.x = 81;
    src.y = 9;
    float time = calc_time(27, 0, 37);
    island *is = find(src, time);
    for (int i=0;i<200;i++){
        printf("%d %d\n", is[i].x, is[i].y);
    }
    free(is);
}
