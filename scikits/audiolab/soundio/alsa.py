from _alsa import card_name, card_indexes, asoundlib_version

if __name__ == '__main__':
    print "Asoundlib version is", asoundlib_version()
    for i in card_indexes():
        print card_name(i)
