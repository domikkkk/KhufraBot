// #include "qsort.h"
#include "qsort.h"
#include <stdio.h>


int main() {
    float array[] = {9.5, 3.2, 7.8, 5.1, 1.6};
    for (int i = 0; i < 5; i++) {
        printf("%lf ", array[i]);
    }
    printf("\n");
    qqsort(array, 0, 4);
    for (int i = 0; i < 5; i++) {
        printf("%lf ", array[i]);
    }
    printf("\n");
}
