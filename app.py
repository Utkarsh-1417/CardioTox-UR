# ==========================================================
# Multi-Channel Cardiotoxicity Predictor — Streamlit App
# hERG / Cav / Nav ion-channel blocker prediction + late-fusion risk score
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import pickle, json, os, io

st.set_page_config(page_title="Cardiotoxicity Predictor", layout="wide")

# ----------------------------------------------------------
# Load artifacts (cached — runs once per app session, not per prediction)
# ----------------------------------------------------------
@st.cache_resource
def load_artifacts():
    import gdown

    # Small models + config committed directly to the repo
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

    # hERG model is too large for GitHub — download from Drive on first run
    herg_path = 'herg_model_downloaded.pkl'
    if not os.path.exists(herg_path):
        file_id = '1PdZD162tBdsk4DKLX8lmHe5DXPbgIEf_'
        gdown.download(f'https://drive.google.com/uc?id={file_id}', herg_path, quiet=False)

    with open(herg_path, 'rb') as f:
        herg_model = pickle.load(f)

    final_models = {'herg': herg_model, 'cav': small_models['cav'], 'nav': small_models['nav']}

    return final_models, preproc, train_fps_cache, descriptor_names, fusion_config


with st.spinner("Loading models (first run may take ~1-2 min to download hERG model)..."):
    final_models, preproc, train_fps_cache, descriptor_names, fusion_config = load_artifacts()

from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem, Descriptors, Draw

AD_THRESHOLD = fusion_config['ad_threshold']
MITIGATION_WEIGHT = fusion_config['mitigation_weight']
RISK_TIERS = fusion_config['risk_tiers']

# ----------------------------------------------------------
# Pipeline functions (identical logic to the notebook's rebuilt pipeline)
# ----------------------------------------------------------
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

# ----------------------------------------------------------
# UI
# ----------------------------------------------------------
st.title("🫀 Multi-Channel Cardiotoxicity Predictor")
st.caption("Predicts hERG / Cav / Nav ion-channel blockade risk and a fused cardiotoxicity risk score, from SMILES.")

tab1, tab2 = st.tabs(["Single Compound", "Batch (CSV Upload)"])

with tab1:
    smiles_input = st.text_input("Enter SMILES", placeholder="e.g. CC(=O)Oc1ccccc1C(=O)O")

    if st.button("Predict", type="primary"):
        mol = Chem.MolFromSmiles(smiles_input) if smiles_input else None
        if mol is None:
            st.error("Invalid or empty SMILES string.")
        else:
            col1, col2 = st.columns([1, 2])
            with col1:
                img = Draw.MolToImage(mol, size=(300, 300))
                st.image(img, caption="Structure")

            with col2:
                with st.spinner("Running predictions..."):
                    result = predict_cardiotoxicity(smiles_input)

                tier_color = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
                st.metric("Composite Risk Score", f"{result['composite_score']:.3f}",
                           f"{tier_color.get(result['risk_tier'],'')} {result['risk_tier']} Risk")
                st.caption(f"Confidence: {result['confidence']}")

                st.write("**Per-channel blocker probability:**")
                c1, c2, c3 = st.columns(3)
                c1.metric("hERG", f"{result['herg_prob']:.3f}")
                c2.metric("Cav", f"{result['ca_prob']:.3f}")
                c3.metric("Nav", f"{result['na_prob']:.3f}")

                with st.expander("Applicability domain similarities"):
                    for ch, sim in result['ad_similarities'].items():
                        st.write(f"{ch.upper()}: max Tanimoto similarity to training set = {sim:.3f} "
                                 f"({'✓ in AD' if sim >= AD_THRESHOLD else '✗ outside AD'})")

with tab2:
    uploaded_file = st.file_uploader("Upload CSV with a 'SMILES' column", type='csv')

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        smiles_col = st.selectbox("Which column contains SMILES?", df.columns.tolist())

        if st.button("Run batch prediction", type="primary"):
            progress = st.progress(0)
            batch_results = []

            for i, smi in enumerate(df[smiles_col]):
                try:
                    r = predict_cardiotoxicity(str(smi))
                    batch_results.append({
                        'SMILES': smi, 'hERG_prob': round(r['herg_prob'], 3),
                        'Ca_prob': round(r['ca_prob'], 3), 'Na_prob': round(r['na_prob'], 3),
                        'Composite_score': round(r['composite_score'], 3),
                        'Risk_tier': r['risk_tier'], 'Confidence': r['confidence'],
                    })
                except Exception as e:
                    batch_results.append({'SMILES': smi, 'hERG_prob': None, 'Ca_prob': None,
                                           'Na_prob': None, 'Composite_score': None,
                                           'Risk_tier': 'ERROR', 'Confidence': str(e)})
                progress.progress((i + 1) / len(df))

            results_df = pd.DataFrame(batch_results)
            st.dataframe(results_df, use_container_width=True)

            st.write("**Summary:**")
            st.write(results_df['Risk_tier'].value_counts())

            csv_buffer = io.StringIO()
            results_df.to_csv(csv_buffer, index=False)
            st.download_button("Download results (CSV)", csv_buffer.getvalue(),
                                "cardiotoxicity_predictions.csv", "text/csv")

st.divider()
st.caption("Composite score = hERG_risk × (1 − mitigation_weight × mean(Ca_risk, Na_risk)). "
           "Ca/Na channel block is treated as electrophysiologically mitigating hERG-driven risk (CiPA-style fusion).")
