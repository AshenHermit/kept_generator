from pydub import AudioSegment
import os
import time
import threading
from pathlib import Path

from audio_shuffler import AudioShuffler

class ShufflingBroadcaster():
    #TODO: not in use
    class SongProfile():
        def __init__(self, id, filepath, bpm, offset_ms) -> None:
            self.id = id
            self.filepath = filepath
            self.bpm = bpm
            self.offset_ms = offset_ms

    class ChunksProfile():
        def __init__(self, audio_format, file_name, folder_path) -> None:
            self.audio_format = audio_format
            self.file_name = file_name
            self.folder_path = folder_path
            Path(self.folder_path).mkdir(exist_ok=True)

        def get_chunk_filepath(self, chunk_index):
            return f"{self.folder_path}/{self.file_name}_{chunk_index}.{self.audio_format}"
            

    def __init__(self, streaming_url):
        self.streaming_url = streaming_url

        self.shuffler = None
        self.song_profiles = {}
        self.current_song_id = ""
        self.started = False

        self.current_chunk_index = 1
        self.chunks_profile = self.ChunksProfile("mp3", "chunk", "chunks")

    def load_song_profiles(self, song_profiles):
        self.song_profiles = song_profiles

    def play_song_by_id(self, song_id):
        if not song_id in self.song_profiles: return False

        self.current_song_id = song_id
        song_profile = self.song_profiles[self.current_song_id]

        full_audio = AudioSegment.from_mp3(song_profile["filepath"])
        full_audio = full_audio[song_profile["offset_ms"]:]
        self.shuffler = AudioShuffler(full_audio, song_profile["bpm"], song_profile["max_steps"])

    def run(self):
        while True:
            self.threaded_generate_chunk(self.current_chunk_index)
            
            time.sleep(self.wait_time)
            self.started = True
            
            self.threaded_stream_chunk(self.current_chunk_index)
            self.current_chunk_index += 1
            self.threaded_generate_chunk(self.current_chunk_index)
            
            time.sleep(self.wait_time)
            self.threaded_stream_chunk(self.current_chunk_index)
            self.current_chunk_index -= 1

            if self.current_chunk_index >= 20: break

    def threaded_generate_chunk(self, chunk_index):
        if self.shuffler is None: return

        filepath = self.chunks_profile.get_chunk_filepath(chunk_index)
        threading.Thread(target=ShufflingBroadcaster.generation_thread, 
            args=(self.shuffler, filepath)).start()

    def threaded_stream_chunk(self, chunk_index):
        if self.shuffler is None: return

        filepath = self.chunks_profile.get_chunk_filepath(chunk_index)
        threading.Thread(target=ShufflingBroadcaster.streaming_thread, 
            args=(filepath, self.streaming_url)).start()

    @property
    def wait_time(self):
        if self.started: return (self.shuffler.quarter_ms_per_tic * self.shuffler.cut)/1000
        else: return 1.0

    @staticmethod
    def stream_part(filepath, streaming_url):
        single_image = False
        if single_image:
            os.system(f"ffmpeg -loop 1 -i video_image.jpg -i {filepath} -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest -f mpegts - | ffmpeg -i pipe: -f flv {streaming_url}")
        else:
            os.system(f"ffmpeg -i loop_video.mp4 -i {filepath} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest -f mpegts - | ffmpeg -i pipe: -f flv {streaming_url}")

    @staticmethod
    def generation_thread(shuffler:AudioShuffler, filename):
        audio = shuffler.generate_next()
        #TODO: temporary solution. when streaming, there is a pause arises between chunks, and I can't get rid of it.
        audio = audio[:-20]
        audio.export(filename)

    @staticmethod
    def streaming_thread(filename, streaming_url):
        ShufflingBroadcaster.stream_part(filename, streaming_url)