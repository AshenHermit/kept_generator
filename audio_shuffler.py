from pydub import AudioSegment
from pydub.playback import play
import random
import os
from tqdm import tqdm
import subprocess
import time
import threading
from pathlib import Path

class AudioShuffler():
    def __init__(self, full_audio, bpm, max_steps=4*8, beats_in_step=4*4):
        self.full_audio = full_audio

        self.bpm = bpm
        self.quarter_ms_per_beat = (60 / bpm * 1000)

        self.beats_in_step = beats_in_step

        self.max_steps = max_steps
        self.next_step_index = 0

    def get_parts_from_audio(self, audio, ms_per_tic, parts_count, offset=0):
        parts = []
        for part_index in range(offset, offset+parts_count):
            parts.append(
                audio[ms_per_tic*part_index:ms_per_tic*(part_index+1)])

        return parts

    def merge_random_parts(self, parts, length):
        out_audio = AudioSegment.empty()
        last_r = [0]*2

        def rand(i):
            return random.randint(0, len(parts)//2-1)*2 + i%2

        for i in range(length):
            r = rand(i)
            while last_r[0] == r or last_r[1] == r:
                r = rand(i)

            last_r[1] = last_r[0]
            last_r[0] = r

            out_audio += parts[r]

        return out_audio

    def generate(self):
        out_audio = AudioSegment.empty()

        for i in tqdm(range(4*8)):
            parts = self.get_parts_from_audio(self.full_audio, self.quarter_ms_per_beat, self.beats_in_step, self.beats_in_step*i)
            out_audio += self.merge_random_parts(parts, self.beats_in_step)

        return out_audio

    def generate_and_play(self):
        out_audio = self.generate()
        print("exporting...")
        out_audio.export("generated_kept.mp3")
        print("done")
        play(out_audio)

    def generate_next(self):        
        offset = self.beats_in_step * (self.next_step_index%self.max_steps)
        parts = self.get_parts_from_audio(self.full_audio, self.quarter_ms_per_beat, self.beats_in_step, offset)
        self.next_step_index += 1
        return self.merge_random_parts(parts, self.beats_in_step)

    def test_save_samples(self, full_audio, bpm, quarter_ms_per_tic, cut):
        folder_name = "samples"
        os.makedirs(folder_name, exist_ok=True)
        samples = self.get_parts_from_audio(full_audio, quarter_ms_per_tic, cut*8, 0)

        for i in tqdm(range(len(samples))):
            samples[i].export(f"{folder_name}/kept_part_{i}.wav")
