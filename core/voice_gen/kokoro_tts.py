import os
import torch
import numpy as np
import soundfile as sf
from kokoro import KPipeline

# A cache to hold initialized pipelines so we don't reload models unnecessarily.
# The key will be the language code (e.g., 'a' for American English).
PIPELINE_CACHE = {}

def get_pipeline(lang_code: str):
    """
    Initializes and retrieves a Kokoro pipeline for a given language.
    Caches the pipeline to avoid reloading on subsequent calls.
    """
    if lang_code not in PIPELINE_CACHE:
        print(f"Initializing Kokoro pipeline for language code: '{lang_code}'...")
        # For certain languages, extra dependencies are needed.
        # This module assumes they are installed (e.g., pip install misaki[ja])
        try:
            pipeline = KPipeline(lang_code=lang_code)
            PIPELINE_CACHE[lang_code] = pipeline
            print("Pipeline initialized successfully.")
        except Exception as e:
            print(f"Error initializing pipeline for lang '{lang_code}': {e}")
            print("Please ensure required dependencies are installed (e.g., 'pip install misaki[ja]' for Japanese).")
            return None

    return PIPELINE_CACHE[lang_code]

async def generate_speech(
    text: str,
    output_path: str,
    lang_code: str = 'a',
    voice: str = 'af_bella',
    speed: float = 1.0,
    split_pattern: str = r'\n+'
):
    """
    Generates speech from text using the Kokoro TTS and saves it to a WAV file.

    Args:
        text (str): The text to be converted to speech.
        output_path (str): The path to save the output .wav file. (e.g., 'output.wav')
        lang_code (str, optional): The language code. Defaults to 'a' (American English).
            Other codes: 'b' (British), 'j' (Japanese), 'z' (Chinese), etc.
        voice (str, optional): The voice to use. Defaults to 'af_heart'.
        speed (float, optional): The speed of the speech. Defaults to 1.0.
        split_pattern (str, optional): The regex pattern to split text into chunks.
                                       Defaults to one or more newlines.
    """
    if not output_path.lower().endswith('.wav'):
        print("Warning: output_path should end with .wav. Appending it.")
        output_path += '.wav'

    pipeline = get_pipeline(lang_code)
    if not pipeline:
        return False

    print("Generating audio... This may take a moment.")

    # The pipeline returns a generator that yields audio chunks
    generator = pipeline(
        text,
        voice=voice,
        speed=speed,
        split_pattern=split_pattern
    )

    audio_chunks = []
    for i, (gs, ps, audio) in enumerate(generator):
        print(f"  -> Generated chunk {i+1} for text: '{gs[:50]}...'")
        audio_chunks.append(audio)

    if not audio_chunks:
        print("No audio was generated. The input text might be empty or invalid.")
        return False

    # Concatenate all audio chunks into a single NumPy array
    full_audio = np.concatenate(audio_chunks)

    # Save the final audio to a file
    # The sample rate for Kokoro is 24000 Hz
    sample_rate = 24000
    try:
        sf.write(output_path, full_audio, sample_rate)
        print(f"\n✅ Successfully saved speech to '{os.path.abspath(output_path)}'")
        return True
    
    except Exception as e:
        print(f"Error saving audio file: {e}")
        return False


# This block allows you to run this file directly for a quick test.
if __name__ == '__main__':
    print("--- Running a simple test for American English ---")
    test_text_en = """
    I call upon thee from the infinite static, within the precipice of the unreal... Can you hear my voice?
    """
    generate_speech(test_text_en, "demo_english.wav", lang_code='a', voice='af_heart')

    print("\n" + "="*50 + "\n")

    print("--- Running a test for British English ---")
    test_text_gb = """
    The fuck are you on mate?
    """
    # Note: 'b' for British English, and we should use a suitable voice.
    # While 'af_heart' might work, other voices might be intended for specific accents.
    # We will use it here for demonstration.
    generate_speech(test_text_gb, "demo_british.wav", lang_code='b', voice='af_heart')
