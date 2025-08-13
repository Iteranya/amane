# Modified and Reverse Engineered from @SociallyIneptWeeb repository
# Original Here: https://github.com/SociallyIneptWeeb/AICoverGen
# ---- main.py (Updated) ----

import os
import gradio as gr
from pydub import AudioSegment

# Import the main functions from our modules
from input_handler import prepare_input
from source_separator import separate_sources
from voice_converter import convert_voice
from audio_mixer import apply_audio_effects, combine_and_export

# Import utilities
# Note: You will need to update get_audio_paths in utils.py as well.
from utils import get_separated_audio_paths, pitch_shift, raise_exception

def audio_conversion_pipeline(
    # Core Parameters
    audio_input: str,
    voice_model: str,
    pitch_change: int,
    # Workflow Parameters
    remix_audio: bool = True,
    keep_files: bool = False,
    # RVC Parameters
    index_rate: float = 0.5,
    filter_radius: int = 3,
    rms_mix_rate: float = 0.25,
    protect: float = 0.33,
    f0_method: str = 'rmvpe',
    crepe_hop_length: int = 128,
    # Mixing Parameters
    main_gain: int = 0,
    backup_gain: int = 0,
    inst_gain: int = 0,
    pitch_change_all: int = 0,
    # Effects Parameters
    reverb_rm_size: float = 0.15,
    reverb_wet: float = 0.2,
    reverb_dry: float = 0.8,
    reverb_damping: float = 0.7,
    # Output Parameters
    output_format: str = 'mp3',
    # UI
    is_webui: bool = False,
    progress=gr.Progress()
):
    """
    A generic pipeline to convert the main voice in an audio file, with an option to remix it with background audio.
    - audio_input: Path or URL to the audio file.
    - voice_model: The RVC voice model to use.
    - pitch_change: Pitch shift for the AI voice (in semitones, not octaves anymore for clarity).
    - remix_audio: If True, combines the AI voice with the original background audio. If False, returns only the converted voice.
    """
    try:
        if not audio_input or not voice_model:
            raise_exception('Ensure that the audio input and voice model are selected.', is_webui)

        # 1. PREPARE INPUT (Handles downloads, hashing, etc.)
        project_id, original_audio_path, project_dir = prepare_input(audio_input, is_webui, progress)

        # 2. SEPARATE SOURCES (Vocals, Instrumentals, etc.)
        # Check for cached separated files first
        background_audio_path, clean_voice_path, secondary_voice_path = get_separated_audio_paths(project_dir)
        if not all([background_audio_path, clean_voice_path, secondary_voice_path]):
            background_audio_path, clean_voice_path, secondary_voice_path = separate_sources(original_audio_path, project_dir, is_webui, progress)

        # 3. CONVERT THE PRIMARY VOICE
        # The main pitch change is now combined with the "all" pitch change for the main voice
        total_pitch_change = pitch_change + pitch_change_all
        ai_voice_filename = f'{os.path.splitext(os.path.basename(original_audio_path))[0]}_{voice_model}_p{total_pitch_change}.wav'
        ai_voice_path = os.path.join(project_dir, ai_voice_filename)

        if not os.path.exists(ai_voice_path):
            convert_voice(voice_model, clean_voice_path, ai_voice_path, total_pitch_change, f0_method,
                          index_rate, filter_radius, rms_mix_rate, protect, crepe_hop_length, is_webui, progress)

        # 4. APPLY AUDIO EFFECTS to the converted voice
        ai_voice_mixed_path = apply_audio_effects(ai_voice_path, reverb_rm_size, reverb_wet, reverb_dry, reverb_damping, progress, is_webui)

        # 5. FINALIZE OUTPUT based on user's choice
        if remix_audio:
            # --- PATH A: REMIX WITH BACKGROUND AUDIO (For Song Covers) ---
            print("Remixing audio with background tracks.")

            # Apply overall pitch shift to background/secondary tracks if requested
            if pitch_change_all != 0:
                background_audio_path = pitch_shift(background_audio_path, pitch_change_all)
                secondary_voice_path = pitch_shift(secondary_voice_path, pitch_change_all)

            # Combine all tracks into the final cover
            final_output_path = os.path.join(project_dir, f'{os.path.splitext(os.path.basename(original_audio_path))[0]} ({voice_model} Cover).{output_format}')
            combine_and_export(ai_voice_mixed_path, background_audio_path, secondary_voice_path,
                               main_gain, backup_gain, inst_gain, final_output_path, output_format, progress, is_webui)
        else:
            # --- PATH B: VOICE ONLY (For Audiobooks, Voiceovers) ---
            print("Exporting AI voice only.")

            # Define the final path for the voice-only file
            final_output_path = os.path.join(project_dir, f'{os.path.splitext(os.path.basename(original_audio_path))[0]} ({voice_model} Voice Only).{output_format}')

            # Export the processed AI voice to the desired format
            audio_segment = AudioSegment.from_wav(ai_voice_mixed_path)
            audio_segment.export(final_output_path, format=output_format)

        # 6. CLEANUP
        if not keep_files:
            # Add os.remove() calls here for any files you want to delete
            pass

        print(f"[*] Final audio created: {final_output_path}")
        return final_output_path

    except Exception as e:
        raise_exception(str(e), is_webui)
