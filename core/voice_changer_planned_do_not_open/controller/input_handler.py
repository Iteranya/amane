# ---- input_handler.py ----

import os
from urllib.parse import urlparse

import yt_dlp

# Assuming utils.py is in the same directory
from utils import get_youtube_video_id, get_hash, raise_exception, display_progress, output_dir, convert_to_stereo

def yt_download(link):
    """Downloads audio from a YouTube link and returns the file path."""
    ydl_opts = {
        'format': 'bestaudio', 'outtmpl': '%(title)s', 'nocheckcertificate': True,
        'ignoreerrors': True, 'no_warnings': True, 'quiet': True, 'extractaudio': True,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(link, download=True)
        download_path = ydl.prepare_filename(result, outtmpl='%(title)s.mp3')
    return download_path

def prepare_input(song_input, is_webui, progress=None):
    """
    Determines input type, downloads if necessary, and returns the song ID and path.
    """
    display_progress('[~] Preparing Input Song...', 0, is_webui, progress)

    if urlparse(song_input).scheme in ['http', 'https']:
        # YouTube URL
        song_id = get_youtube_video_id(song_input)
        if song_id is None:
            raise_exception('Invalid YouTube URL.', is_webui)

        song_link = song_input.split('&')[0]
        song_path = yt_download(song_link)

    else:
        # Local File Path
        song_input = song_input.strip('\"')
        if not os.path.exists(song_input):
            raise_exception(f'File not found: {song_input}', is_webui)

        song_id = get_hash(song_input)
        song_path = song_input

    song_dir = os.path.join(output_dir, song_id)
    if not os.path.exists(song_dir):
        os.makedirs(song_dir)

    # Ensure audio is stereo for consistent processing
    song_path = convert_to_stereo(song_path)

    return song_id, song_path, song_dir
