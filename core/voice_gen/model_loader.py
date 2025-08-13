# model_loader.py

import torch
from snac import SNAC
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import snapshot_download
import config

def load_snac_model(device="cpu"):
    snac_model = SNAC.from_pretrained("hubertsiuzdak/snac_24khz")
    return snac_model.to(device)

def load_text_model(model_name, device="cpu"):
    # Download only config and safetensors
    snapshot_download(
        repo_id=model_name,
        allow_patterns=["config.json", "*.safetensors", "model.safetensors.index.json"],
        ignore_patterns=["*.pt", "*.bin", "tokenizer.*", "vocab.json", "merges.txt"]
    )

    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model.to(device), tokenizer
