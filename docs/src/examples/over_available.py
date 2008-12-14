from scikits.audiolab import available_file_formats, available_encodings

for format in available_file_formats():
    print "File format %s is supported; available encodings are:" % format
    for enc in available_encodings(format):
        print "\t%s" % enc
    print ""
