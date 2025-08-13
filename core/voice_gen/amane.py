# main.py

import torch
import config
from model_loader import load_snac_model, load_text_model
from audio_utils import prepare_prompts, parse_and_decode
from inference import generate_text

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load models
    snac_model = load_snac_model(device)
    model, tokenizer = load_text_model(config.MODEL_NAME, device)

    # Prepare prompts
    input_ids, attention_mask = prepare_prompts(
        tokenizer, config.PROMPTS, config.CHOSEN_VOICE
    )
    input_ids, attention_mask = input_ids.to(device), attention_mask.to(device)

    # Generate text
    generated_ids = generate_text(model, input_ids, attention_mask)

    # Decode audio
    audio_samples = parse_and_decode(generated_ids, snac_model, device)

    print("Generated audio samples:", len(audio_samples))

if __name__ == "__main__":
    main()
