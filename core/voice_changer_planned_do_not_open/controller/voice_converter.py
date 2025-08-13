# ---- voice_converter.py ----

import gc
import os

from rvc import Config, load_hubert, get_vc, rvc_infer
from utils import get_rvc_model, rvc_models_dir, display_progress

def convert_voice(voice_model, vocals_path, output_path, pitch_change, f0_method,
                  index_rate, filter_radius, rms_mix_rate, protect, crepe_hop_length, is_webui, progress=None):
    """
    Converts the voice of a vocal track using RVC.
    """
    display_progress('[~] Converting voice using RVC...', 0.5, is_webui, progress)

    rvc_model_path, rvc_index_path = get_rvc_model(voice_model, is_webui)
    device = 'cuda:0'
    config = Config(device, True)
    hubert_model = load_hubert(device, config.is_half, os.path.join(rvc_models_dir, 'hubert_base.pt'))
    cpt, version, net_g, tgt_sr, vc = get_vc(device, config.is_half, config, rvc_model_path)

    rvc_infer(rvc_index_path, index_rate, vocals_path, output_path, pitch_change, f0_method, cpt, version, net_g, filter_radius, tgt_sr, rms_mix_rate, protect, crepe_hop_length, vc, hubert_model)

    del hubert_model, cpt
    gc.collect()
