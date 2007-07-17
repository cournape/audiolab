#! /usr/bin/env python
# Last Change: Tue May 22 10:00 AM 2007 J

# Copyright (C) 2006-2007 Cournapeau David <cournape@gmail.com>
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option) any
# later version.
# 
# This library is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
# 
# You should have received a copy of the GNU Lesser General Public License along
# with this library; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

# TODO:
#   - find out why finally does not work with KeyboardInterrupt instances

from tempfile import mkstemp
from os import remove, popen

from pysndfile import sndfile, formatinfo as format

def play(input, sr = 22050):
    """play(input, sr = 22050): "play" a numpy array input
    to the audio device using aplay command, @ sampling rate
    sr. 
    
    Warning: This is really crude, as it copies the numpy array
    into an audio file before writing: I am too lazy to write
    interfaces to also, windows and co..."""
    # Check inputs are OK
    if input.ndim   == 1:
        nc      = 1
        nframes = input.size
    else:
        (nframes, nc)   = input.shape

    # Create tmp file
    fd, filename    = mkstemp('py_player')

    # Copy the data into it
    b       = sndfile(filename, 'write', format('wav', 'pcm16'), nc, sr)
    b.write_frames(input, nframes)
    b.close()

    # Play using an audio command
    try:
        cmd = "aplay %s" % filename
        popen(cmd)
        remove(filename)
    except KeyboardInterrupt, inst:
        remove(filename)
        raise inst

if __name__ == '__main__':
    # Read the content of a file into numpy array, and play the numpy
    # array using the play command
    import numpy as N
    sr      = 22050
    # Play a really small noise to avoid screaming in loudspeakers
    # or headphones.
    noise   = 0.0001 * N.random.randn((sr))
    play(noise, sr)
