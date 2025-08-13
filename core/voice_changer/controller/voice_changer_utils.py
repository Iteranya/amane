# ---- utils.py ----

import hashlib
import os
import shlex
import subprocess
from contextlib import suppress
from urllib.parse import urlparse, parse_qs

import librosa
import numpy as np
import sox
import soundfile as sf
import gradio as gr

# Define constants for file paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mdxnet_models_dir = os.path.join(BASE_DIR, 'mdxnet_models')
rvc_models_dir = os.path.join(BASE_DIR, 'rvc_models')
output_dir = os.path.join(BASE_DIR, 'song_output')


def get_youtube_video_id(url, ignore_playlist=True):
    """Parses a YouTube URL to extract the video ID."""
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        if query.path[1:] == 'watch': return query.query[2:]
        return query.path[1:]
    if query.hostname in {'www.youtube.com', 'youtube.com', 'music.youtube.com'}:
        if not ignore_playlist:
            with suppress(KeyError): return parse_qs(query.query)['list'][0]
        if query.path == '/watch': return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/watch/': return query.path.split('/')[1]
        if query.path[:7] == '/embed/': return query.path.split('/')[2]
        if query.path[:3] == '/v/': return query.path.split('/')[2]
    return None

def get_hash(filepath):
    """Creates a unique hash for a file."""
    with open(filepath, 'rb') as f:
        file_hash = hashlib.blake2b()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()[:11]

def get_rvc_model(voice_model, is_webui):
    """Finds the RVC model and index file paths."""
    rvc_model_filename, rvc_index_filename = None, None
    model_dir = os.path.join(rvc_models_dir, voice_model)
    for file in os.listdir(model_dir):
        ext = os.path.splitext(file)[1]
        if ext == '.pth': rvc_model_filename = file
        if ext == '.index': rvc_index_filename = file

    if rvc_model_filename is None:
        raise_exception(f'No model file exists in {model_dir}.', is_webui)

    rvc_model_path = os.path.join(model_dir, rvc_model_filename)
    rvc_index_path = os.path.join(model_dir, rvc_index_filename) if rvc_index_filename else ''
    return rvc_model_path, rvc_index_path

def get_separated_audio_paths(project_dir):
    """Finds the paths of separated audio files in a directory."""
    background_audio_path = None
    main_voice_dereverb_path = None
    secondary_voice_path = None

    for file in os.listdir(project_dir):
        # This is the background audio (formerly instrumentals)
        if file.endswith('_Instrumental.wav'):
            background_audio_path = os.path.join(project_dir, file)

        # This is the main voice track, cleaned and ready for conversion
        elif file.endswith('_Vocals_Main_DeReverb.wav'):
            main_voice_dereverb_path = os.path.join(project_dir, file)

        # This is the secondary voice audio (formerly backup vocals)
        elif file.endswith('_Vocals_Backup.wav'):
            secondary_voice_path = os.path.join(project_dir, file)

    return background_audio_path, main_voice_dereverb_path, secondary_voice_path

def convert_to_stereo(audio_path):
    """Converts a mono audio file to stereo."""
    wave, sr = librosa.load(audio_path, mono=False, sr=44100)
    if type(wave[0]) != np.ndarray:
        stereo_path = f'{os.path.splitext(audio_path)[0]}_stereo.wav'
        command = shlex.split(f'ffmpeg -y -loglevel error -i "{audio_path}" -ac 2 -f wav "{stereo_path}"')
        subprocess.run(command)
        return stereo_path
    return audio_path

def pitch_shift(audio_path, pitch_change):
    """Changes the pitch of an audio file using SoX."""
    output_path = f'{os.path.splitext(audio_path)[0]}_p{pitch_change}.wav'
    if not os.path.exists(output_path):
        y, sr = sf.read(audio_path)
        tfm = sox.Transformer()
        tfm.pitch(pitch_change)
        y_shifted = tfm.build_array(input_array=y, sample_rate_in=sr)
        sf.write(output_path, y_shifted, sr)
    return output_path

def display_progress(message, percent, is_webui, progress=None):
    """Displays progress updates for CLI or Gradio UI."""
    if is_webui and progress:
        progress(percent, desc=message)
    else:
        print(message)

def raise_exception(error_msg, is_webui):
    """Raises an exception for CLI or Gradio UI."""
    if is_webui:
        raise gr.Error(error_msg)
    else:
        raise Exception(error_msg)
