#define DIST 20.0
#define EPSI 0.02
#define N 25

typedef struct {
    int x;
    int y;
} island;

float distance(island a, island b);
float calc_time(int h, int min, float sec);
int compare_t(const void *a, const void *b);
float *get_distances();


island *find(island isl, float time);
