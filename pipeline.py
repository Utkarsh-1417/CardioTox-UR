# ==========================================================
# Shared pipeline logic — imported by app.py and all pages/
# ==========================================================

import streamlit as st
import numpy as np
import pandas as pd
import pickle, json, os

@st.cache_resource
def load_artifacts():
    import gdown

    with open('small_models.pkl', 'rb') as f:
        small_models = pickle.load(f)
    with open('preprocessing_objects.pkl', 'rb') as f:
        preproc = pickle.load(f)
    with open('train_fps_cache.pkl', 'rb') as f:
        train_fps_cache = pickle.load(f)
    with open('descriptor_list.json', 'r') as f:
        descriptor_names = json.load(f)
    with open('fusion_pipeline_info.json', 'r') as f:
        fusion_config = json.load(f)

    herg_path = 'herg_model_downloaded.pkl'
    if not os.path.exists(herg_path):
        file_id = '1PdZD162tBdsk4DKLX8lmHe5DXPbgIEf_'
        gdown.download(f'https://drive.google.com/uc?id={file_id}', herg_path, quiet=False)

    with open(herg_path, 'rb') as f:
        herg_model = pickle.load(f)

    final_models = {'herg': herg_model, 'cav': small_models['cav'], 'nav': small_models['nav']}
    return final_models, preproc, train_fps_cache, descriptor_names, fusion_config


final_models, preproc, train_fps_cache, descriptor_names, fusion_config = load_artifacts()

from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem, Descriptors

AD_THRESHOLD = fusion_config['ad_threshold']
MITIGATION_WEIGHT = fusion_config['mitigation_weight']
RISK_TIERS = fusion_config['risk_tiers']

def compute_descriptors(mol):
    return {
        'MolWt': Descriptors.MolWt(mol), 'MolLogP': Descriptors.MolLogP(mol),
        'TPSA': Descriptors.TPSA(mol), 'NumHDonors': Descriptors.NumHDonors(mol),
        'NumHAcceptors': Descriptors.NumHAcceptors(mol), 'NumRotatableBonds': Descriptors.NumRotatableBonds(mol),
        'NumAromaticRings': Descriptors.NumAromaticRings(mol), 'RingCount': Descriptors.RingCount(mol),
        'FractionCSP3': Descriptors.FractionCSP3(mol), 'NumHeteroatoms': Descriptors.NumHeteroatoms(mol),
        'NumSaturatedRings': Descriptors.NumSaturatedRings(mol), 'HeavyAtomCount': Descriptors.HeavyAtomCount(mol),
        'NumAliphaticRings': Descriptors.NumAliphaticRings(mol),
    }

def featurize_smiles(smiles, channel):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")
    fp_size = 2048 if channel == 'herg' else 1024
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=fp_size)
    fp_arr = np.array(fp)
    if channel != 'herg':
        selector = preproc['fp_selectors'][channel]
        fp_arr = fp_arr[selector.get_support()]
    desc_dict = compute_descriptors(mol)
    desc_vec = np.array([desc_dict[name] for name in descriptor_names]).reshape(1, -1)
    desc_scaled = preproc['descriptor_scalers'][channel].transform(desc_vec).flatten()
    return np.concatenate([fp_arr, desc_scaled]).reshape(1, -1)

def get_risk_tier(score):
    for threshold, label in RISK_TIERS:
        if score >= threshold:
            return label
    return RISK_TIERS[-1][1]

def max_tanimoto_to_train(smiles, channel):
    mol = Chem.MolFromSmiles(smiles)
    fp_size = 2048 if channel == 'herg' else 1024
    query_fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=fp_size)
    sims = DataStructs.BulkTanimotoSimilarity(query_fp, train_fps_cache[channel])
    return max(sims)

def predict_cardiotoxicity(smiles):
    herg_vec = featurize_smiles(smiles, 'herg')
    cav_vec  = featurize_smiles(smiles, 'cav')
    nav_vec  = featurize_smiles(smiles, 'nav')

    herg_prob = final_models['herg'].predict_proba(herg_vec)[0, 1]
    cav_prob  = final_models['cav'].predict_proba(cav_vec)[0, 1]
    nav_prob  = final_models['nav'].predict_proba(nav_vec)[0, 1]

    composite = herg_prob * (1 - MITIGATION_WEIGHT * np.mean([cav_prob, nav_prob]))
    risk_tier = get_risk_tier(composite)

    ad_sims = {ch: max_tanimoto_to_train(smiles, ch) for ch in ['herg', 'cav', 'nav']}
    in_ad = all(sim >= AD_THRESHOLD for sim in ad_sims.values())
    confidence = "Reliable (in AD)" if in_ad else "Low confidence (outside AD)"

    return {
        'herg_prob': herg_prob, 'ca_prob': cav_prob, 'na_prob': nav_prob,
        'composite_score': composite, 'risk_tier': risk_tier,
        'confidence': confidence, 'ad_similarities': ad_sims,
    }
