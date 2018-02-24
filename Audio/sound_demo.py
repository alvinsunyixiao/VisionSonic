#oh yeah
"""Utility functions for loading sounds."""
import os
import sys
import wave
from openal.audio import SoundData
from openal.loaders import load_wav_file
from openal.audio import SoundSink, SoundSource, SoundListener
import time
import math

if __name__ == "__main__":
    sink = SoundSink()
    sink.activate()
    listener = SoundListener()
    listener.orientation = (0,0,1,0,0,1)
    source1 = SoundSource(position=[0, 0, 3])
    source1.looping = True
    source2 = SoundSource(position=[0, 0, 3],pitch=2.0)
    source2.looping = True
    data1 = load_wav_file("./hey2.wav")
    data2 = load_wav_file("./hey.wav")
    source1.queue(data2)
    source2.queue(data2)
    sink.play(source1)
    sink.play(source2)
    t = 0
    while True:
        x_pos = 5*math.sin(math.radians(t))
        source1.position = [x_pos, source1.position[1], source1.position[2]]
        source2.position = [0, source2.position[1], source2.position[2]]
        sink.update()
        print("playing source 1 at %r" % source1.position)
        print("playing source 2 at %r" % source2.position)
        time.sleep(0.1)
        t += 5
