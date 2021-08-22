from pydub import AudioSegment
from pydub.playback import play
import random
import os
from tqdm import tqdm
import subprocess
import time
import threading
from pathlib import Path

from audio_shuffler import AudioShuffler



def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

def stream_part(filepath):
    streaming_url = os.environ.get('STREAMING_URL')
    # for single image
    # os.system(f"ffmpeg -loop 1 -i video_image.jpg -i {filepath} -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest -f mpegts - | ffmpeg -i pipe: -f flv {streaming_url}")
    # for video
    os.system(f"ffmpeg -i loop_video.mp4 -i {filepath} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest -f mpegts - | ffmpeg -i pipe: -f flv {streaming_url}")

def generation_thread(shuffler, filename):
    audio = shuffler.generate_next()
    audio = audio[:-40] #TODO: temporary solution. when streaming, there is a pause arises between chunks, and I can't get rid of it.
    audio.export(filename)

def streaming_thread(filename):
    stream_part(filename)

def make_dirs(path):
    Path(path).mkdir(exist_ok=True)

def main():
    full_audio = AudioSegment.from_mp3("kept.mp3")
    full_audio = full_audio[25:]
    shuffler = AudioShuffler(full_audio, 125.11)

    audio_format = "wav"

    chunks_folder_path = "chunks"
    chunk_name = "chunk"
    make_dirs(chunks_folder_path)
    chunks = 1

    started = False

    def get_wait_time():
        if started: return (shuffler.quarter_ms_per_tic * shuffler.cut)/1000
        else: return 1.0

    wait_time = get_wait_time()

    #TODO: 

    while True:
        threading.Thread(target=generation_thread, args=(shuffler, f"{chunks_folder_path}/{chunk_name}_{chunks}.{audio_format}")).start()
        
        time.sleep(wait_time)
        started = True
        wait_time = get_wait_time()
        
        threading.Thread(target=streaming_thread, args=(f"{chunks_folder_path}/{chunk_name}_{chunks}.{audio_format}",)).start()
        chunks += 1
        threading.Thread(target=generation_thread, args=(shuffler, f"{chunks_folder_path}/{chunk_name}_{chunks}.{audio_format}")).start()
        
        time.sleep(wait_time)
        threading.Thread(target=streaming_thread, args=(f"{chunks_folder_path}/{chunk_name}_{chunks}.{audio_format}",)).start()
        chunks -= 1

        if chunks >= 20: break

if __name__ == '__main__':
    main()
    pass