import numpy as np
from scikits.audiolab import play

# output one second of stereo gaussian white noise at 48000 hz
play(0.05 * np.random.randn(2, 48000))
