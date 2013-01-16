CC	= colorgcc
LD	= gcc

CFLAGS	= -Wall -W

winfdopen: winfdopen.o
	$(LD) $< -o $@ -lsndfile

winfdopen.o: winfdopen.c
	$(CC) $(CFLAGS) -c $< -o $@

badflac: badflac.o
	$(LD) $< -o $@ -lsndfile

badflac.o: badflac.c
	$(CC) $(CFLAGS) -c $< -o $@

test_badflac: badflac badflac.flac
	./badflac badflac.flac

clean:
	rm -f *.o
	rm -f badflac
