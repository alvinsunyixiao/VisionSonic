#!/usr/bin/env python2
import os
import sys
import wave
import numpy as np
from openal.audio import SoundData
from openal.loaders import load_wav_file
from openal.audio import SoundSink, SoundSource, SoundListener
import threading
import time
import math
import config
from IPython import embed

#do nothing for now. Should be implemented if sound is distant or distorted
def normalize(a_vector):
    ret = np.array([a_vector[0], a_vector[1], a_vector[2]])
    scalar_ = np.sqrt(np.sum(ret ** 2))
    return ret / scalar_ * 5

class sound_source(threading.Thread):
    def __init__(self, sink_obj, source_obj):
        threading.Thread.__init__(self)
        self.secret_sink = sink_obj
        self.this_source = source_obj

    def run(self):
        self.secret_sink.update()
        self.secret_sink.play(self.this_source)

    def stop(self):
        self.secret_sink.pause(self.this_source)

class stereosound:
    def __init__(self):
        self.sink = SoundSink()
        self.sink.activate()
        self.listener = SoundListener()
        self.listener.orientation = (0,0,1,0,0,1)
        self.sources = [SoundSource(position = [i, 0, 0], pitch = 1) for i in range(-1, 2, 2)]
        self.intense_sources = [SoundSource(position = [i, 0, 0], pitch = 1) for i in range(-1, 2, 2)]
        #pitch: 5,4,3,2,1
        self.data = load_wav_file("./beep.wav")
        self.intense_data = load_wav_file("./high_beep.wav")
        '''
        for source in self.sources:
            #we want the sources to be looping
            source.looping = True
            source.queue(self.data)
        '''
        for source in self.intense_sources:
            source.looping = True
            source.queue(self.intense_data)
        self.threading_pool = []
        for mild_source in self.sources:
            t = sound_source(self.sink, mild_source)
            self.threading_pool.append(t)
        for intense_source in self.intense_sources:
            t = sound_source(self.sink, intense_source)
            self.threading_pool.append(t)
        #threading pool: mild left; mild right; i left; i right
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

    def alert(self, ear = "left", intensity = "mild", command = "start"):
        if ear == "left":
            first_mul = 0
        else:
            first_mul = 1
        if intensity == "mild":
            second_mul = 0
        else:
            second_mul = 2
        if command == "start":
            self.threading_pool[first_mul + second_mul].start()
        elif command == "stop":
            self.threading_pool[first_mul + second_mul].stop()

    def _play(self, coord_tuple, avg_dis, val = "low"):
        if(not (np.array(coord_tuple).any())): return
        source_ind = self.determine_cutoff(avg_dis)
        print "calling sources" + str(source_ind)
        use_source = self.sources[source_ind]
        #embed()
        if val == "low":
            use_source.queue(self.data)
        if val == "high":
            use_source.queue(self.intense_data)
        coord_tuple = normalize(coord_tuple)
        use_source.position = [coord_tuple[0], coord_tuple[1], coord_tuple[2]]
        #time.sleep(0.02)
        self.sink.update()
        self.sink.play(use_source)
