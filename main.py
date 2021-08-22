import os
from shuffling_broadcaster import ShufflingBroadcaster

song_profiles_dict = {
    "crimewave":{
        "filepath": "songs/crimewave.mp3",
        "bpm": 120.575,
        "offset_ms": 0,
        "max_steps": 4*8,
    },
    "kept":{
        "filepath": "songs/kept.mp3",
        "bpm": 125.11,
        "offset_ms": 20,
        "max_steps": 4*8,
    }
}

def main():
    broadcaster = ShufflingBroadcaster(os.environ.get("STREAMING_URL"))
    broadcaster.load_song_profiles(song_profiles_dict)
    broadcaster.play_song_by_id("crimewave")
    broadcaster.run()
    
    
if __name__ == '__main__':
    main()
    pass