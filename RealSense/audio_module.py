import pyaudio
import wave
import threading
import pyaudio_looper
from IPython import embed

dog_audio_files = ["../Audio/dog-left.wav", "../Audio/dog-front.wav", "../Audio/dog-right.wav"]
person_audio_files = ["../Audio/person-left.wav", "../Audio/person-front.wav", "../Audio/person-right.wav"]
beep_audio_files = ["../Audio/left_low.wav", "../Audio/left_high.wav", "../Audio/right_low.wav", "../Audio/right_high.wav"]

keyword_dict = {"dog": {"left": 0, "front": 1, "right": 2},
                    "person": {"left": 3, "front": 4, "right": 5},
                    "beep": {"left_low": 6, "left_high": 7, "right_low": 8, "right_high": 9}}

def keyword_2_ind(object, direction):
    return keyword_dict[object][direction]


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

    def play(self, obj, dire):
        num = keyword_2_ind(obj, dire)
        self.thread_pool[num][0].start() #no blocking

    def stop(self, obj, dire):
        num = keyword_2_ind(obj, dire)
        play_file_name = self.thread_pool[num][1]
        replacement_thread = [pyaudio_looper.WavePlayerLoop(play_file_name), play_file_name]
        self.thread_pool[num][0].stop()
        self.thread_pool[num] = replacement_thread
