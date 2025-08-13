# inference.py

import torch
import config

@torch.no_grad()
def generate_text(model, input_ids, attention_mask):
    return model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        **config.GEN_PARAMS
    )
