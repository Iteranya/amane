from core.voice_gen.kokoro_tts import generate_speech

AUDIO_LOCATION = "output/"

async def convert_text_to_voice(text,filename,character="af_bella",language="a")-> bool:
    result = generate_speech(text, AUDIO_LOCATION+filename, language, character)
    return result