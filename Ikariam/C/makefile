CC = exec cc

start:
	$(CC) -shared -o ika.so Islands.c queue.c -lm -fPIC


test:
	$(CC) -o main Islands.c main.c -lm
