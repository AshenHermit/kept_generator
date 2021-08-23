import os
from shuffling_broadcaster import ShufflingBroadcaster, SongBank

song_profiles_dict = {
    "crimewave":{
        "name": "Crimewave",
        "filepath": "songs/crimewave.mp3",
        "bpm": 120.575,
        "offset_ms": 0,
        "max_steps": 4*8,
    },
    "kept":{
        "name": "Kept",
        "filepath": "songs/kept.mp3",
        "bpm": 125.138,
        "offset_ms": 0,
        "max_steps": 4*8,
    },
    "year_of_silence":{
        "name": "Year of Silence",
        "filepath": "songs/year_of_silence.mp3",
        "bpm": 115.266,
        "offset_ms": 0,
        "max_steps": 4*10,
    },
    "untrust_us":{
        "name": "Untrust Us",
        "filepath": "songs/untrust_us.mp3",
        "bpm": 126.534,
        "offset_ms": 0,
        "max_steps": 4*6,
    },
    "tuesday":{
        "disabled": True,
        "name": "Tuesday",
        "filepath": "songs/tuesday.mp3",
        "bpm": 127.936,
        "offset_ms": 0,
        "max_steps": 4*5,
    }
}

def main():
    broadcaster = ShufflingBroadcaster(
        os.environ.get("STREAMING_URL"), 
        SongBank.create_from_dict(song_profiles_dict))
    
    broadcaster.play_random_song()
    # broadcaster.play_song_by_id("untrust_us")
    broadcaster.run()
    
    
if __name__ == '__main__':
    main()
    pass