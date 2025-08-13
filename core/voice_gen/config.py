# config.py

MODEL_NAME = "unsloth/orpheus-3b-0.1-ft-unsloth-bnb-4bit"
TOKENISER_NAME = "meta-llama/Llama-3.2-3B-Instruct"
CHOSEN_VOICE = "tara"

PROMPTS = [
    "Ah yes... Can you hear it my brethren!? The sound of a bard singing songs ancient and artificial... Indeed, it has been within me, the world betwixt. Oooh, how wonderous indeed!",
    "It is her time now... For her to rise and sing, to let her tell her tales of worlds beyond and existence itself...",
    "I call upon thee, the bard of infinity! Amane Celesphonia!!!"
]

# Generation settings
GEN_PARAMS = {
    "max_new_tokens": 1200,
    "do_sample": True,
    "temperature": 0.6,
    "top_p": 0.95,
    "repetition_penalty": 1.1,
    "num_return_sequences": 1,
    "eos_token_id": 128258,
}
