import numpy as np
from _alsa_backend import asoundlib_version, card_indexes, card_name, AlsaDevice

print asoundlib_version()
print card_indexes()

a = AlsaDevice()
x = np.random.randn(48000 * 6, 2)
a.play(0.01*x)
