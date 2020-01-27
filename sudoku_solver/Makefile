CC = g++
CFLAGS = -c -g -Wall
LFLAGS = -g -o
LDFLAGS = -lncurses

main:	main.o solver.o sdk_board.o
	$(CC) $(LFLAGS) main main.o solver.o sdk_board.o $(LDFLAGS)

main.o: main.cpp solver.h cell.h variable.h sdk_board.h
	$(CC) $(CFLAGS) main.cpp

solver.o: solver.cpp solver.h cell.h variable.h sdk_board.h
	$(CC) $(CFLAGS) solver.cpp

sdk_board.o: sdk_board.cpp sdk_board.h variable.h cell.h
	$(CC) $(CFLAGS) sdk_board.cpp

.PHONY: clean
clean:
	rm -f *.o main a.out
