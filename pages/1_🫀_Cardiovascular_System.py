import streamlit as st

st.set_page_config(page_title="Cardiovascular System & Cardiotoxicity", layout="wide", page_icon="🫀")

st.markdown(
    "<div style='display:flex; align-items:center; gap:12px;'>"
    "<span style='font-size:48px;'>🫀</span>"
    "<h1 style='margin:0;'><span style='color:#E63946;'>Cardiotox</span>"
    "<span style='color:#2A9D8F;'>-UR</span></h1>"
    "</div>",
    unsafe_allow_html=True,
)
st.title("The Heart's Electrical System & Cardiotoxicity")

st.header("How the Heart Beats: A Quick Primer")
st.markdown("""
Every heartbeat is triggered by a precisely timed electrical signal called the **cardiac action potential**,
generated as ions flow in and out of heart muscle cells (cardiomyocytes) through specialized protein channels
embedded in the cell membrane. Three ion channels dominate this process — sodium (Na⁺), calcium (Ca²⁺), and
potassium (K⁺) — each responsible for a distinct phase of the heartbeat.
""")

st.header("The Three Channels")

st.subheader("🟦 Sodium Channels (Nav) — the trigger")
st.markdown("""
Fast-opening Nav channels initiate the action potential (**Phase 0**, rapid depolarization), causing a sudden
influx of Na⁺ that flips the cell's internal voltage from negative to positive almost instantly. This is what
allows the electrical signal to propagate rapidly across heart tissue, coordinating a synchronized contraction.

**Effect of blocking Nav:** Slowed electrical conduction through heart tissue. Mild blockade can be therapeutic
(several antiarrhythmic drugs work this way), but excessive blockade can cause dangerously slow conduction,
widened QRS complexes on an ECG, and life-threatening arrhythmias like ventricular tachycardia.
""")

st.subheader("🟩 Calcium Channels (Cav) — the contraction signal")
st.markdown("""
L-type calcium channels open during **Phase 2 (the plateau phase)**, allowing Ca²⁺ to flow into the cell.
This calcium influx is the direct trigger for muscle contraction (excitation-contraction coupling) and also
sustains the action potential's plateau, which is critical for coordinated, forceful heart contraction.

**Effect of blocking Cav:** Reduced contractile force and slowed conduction through the AV node. This is
therapeutically useful in some contexts (calcium channel blockers treat hypertension and certain arrhythmias),
but excessive blockade can cause low blood pressure, bradycardia (slow heart rate), or heart block.
""")

st.subheader("🟥 Potassium Channels (hERG/Kv) — the reset")
st.markdown("""
The hERG (human Ether-à-go-go-Related Gene) potassium channel governs **Phase 3 (repolarization)** — it lets
K⁺ flow out of the cell, restoring the negative resting voltage and 'resetting' the cell so it's ready for the
next beat. This determines the QT interval seen on an ECG.

**Effect of blocking hERG:** This is the single most common cause of drug-induced cardiotoxicity. Blocking
hERG delays repolarization, **prolonging the QT interval**. A prolonged QT interval creates a vulnerable
window where a stray electrical impulse can trigger **Torsades de Pointes (TdP)** — a chaotic, life-threatening
ventricular arrhythmia that can degenerate into sudden cardiac death.
""")

st.header("What Is Cardiotoxicity?")
st.markdown("""
**Cardiotoxicity** refers to any drug- or chemical-induced damage or dysfunction of the heart or its electrical
system. In drug discovery, it most often refers specifically to **ion-channel-mediated cardiotoxicity** — a
compound unintentionally binding to and blocking one or more of these channels, disrupting the heart's normal
rhythm even though the drug was designed for a completely different therapeutic purpose.

This is precisely why cardiotoxicity screening exists as a distinct, mandatory stage in drug development —
a compound can be highly effective against its intended target and still be unsafe if it also blocks hERG,
Cav, or Nav as an unintended side effect.
""")

st.header("Why This Is a Major Challenge in Drug Discovery")
st.markdown("""
- **hERG's binding pocket is unusually promiscuous.** Its large, flexible pore accommodates a wide range of
  structurally diverse molecules, making it one of the easiest off-targets to hit by accident — and one of the
  hardest to design around.
- **It has ended real drugs' careers.** Several drugs (e.g., terfenadine, cisapride, astemizole) were withdrawn
  from the market after post-approval reports of fatal arrhythmias traced back to hERG blockade.
- **It's a leading cause of late-stage and post-market drug failure**, making early, computational screening
  (like this project) valuable — catching liability *before* expensive clinical trials, rather than after.
- **Multi-channel effects can offset each other.** A compound that blocks hERG but *also* blocks Cav/Nav may
  carry lower real-world arrhythmia risk than hERG blockade alone suggests, since balanced multi-channel block
  can be less pro-arrhythmic than "pure" hERG block — this nuance is exactly what CardioTox-UR's fusion model
  is designed to capture, rather than relying on hERG activity alone.
""")

st.info("See the **Model Details** page for how CardioTox-UR translates this biology into a computational "
        "risk score.")
