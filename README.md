# kept generator
Shuffling music tacts and broadcasting chunks with rtmp.  
This is an experiment with ffmpeg and pydub.  
The broadcast is implemented extremely shitty, because i dont know how to actually do such endless generated streaming, so somehow i came up with something myself.  

## Requires
* [ffmpeg](https://ffmpeg.org/)

## start.bat commands
* Sets streaming target url.
    ```
    set STREAMING_URL=rtmp://awasome-streaming-server.com/adwadawd-key-or-something-awdoiawndownadpo
    ```
* Sets some broadcast options. Used in method `broadcast_part` in [shuffling_broadcaster.py](./shuffling_broadcaster.py).
    ```
    set BROADCAST_OPTIONS=-thread_queue_size 1024
    ```
* Runs program. Guess i should transfer env variables to the program arguments.
    ```
    python main.py
    ```

## Record
[![RECORD](https://drive.google.com/thumbnail?id=1GMzFnv8WbaUQHOEXQnkYUjDGsDZyRr3C)](https://drive.google.com/file/d/1GMzFnv8WbaUQHOEXQnkYUjDGsDZyRr3C/preview)

## Youtube radio
(banned, unfortunately)  
[![Youtube radio](https://img.youtube.com/vi/lS9pbiYg770/0.jpg)](https://www.youtube.com/watch?v=lS9pbiYg770)
