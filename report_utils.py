# ==========================================================
# PDF + CSV report generation helpers
# ==========================================================

from fpdf import FPDF
import pandas as pd
import io

def safe_text(text):
    """FPDF's core fonts only support latin-1 — replace anything outside that range."""
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def generate_single_pdf(smiles, result, mol_img_path=None):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", 'B', 18)
    pdf.set_text_color(230, 57, 70)
    pdf.cell(0, 12, "CardioTox-UR", ln=True, align='C')
    pdf.set_font("Helvetica", '', 12)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, "Cardiotoxicity Prediction Report", ln=True, align='C')
    pdf.ln(5)

    if mol_img_path:
        pdf.image(mol_img_path, x=75, w=60)
        pdf.ln(5)

    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "SMILES:", ln=True)
    pdf.set_font("Helvetica", '', 10)
    pdf.multi_cell(0, 6, safe_text(smiles))
    pdf.ln(3)

    pdf.set_font("Helvetica", 'B', 13)
    tier_colors = {'High': (220, 53, 69), 'Medium': (255, 193, 7), 'Low': (40, 167, 69)}
    r, g, b = tier_colors.get(result['risk_tier'], (0, 0, 0))
    pdf.set_text_color(r, g, b)
    pdf.cell(0, 10, f"Risk Tier: {result['risk_tier']}  (Composite Score: {result['composite_score']:.3f})", ln=True)

    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, f"Confidence: {safe_text(result['confidence'])}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "Per-Channel Blocker Probability", ln=True)
    pdf.set_font("Helvetica", '', 10)
    pdf.cell(0, 6, f"hERG (potassium): {result['herg_prob']:.3f}", ln=True)
    pdf.cell(0, 6, f"Cav (calcium):    {result['ca_prob']:.3f}", ln=True)
    pdf.cell(0, 6, f"Nav (sodium):     {result['na_prob']:.3f}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", 'I', 8)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 5, "Composite score = hERG_risk x (1 - mitigation_weight x mean(Ca_risk, Na_risk)). "
                         "This is a computational prediction for research use only and is not a substitute "
                         "for experimental validation or clinical judgment.")

    return bytes(pdf.output(dest='S'))

def generate_single_csv(smiles, result):
    df = pd.DataFrame([{
        'SMILES': smiles, 'hERG_prob': round(result['herg_prob'], 3),
        'Ca_prob': round(result['ca_prob'], 3), 'Na_prob': round(result['na_prob'], 3),
        'Composite_score': round(result['composite_score'], 3),
        'Risk_tier': result['risk_tier'], 'Confidence': result['confidence'],
    }])
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()
