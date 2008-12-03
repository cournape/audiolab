import numpy as np
from _alsa_backend import alsa_version, enumerate_devices, AlsaDevice

print alsa_version()
for i in enumerate_devices():
    print i

a = AlsaDevice()
x = np.random.randn(2, 48000 * 6)
a.play(0.01*x)
