# audio_utils.py

import torch
import config

def prepare_prompts(tokenizer, prompts, chosen_voice):
    prompts = [f"{chosen_voice}: " + p for p in prompts]

    start_token = torch.tensor([[128259]], dtype=torch.int64)
    end_tokens = torch.tensor([[128009, 128260]], dtype=torch.int64)

    all_modified_input_ids = []
    for prompt in prompts:
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids
        modified = torch.cat([start_token, input_ids, end_tokens], dim=1)
        all_modified_input_ids.append(modified)

    max_length = max(m.shape[1] for m in all_modified_input_ids)
    all_padded, all_masks = [], []
    for ids in all_modified_input_ids:
        padding = max_length - ids.shape[1]
        padded = torch.cat([torch.full((1, padding), 128263, dtype=torch.int64), ids], dim=1)
        mask = torch.cat([torch.zeros((1, padding), dtype=torch.int64), torch.ones((1, ids.shape[1]), dtype=torch.int64)], dim=1)
        all_padded.append(padded)
        all_masks.append(mask)

    return torch.cat(all_padded, dim=0), torch.cat(all_masks, dim=0)

def parse_and_decode(generated_ids, snac_model, device="cuda"):
    token_to_find = 128257
    token_to_remove = 128258

    token_indices = (generated_ids == token_to_find).nonzero(as_tuple=True)
    if len(token_indices[1]) > 0:
        last_idx = token_indices[1][-1].item()
        cropped = generated_ids[:, last_idx+1:]
    else:
        cropped = generated_ids

    processed_rows = [row[row != token_to_remove] for row in cropped]

    code_lists = []
    for row in processed_rows:
        row_len = row.size(0)
        new_len = (row_len // 7) * 7
        trimmed = row[:new_len] - 128266
        code_lists.append(trimmed.tolist())

    def redistribute_codes(code_list):
        layer_1, layer_2, layer_3 = [], [], []
        for i in range((len(code_list) + 1) // 7):
            layer_1.append(code_list[7*i])
            layer_2.append(code_list[7*i+1] - 4096)
            layer_3.append(code_list[7*i+2] - (2*4096))
            layer_3.append(code_list[7*i+3] - (3*4096))
            layer_2.append(code_list[7*i+4] - (4*4096))
            layer_3.append(code_list[7*i+5] - (5*4096))
            layer_3.append(code_list[7*i+6] - (6*4096))

        codes = [torch.tensor(layer_1).unsqueeze(0),
                 torch.tensor(layer_2).unsqueeze(0),
                 torch.tensor(layer_3).unsqueeze(0)]
        return snac_model.decode(codes)

    samples = [redistribute_codes(codes) for codes in code_lists]
    return samples
