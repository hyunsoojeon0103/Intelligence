CC = g++
CFLAGS = -c -g -Wall
LFLAGS = -g -o

main: main.o funcs.o
	$(CC) $(LFLAGS) main main.o funcs.o

main.o:	main.cpp queen.h funcs.h
	$(CC) $(CFLAGS) main.cpp

funcs.o: funcs.cpp queen.h
	$(CC) $(CFLAGS) funcs.cpp

.PHONY: clean
clean:
	rm -f *.o a.out main
