from scikits.audiolab import play, wavread

data, fs, enc = wavread('test.wav')
# There is a discrepency between wavread (one column per channel) and play
# convention (one row per channel). Audiolab will be fully converted to 'numpy
# conventions' (last axis per default) after version 0.9
play(data.T, fs)
