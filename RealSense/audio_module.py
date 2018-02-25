import pyaudio
import wave
import threading
import pyaudio_looper
import single_audio_mod
from IPython import embed

dog_audio_files = ["../Audio/dog-left.wav", "../Audio/dog-front.wav", "../Audio/dog-right.wav"]
person_audio_files = ["../Audio/person-left.wav", "../Audio/person-front.wav", "../Audio/person-right.wav"]
beep_audio_files = ["../Audio/left_low.wav", "../Audio/left_high.wav", "../Audio/right_low.wav", "../Audio/right_high.wav"]

keyword_dict = {"beep": {"left_low": 6, "left_high": 7, "right_low": 8, "right_high": 9}}

mystery_dict = {"dog": {"left": "../Audio/dog-left.wav", "front": "../Audio/dog-front.wav", "right": "../Audio/dog-right.wav"}, "person": {"left": "../Audio/person-left.wav", "front": "../Audio/person-front.wav", "right": "../Audio/person-right.wav"}}

single_dict = {"dog": {"left": True, "front": True, "right": True}, "person": {"left": True, "front": True, "right": True}}

def keyword_2_ind(obje, direction):
    return keyword_dict[obje][direction]

class audio_module:
    def __init__(self):
        self.thread_pool = []
        #struct
        #thread;
        #file_path
        for dog in dog_audio_files:
            self.thread_pool.append([pyaudio_looper.WavePlayerLoop(dog), dog])
        for person in person_audio_files:
            self.thread_pool.append([pyaudio_looper.WavePlayerLoop(person), person])
        for beep in beep_audio_files:
            self.thread_pool.append([pyaudio_looper.WavePlayerLoop(beep), beep])
        #struct of thread pool
        #dog l/f/r person l/f/r beep l/r l/h
        self.single_thread_pool = []

    def play(self, obj, dire):
        for n, pool_struct in enumerate(self.single_thread_pool):
            if pool_struct[0].is_alive():
                if pool_struct[1] == obj and pool_struct[2] == dire:
                    #is playing and obj name and direc mateched
                    return
        if obj == "dog" or obj == "person":
            t = single_audio_mod.WavePlayerSingle(mystery_dict[obj][dire])
            t.start()
            self.single_thread_pool.append([t, obj, dire])
        else:
            num = keyword_2_ind(obj, dire)
            self.thread_pool[num][0].start() #no blocking

    def stop(self, obj, dire):
        assert obj == "beep"
        num = keyword_2_ind(obj, dire)
        play_file_name = self.thread_pool[num][1]
        replacement_thread = [pyaudio_looper.WavePlayerLoop(play_file_name), play_file_name]
        self.thread_pool[num][0].stop()
        self.thread_pool[num] = replacement_thread

    def is_active(self, obj, dire):
        num = keyword_2_ind(obj, dire)
        return self.thread_pool[num][0].is_alive()
