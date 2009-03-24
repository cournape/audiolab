Future
======

Known bugs
----------

 - there seems to be a problem when using libsndfile fseek facilities with flac
   files (which are necessary for the functions flacread/flacwrite). The
   problem seems to be with libFLAC; for this reason, seek in flac files is not
   enabled by default for now. See FLAC_SUPPORT.txt for more information.

TODO
----

Before a 1.0 release, I would like to implement the followings:

 - support (at least some) meta-data embedded in some audio files format.
 - support the libsndfile's error system.
 - player on all major platforms (windows is the only one missing).
