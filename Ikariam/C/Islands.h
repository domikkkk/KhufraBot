#define DIST 20.0
#define EPSI 0.02

typedef struct {
    int x;
    int y;
} island;

float distance(island a, island b);
float calc_time(int h, int min, float sec);
float *get_distances(float time, float epsi);


island *find(island isl, float time, float epsi);
