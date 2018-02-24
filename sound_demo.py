#oh yeah
"""Utility functions for loading sounds."""
import os
import sys
import wave
from openal.audio import SoundData

__all__ = ["load_wav_file", "load_file"]


def load_wav_file(fname):
    """Loads a WAV encoded audio file into a SoundData object."""
    fp = wave.open(fname, "rb")
    channels = fp.getnchannels()
    bitrate = fp.getsampwidth() * 8
    samplerate = fp.getframerate()
    buf = fp.readframes(fp.getnframes())
    return SoundData(buf, channels, bitrate, len(buf), samplerate)

import time
import math
from openal.audio import SoundSink, SoundSource, SoundListener

if __name__ == "__main__":
    sink = SoundSink()
    sink.activate()
    listener = SoundListener()
    listener.orientation = (0,0,1,0,0,1)
    source = SoundSource(position=[0, 0, 3])
    source.looping = True
    data = load_wav_file("./hey.wav")
    source.queue(data)
    sink.play(source)
    t = 0
    while True:
        x_pos = 5*math.sin(math.radians(t))
        source.position = [x_pos, source.position[1], source.position[2]]
        sink.update()
        print("playing at %r" % source.position)
        time.sleep(0.1)
        t += 5
