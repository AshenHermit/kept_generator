from typing import Dict
from pydub import AudioSegment
import os
import time
import threading
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

from audio_shuffler import AudioShuffler

class SongProfile():
    def __init__(self, id="song", name="song", filepath="song.mp3", bpm=120, offset_ms=0, max_steps=4*8) -> None:
        self.id = id
        self.name = name
        self.filepath = filepath
        self.bpm = bpm
        self.offset_ms = offset_ms
        self.max_steps = max_steps

    def fit_dictionary(self, dict:dict):
        self.name = dict.get("name", self.name)
        self.filepath = dict.get("filepath", self.filepath)
        self.bpm = dict.get("bpm", self.bpm)
        self.offset_ms = dict.get("offset_ms", self.offset_ms)
        self.max_steps = dict.get("max_steps", self.max_steps)
        return self

class SongBank():
    def __init__(self) -> None:
        self.song_profiles = {}

    def get_song_by_id(self, song_id) -> SongProfile:
        return self.song_profiles[song_id]

    def has_song_with_id(self, song_id):
        return song_id in self.song_profiles

    def load_from_dict(self, song_profiles_dict):
        for song_id in song_profiles_dict:
            song_dict = song_profiles_dict[song_id]
            
            if not song_dict.get("disabled", False):
                self.song_profiles[song_id] = SongProfile(song_id).fit_dictionary(song_dict)

    @staticmethod
    def create_from_dict(song_profiles_dict):
        bank = SongBank()
        bank.load_from_dict(song_profiles_dict)
        return bank

    def get_random_song_id(self, execlude_ids):
        while True:
            song_id = list(self.song_profiles.keys())[random.randint(0, len(self.song_profiles.keys())-1)]
            if not (song_id in execlude_ids): return song_id


class ChunksProfile():
    def __init__(self, audio_format, file_name, folder_path) -> None:
        self.audio_format = audio_format
        self.file_name = file_name
        self.folder_path = folder_path
        Path(self.folder_path).mkdir(exist_ok=True)

    def get_chunk_filepath(self, chunk_index):
        return f"{self.folder_path}/{self.file_name}_{chunk_index}.{self.audio_format}"

#
class ShufflingBroadcaster():
    def __init__(self, streaming_url, song_bank=None):
        self.streaming_url = streaming_url
        if song_bank is None: song_bank = SongBank()
        self.song_bank = song_bank

        self.shuffler = None

        self.started = False
        self.previous_songs_ids = []
        self.current_chunk_index = 1
        self.chunks_profile = ChunksProfile("mp3", "chunk", "chunks")

        self.current_song_id = ""
        self.next_song_id = ""
        self.remaining_chunks_count = 0

        self.viewport_size = (640, 360)
        self.info_image = Image.new("RGB", self.viewport_size, (0,0,0))
        self.info_image_filepath = "info_overlay.png"
        self.info_font_filepath = "info_font.ttf"
        self.info_font = ImageFont.truetype(self.info_font_filepath, 20)

    @property
    def current_song(self):
        if self.current_song_id=="": return None
        return self.song_bank.get_song_by_id(self.current_song_id)
    
    def remember_song(self, song_id):
        if self.current_song is None: return
        self.previous_songs_ids += [song_id]
        self.previous_songs_ids = self.previous_songs_ids[-2:]

    def play_song_by_id(self, song_id):
        if not self.song_bank.has_song_with_id(song_id): return False

        self.current_song_id = song_id

        self.remember_song(self.current_song.id)
        self.next_song_id = self.song_bank.get_random_song_id(self.previous_songs_ids)

        full_audio = AudioSegment.from_mp3(self.current_song.filepath)
        full_audio = full_audio[self.current_song.offset_ms:]
        self.shuffler = AudioShuffler(full_audio, self.current_song.bpm, self.current_song.max_steps)
        self.remaining_chunks_count = self.current_song.max_steps

        self.update_info_image()

    def update_info_image(self):
        draw = ImageDraw.Draw(self.info_image)
        draw.rectangle(((0,0), self.viewport_size), fill=(0,0,0))
        
        draw.text((32,32), f'Now playing: "{self.current_song.name}"', (180,180,180), self.info_font)
        if self.next_song_id!="":
            draw.text(
                (32,self.viewport_size[1]-32-self.info_font.size), 
                f'Next: "{self.song_bank.get_song_by_id(self.next_song_id).name}"', 
                (120,120,120), self.info_font)

        self.info_image.save(self.info_image_filepath)

    def play_random_song(self):
        self.current_song_id = self.song_bank.get_random_song_id(self.previous_songs_ids)
        self.play_song_by_id(self.current_song_id)

    def on_song_ended(self):
        if self.next_song_id!="": self.play_song_by_id(self.next_song_id)
        else: self.play_random_song()

    def check_if_song_is_ended(self):
        if self.remaining_chunks_count <= 0:
            self.on_song_ended()
            return True
        return False

    def consume_chunk_and_check_song_end(self):
        self.remaining_chunks_count -= 1
        return self.check_if_song_is_ended()
            
    def run(self):
        #TODO: needs refactor
        while True:
            self.threaded_generate_chunk(self.current_chunk_index)
            
            time.sleep(self.wait_time)
            self.started = True
            
            self.threaded_stream_chunk(self.current_chunk_index)
            self.current_chunk_index += 1
            self.consume_chunk_and_check_song_end()
            self.threaded_generate_chunk(self.current_chunk_index)
            
            time.sleep(self.wait_time)
            self.threaded_stream_chunk(self.current_chunk_index)
            self.current_chunk_index -= 1
            self.consume_chunk_and_check_song_end()

            if self.current_chunk_index >= 20: break

    def threaded_generate_chunk(self, chunk_index):
        if self.shuffler is None: return

        filepath = self.chunks_profile.get_chunk_filepath(chunk_index)
        threading.Thread(target=self.generation_thread, 
            args=(self.shuffler, filepath)).start()

    def threaded_stream_chunk(self, chunk_index):
        if self.shuffler is None: return

        filepath = self.chunks_profile.get_chunk_filepath(chunk_index)
        threading.Thread(target=self.streaming_thread, 
            args=(filepath, self.streaming_url, self.info_image_filepath)).start()

    @property
    def wait_time(self):
        if self.started: return (self.shuffler.quarter_ms_per_tic * self.shuffler.cut)/1000
        else: return 1.0

    @staticmethod
    def stream_part(filepath, streaming_url, info_image_filepath):
        single_image = False
        if single_image:
            os.system(f"ffmpeg -loop 1 -i video_image.jpg -i {filepath} -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest -f mpegts - | ffmpeg -i pipe: -f flv {streaming_url}")
        else:
            os.system(f'ffmpeg -i loop_video.mp4 -i {info_image_filepath} -filter_complex "[0:v][1:v]blend=all_mode=lighten[v]" -map "[v]" -map 0:a -f flv - | ffmpeg -stream_loop -1 -i pipe: -i {filepath} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest -f flv {streaming_url}')

    @staticmethod
    def generation_thread(shuffler:AudioShuffler, filename):
        audio = shuffler.generate_next()
        #TODO: temporary solution. when streaming, there is a pause arises between chunks, and I can't get rid of it.
        audio = audio[:-20]
        audio.export(filename)

    @staticmethod
    def streaming_thread(filename, streaming_url, info_image_filepath):
        ShufflingBroadcaster.stream_part(filename, streaming_url, info_image_filepath)