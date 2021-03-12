from os import name
from pydub import AudioSegment
from pydub.playback import play
import random
import os
from tqdm import tqdm

def get_parts_from_audio(audio, ms_per_tic, parts_count, offset=0):
    parts = []
    for part_id in range(offset, offset+parts_count):
        parts.append(
            audio[ms_per_tic*(part_id):ms_per_tic*(part_id+1)])

    return parts

def merge_random_parts(parts, length):
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


def main():
    full_audio = AudioSegment.from_mp3("kept.mp3")
    full_audio = full_audio[264:]

    bpm = 125
    quarter_ms_per_tic = (60 / bpm * 1000)

    cut = 4*4

    generate_and_play(full_audio, bpm, quarter_ms_per_tic, cut)
    # save_samples(full_audio, bpm, quarter_ms_per_tic, cut)

def generate(full_audio, bpm, quarter_ms_per_tic, cut):
    out_audio = AudioSegment.empty()

    for i in range(8):
        parts = get_parts_from_audio(full_audio, quarter_ms_per_tic, cut, cut*i)
        out_audio += merge_random_parts(parts, cut)

    return out_audio

def generate_and_play(full_audio, bpm, quarter_ms_per_tic, cut):
    out_audio = generate(full_audio, bpm, quarter_ms_per_tic, cut)
    out_audio.export("generated_kept.mp3")
    play(out_audio)


def save_samples(full_audio, bpm, quarter_ms_per_tic, cut):
    folder_name = "samples"
    os.makedirs(folder_name, exist_ok=True)
    samples = get_parts_from_audio(full_audio, quarter_ms_per_tic, cut*8, 0)

    for i in tqdm(range(len(samples))):
        samples[i].export(f"{folder_name}/kept_part_{i}.wav")



if __name__ == "__main__":
    main()