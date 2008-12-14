Future
======

Known bugs
----------

 - the function supported_* are broken (they never worked correctly). This will
   be fixed for audiolab 0.10
 - there seems to be a problem when using libsndfile fseek facilities with flac
   files (which are necessary for the functions flacread/flacwrite). The
   problem seems to be with libFLAC; for this reason, seek in flac files is not
   enabled by default for now. See FLAC_SUPPORT.txt for more informations.

TODO
----

Before a 1.0 release, I would like to implement the follwings:

 - support (at least some) meta-data embedded in some audio files format.
 - support the libsndfile's error system.
 - player on all major plateforms (windows is missing).
