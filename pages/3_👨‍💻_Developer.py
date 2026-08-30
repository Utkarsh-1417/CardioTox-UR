import streamlit as st
import os

st.set_page_config(page_title="Developer", layout="wide", page_icon="🫀")

st.markdown(
    "<div style='display:flex; align-items:center; gap:12px;'>"
    "<span><svg width='44' height='44' viewBox='0 0 24 24' fill='#E63946' xmlns='http://www.w3.org/2000/svg'><path d='M12 21s-6.7-4.35-9.33-8.2C.86 10.28 1.4 6.66 4.36 4.86 6.5 3.56 9.14 4.02 12 6.98 14.86 4.02 17.5 3.56 19.64 4.86 22.6 6.66 23.14 10.28 21.33 12.8 18.7 16.65 12 21 12 21z'/></svg></span>"
    "<h1 style='margin:0;'><span style='color:#E63946;'>Cardiotox</span>"
    "<span style='color:#2A9D8F;'>-UR</span></h1>"
    "</div>",
    unsafe_allow_html=True,
)
st.title("About the Developer")

col1, col2 = st.columns([1, 2])

with col1:
    if os.path.exists('developer_photo.jpg'):
        st.image('developer_photo.jpg', use_container_width=True)
    else:
        st.info("Developer photo not found.")

with col2:
    st.subheader("Utkarsh Kumar")
    st.caption("AI in Drug Discovery Intern · IIT (BHU) Varanasi")

    st.markdown("""
    Utkarsh completed his **Bachelor of Pharmacy in 2026** and went on to complete a
    **research internship at IIT (BHU) Varanasi**, focused on AI in Drug Discovery.

    He has also completed an **Executive Diploma in Pharmacovigilance**, an **Executive
    Diploma in Medical Writing**, an **Industrial Internship in Clinical Research**, and an
    **Executive Diploma in Clinical Data Management**.

    He has previously worked on developing a **hepatotoxicity (DILI) prediction model** and a
    **P2X7 receptor activity prediction model**, and is currently developing **cardiotoxicity
    prediction models** using machine learning and cheminformatics — combining a pharmaceutical
    sciences background with applied AI to build tools for early-stage drug safety and activity
    screening. **CardioTox-UR** is his latest project, predicting ion-channel-mediated
    cardiotoxicity risk from molecular structure.
    """)

    st.caption("This is an academic research project developed as a part of the requirement for the fulfillment of the Bachelor of Pharmacy (B.Pharm) degree.")

    st.markdown("### Connect")
    st.markdown("""
    🔗 [LinkedIn](https://www.linkedin.com/in/utkarsh-kumar-962046330)
    &nbsp;&nbsp;|&nbsp;&nbsp;
    💻 [GitHub](https://github.com/Utkarsh-1417)
    """)

st.divider()
st.caption("CardioTox-UR is an academic/research project and is intended for educational and "
           "early-stage screening purposes, not for clinical or regulatory decision-making.")
