from _alsa import card_name, card_indexes

if __name__ == '__main__':
    for i in card_indexes():
        print card_name(i)
