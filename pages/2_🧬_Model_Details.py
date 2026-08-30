import streamlit as st

st.set_page_config(page_title="Model Details", layout="wide", page_icon="🫀")

st.markdown(
    "<div style='display:flex; align-items:center; gap:12px;'>"
    "<span style='font-size:48px;'>🫀</span>"
    "<h1 style='margin:0;'><span style='color:#E63946;'>Cardiotox</span>"
    "<span style='color:#2A9D8F;'>-UR</span></h1>"
    "</div>",
    unsafe_allow_html=True,
)
st.title("Model Architecture & Methodology")

st.header("Overview")
st.markdown("""
CardioTox-UR predicts cardiotoxicity risk by combining **three independently trained ion-channel
classifiers** — one each for hERG (potassium), Cav (calcium), and Nav (sodium) — through a
**rule-based late-fusion** layer, rather than a single multi-task model. This design was chosen because
each channel's dataset differs enormously in size and behaves differently under different model families,
so letting each channel pick its own best-suited model/ensemble gave stronger results than forcing one
architecture across all three.
""")

st.header("Data & Features")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **Datasets** (ChEMBL/PubChem-sourced bioactivity data):
    - hERG: 22,246 compounds
    - Cav: 802 compounds
    - Nav: 2,069 compounds

    **Train/Test/External-Validation split:** 70/20/10, using **Murcko scaffold-based splitting**
    (not random) — this guarantees no molecular scaffold appears in more than one split, giving a
    much more honest estimate of how the model performs on genuinely novel chemical structures.
    """)
with col2:
    st.markdown("""
    **Featurization:** ECFP4 (Morgan, radius=2) fingerprints + 13 RDKit physicochemical descriptors
    (MolLogP, TPSA, MolWt, RingCount, FractionCSP3, etc.)

    - hERG: 2048-bit fingerprint (full data supports it)
    - Cav / Nav: 1024-bit fingerprint + variance-threshold feature selection (624 / 694 bits kept)
      — smaller datasets need dimensionality control to avoid overfitting

    **Classification threshold:** pIC50 ≥ 5.0 (IC50 ≤ 10 µM) = "Blocker"
    """)

st.header("Per-Channel Model Selection")
st.markdown("""
9 classifiers were benchmarked per channel (Random Forest, Extra Trees, Gradient Boosting, XGBoost,
LightGBM, CatBoost, SVC, Logistic Regression, KNN), then combined into ensembles. The best-performing
combination differed by channel:
""")

perf_data = {
    "Channel": ["hERG (K⁺)", "Cav (Ca²⁺)", "Nav (Na⁺)"],
    "Final Model": ["Stacking (RF + ExtraTrees + LightGBM)", "Voting (LogReg + SVC + GradBoost)", "Voting (SVC + GradBoost + XGBoost)"],
    "Test ROC-AUC": [0.829, 0.855, 0.907],
    "External Val. ROC-AUC": [0.836, 0.843, 0.902],
    "Test Recall (Blocker)": [0.880, 0.762, 0.909],
}
st.dataframe(perf_data, use_container_width=True, hide_index=True)

st.markdown("""
A notable pattern: **stacking ensembles helped on the large hERG dataset but actively hurt performance
on the smaller Cav/Nav datasets** (stacking's internal cross-validation overfits when there isn't much
data), so simple soft-voting was used there instead. External validation scores tracking closely with
test scores across all three channels (gaps of −0.7 to +1.2 points) confirms the models generalize well
rather than overfitting to their training/test splits.
""")

st.header("Fusion: From 3 Channel Scores to One Risk Score")
st.markdown("""
Rather than treating hERG, Cav, and Nav block as independent additive risks, CardioTox-UR uses a
**CiPA-inspired mechanistic fusion rule**: calcium and sodium channel block are treated as
*electrophysiologically mitigating* — not adding to — hERG-driven arrhythmia risk, since balanced
multi-channel block is generally less pro-arrhythmic than "pure" hERG block alone. This reflects real
cardiac electrophysiology rather than a purely statistical combination.
""")

st.latex(r"\text{Composite Risk} = \text{hERG}_{risk} \times \left(1 - w \times \text{mean}(\text{Ca}_{risk}, \text{Na}_{risk})\right)")

st.markdown("""
where **w = 0.3** (mitigation weight). Risk is then bucketed into tiers: **High** (≥0.6), **Medium**
(≥0.3), **Low** (<0.3).

An **Applicability Domain (AD) check** runs alongside every prediction — the maximum Tanimoto structural
similarity between the query molecule and the training set, per channel. Predictions on molecules
structurally dissimilar to anything the model was trained on are flagged **"Low confidence (outside AD)"**,
since the model is extrapolating rather than interpolating in that case.
""")

st.header("Interpretability (SHAP Analysis)")
st.markdown("""
SHAP (KernelExplainer, applied to the full ensemble models) was used to understand *why* the models make
their predictions, not just what they predict. Two consistent findings emerged across all three channels:

- **MolLogP (lipophilicity) is the single strongest driver of blocker risk in all three channels** —
  consistent with well-established cardiac ion-channel structure-activity literature.
- **hERG risk leans more on simple physicochemical properties** (LogP, TPSA — ~40% of total explanatory
  weight), **while Cav and Nav risk lean more heavily on specific structural substructures** captured by
  fingerprint bits (~80% of total weight) — suggesting hERG's binding pocket is more promiscuous toward
  "what kind of molecule this is," while Cav/Nav are more sensitive to precise structural motifs.
""")

st.header("Validation Against Known Pharmacology")
st.markdown("""
The full pipeline was tested against 12 real-world drugs with documented cardiac risk profiles from
clinical literature — 6 known TdP-risk drugs, 2 possible/conditional-risk drugs, and 3 negative controls.

- **4 of 6 known-risk drugs** (Amiodarone, Methadone, Haloperidol, Terfenadine) were correctly flagged **High**
- **All 3 negative controls** (Aspirin, Metformin, Ibuprofen) were correctly flagged **Low** — no false positives
- One notable miss: **Sotalol**, a well-known hERG blocker, was under-predicted as Low risk — likely
  because it's unusually hydrophilic (low LogP) for a hERG blocker, and the model has learned a
  strong "lipophilic → risky" pattern from the wider training data. This is documented as a known
  model limitation rather than hidden.
""")

st.info("This model is intended for early-stage computational screening and research use. Predictions "
        "are not a substitute for experimental assay data, and results outside the applicability domain "
        "should be treated as directional rather than definitive.")
