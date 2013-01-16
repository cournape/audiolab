#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>

#include <sndfile.h>

#ifdef _MSC_VER
#define __func__ __FUNCTION__
#else
#include <unistd.h>
#endif

int test(const char* filename, int byfd);

int main(int argc, char *argv[])
{
    int st;

    if (argc < 2) {
        fprintf(stderr, "usage: %s filename \n", argv[0]);
        exit(EXIT_FAILURE);
    } 

    st = test(argv[1], 0);
    if (st) {
        fprintf(stderr, "Error while opening directly\n");
    } else {
        fprintf(stderr, "Opening directly is fine\n");
    }

    st = test(argv[1], 1);
    if (st) {
        fprintf(stderr, "Error while opening by fd\n");
    } else {
        fprintf(stderr, "Opening by fd is fine\n");
    }

    return 0;
}

/* If byfd is true, try to open the file with sf_open_fd */
int test(const char* filename, int byfd)
{
    SF_INFO     info;
    SNDFILE*    file;
    int         fid, flags, st;
    char        buffer [2048];

    st  = 0;

    flags = O_RDONLY;
#if (defined (WIN32) || defined (_WIN32))
    flags |= O_BINARY;
#endif

    info.format = 0;
    if (byfd) {
        fid = open(filename, flags);
        if (fid < 0) {
            fprintf(stderr, "%s:%s failed opening file %s\n", __FILE__, __func__, filename);
            return -1;
        }

        file = sf_open_fd(fid, SFM_READ, &info, SF_TRUE);
    } else {
        file = sf_open(filename, SFM_READ, &info);
    }

    if (file == NULL) {
        fprintf(stderr, "%s:%s failed opening file %s\n", __FILE__, __func__, filename);
        sf_command (file, SFC_GET_LOG_INFO, buffer, sizeof (buffer)) ;
        fprintf(stderr, "sndfile error is %s:\n", buffer);
        close(fid);
        exit(EXIT_FAILURE);
    } else {
        fprintf(stderr, "%s:%s file %s has %d frames \n", __FILE__, __func__, filename, info.frames);
    }

    sf_close(file);

    return st;
}
