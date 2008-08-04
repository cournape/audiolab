from _alsa import card_name, card_indexes, asoundlib_version
from _alsa import Device

if __name__ == '__main__':
    print "Asoundlib version is", asoundlib_version()
    for i in card_indexes():
        print card_name(i)

    dev = Device()
    print "Device name:", dev.name
