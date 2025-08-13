# ---- source_separator.py ----

import json
import os

from mdx import run_mdx
from utils import display_progress, mdxnet_models_dir

# ---- source_separator.py (Updated function) ----

def separate_sources(audio_path, project_dir, is_webui, progress=None):
    """
    Separates an audio file into background, main voice, and secondary voice.
    Returns the paths to these separated tracks.
    """
    with open(os.path.join(mdxnet_models_dir, 'model_data.json')) as infile:
        mdx_model_params = json.load(infile)

    # Note: The suffixes like 'Instrumental', 'Vocals', 'Backup' are defined by the MDX models.
    # We keep them here but assign their output paths to our new generic variables.

    display_progress('[~] Separating primary voice from background...', 0.1, is_webui, progress)
    primary_voice_path, background_audio_path = run_mdx(mdx_model_params, project_dir, os.path.join(mdxnet_models_dir, 'UVR-MDX-NET-Voc_FT.onnx'), audio_path, denoise=True)

    display_progress('[~] Separating main voice from secondary voice...', 0.2, is_webui, progress)
    secondary_voice_path, main_voice_path = run_mdx(mdx_model_params, project_dir, os.path.join(mdxnet_models_dir, 'UVR_MDXNET_KARA_2.onnx'), primary_voice_path, suffix='Backup', invert_suffix='Main', denoise=True)

    display_progress('[~] Applying DeReverb to main voice...', 0.3, is_webui, progress)
    _, clean_main_voice_path = run_mdx(mdx_model_params, project_dir, os.path.join(mdxnet_models_dir, 'Reverb_HQ_By_FoxJoy.onnx'), main_voice_path, invert_suffix='DeReverb', exclude_main=True, denoise=True)

    # Return paths to the essential final components using our neutral names
    return background_audio_path, clean_main_voice_path, secondary_voice_path
