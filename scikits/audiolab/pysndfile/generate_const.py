#! /usr/bin/env python
# Last Change: Thu May 24 02:00 PM 2007 J

# David Cournapeau 2006

# TODO:
#   args with the header file to extract info from

from header_parser import get_dict, put_dict_file

def generate_enum_dicts(header = '/usr/include/sndfile.h'):
    # Open the file and get the content, without trailing '\n'
    hdct    = [i.split('\n')[0] for i in open(header, 'r').readlines()]

    # Get sf boolean
    sf_bool     = {}
    nameregex   = '(SF_FALSE)'
    sf          = get_dict(hdct, nameregex)
    sf_bool['SF_FALSE'] = sf['SF_FALSE']
    nameregex   = '(SF_TRUE)'
    sf           = get_dict(hdct, nameregex)
    sf_bool['SF_TRUE'] = sf['SF_TRUE']

    # Get mode constants
    nameregex   = '(SFM_[\S]*)'
    sfm         = get_dict(hdct, nameregex)

    # Get format constants
    nameregex   = '(SF_FORMAT_[\S]*)'
    sf_format   = get_dict(hdct, nameregex)

    # Get endianness 
    nameregex   = '(SF_ENDIAN_[\S]*)'
    sf_endian   = get_dict(hdct, nameregex)

    # Get command constants
    nameregex   = '(SFC_[\S]*)'
    sf_command  = get_dict(hdct, nameregex)

    # Get (public) errors
    nameregex   = '(SF_ERR_[\S]*)'
    sf_errors   = get_dict(hdct, nameregex)

    # Replace dict:
    repdict = {
        '%SFM%' : put_dict_file(sfm, 'SFM'),
        '%SF_BOOL%' : put_dict_file(sf_bool, 'SF_BOOL'),
        '%SF_FORMAT%' : put_dict_file(sf_format, 'SF_FORMAT'),
        '%SF_ENDIAN%' : put_dict_file(sf_endian, 'SF_ENDIAN'),
        '%SF_COMMAND%' : put_dict_file(sf_command, 'SF_COMMAND'),
        '%SF_ERR%' : put_dict_file(sf_errors, 'SF_ERRORS')
    }

    return repdict
