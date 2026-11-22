CC ?= gcc
CFLAGS = -std=c11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-sanitize-recover=all -I../src
all: run
test_engine: test_engine.c ../src/engine.c ../src/signa_tables.c ../src/engine.h vectors_states.h
	$(CC) $(CFLAGS) -o $@ test_engine.c ../src/engine.c ../src/signa_tables.c
test_nvm: test_nvm.c ../src/nvm_log.c ../src/nvm_log.h
	$(CC) $(CFLAGS) -o $@ test_nvm.c ../src/nvm_log.c
test_ws: test_ws.c ../src/ws2816_encode.c ../src/ws2816.h
	$(CC) $(CFLAGS) -o $@ test_ws.c ../src/ws2816_encode.c
run: test_engine test_nvm test_ws
	./test_engine && ./test_nvm && ./test_ws
clean:
	rm -f test_engine test_nvm test_ws
.PHONY: all run clean
