#include <stdio.h>
#include <stdlib.h>

#include <sndfile.h>

int main(int argc, char *argv[])
{
    SF_INFO     info;
    SNDFILE*    file;
    sf_count_t  nf;

    char  buffer [2048] ;
    if (argc < 2) {
        fprintf(stderr, "usage: badflac filename \n");
        exit(EXIT_FAILURE);
    } 

    info.format = 0;
    file        = sf_open(argv[1], SFM_READ, &info);
    if (file == NULL) {
        fprintf(stderr, "%s:%s failed opening file %s\n", __FILE__, __func__, argv[1]);
        sf_command (file, SFC_GET_LOG_INFO, buffer, sizeof (buffer)) ;
        fprintf(stderr, "sndfile error is %s:\n", buffer);
        exit(EXIT_FAILURE);
    }

    fprintf(stderr, "Values of seek are on this platform: SET %d, CUR %d, END %d\n",
            SEEK_SET, SEEK_CUR, SEEK_END);

    fprintf(stderr, "trying to seek %lld frames\n", (long long)1);
    nf  = sf_seek(file, 1, SEEK_CUR);
    fprintf(stderr, "seeked through %lld frames\n", nf);

    sf_close(file);

    return 0;
}
