#!/usr/bin/env python2
import os
import sys
import wave
from openal.audio import SoundData
from openal.loaders import load_wav_file
from openal.audio import SoundSink, SoundSource, SoundListener
import time
import math

#do nothing for now. Should be implemented if sound is distant or distorted
def normalize(a_vector):
    return a_vector

class stereosound:
    def __init__(self):
        self.sink = SoundSink()
        self.sink.activate()
        self.listener = SoundListener()
        self.listener.orientation = (0,0,1,0,0,1)
        self.sources = [SoundSource(position = [0, 0, 1], pitch = 5 - i) for i in range(5)]
        #pitch: 5,4,3,2,1
        self.data = load_wav_file("./hey.wav")
        for source in self.sources:
            #we want the sources to be looping
            source.looping = True
            source.queue(data)
        #self.sink.play(source1)
        #self.sink.play(source2)
        self.cutoff = [i * (config.MAX_DISTANCE / len(self.sources)) for i in range(len(self.sources))]

    #return index for desired sound source in cutoff
    def determine_cutoff(self, avg_dis):
        for n in range(len(self.cutoff) - 1):
            lower_bound = self.cutoff[n]
            upper_bound = self.cutoff[n + 1]
            if(avg_dis >= lower_bound and avg_dis <= upper_bound):
                return n
        return len(self.cutoff) - 1

    def play(self, coord_tuple, avg_dis):
        use_source = self.sources[self.determine_cutoff(avg_dis)]
        use_source.position = [coord_tuple[0], coord_tuple[1], coord_tuple[2]]
        self.sink.update()
        self.sink.play(use_source)
