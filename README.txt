audiolab: a small toolbox to read, write and play audio to and from
numpy arrays.

audiolab provides two API:
    - one similar to matlab: this gives you wavread/wavwrite/auread/auwrite
      functions similar to matlab's ones.
    - a more complete API, which can be used to read, write to many audio files
      (including wav, aiff, flac, au, IRCAM, htk, etc...), with IO capabilities
      not available to matlab (seek, append data, etc...)

It is a thin wrapper around libsndfile from Erik Castro Lopo.

See the docs directory for more details

LICENSE:

audiolab itself is licensed under the LGPL license
(see COPYING.txt in main source directory)

audiolab depends on libsndfile to work; libsndfile is licensed under LGPL.

See http://www.mega-nerd.com/libsndfile/ for details.
