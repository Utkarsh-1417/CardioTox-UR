import streamlit as st
import os

st.set_page_config(page_title="Developer", layout="wide", page_icon="🫀")

st.markdown(
    "<div style='display:flex; align-items:center; gap:12px;'>"
    "<span style='font-size:48px;'>🫀</span>"
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

    He is currently developing **cardiotoxicity prediction models** using machine learning
    and cheminformatics — combining pharmaceutical sciences background with applied AI to
    build tools for early-stage drug safety screening. **CardioTox-UR** is one such project,
    predicting ion-channel-mediated cardiotoxicity risk from molecular structure.
    """)

    st.markdown("### Connect")
    st.markdown("""
    🔗 [LinkedIn](https://www.linkedin.com/in/utkarsh-kumar-962046330)
    &nbsp;&nbsp;|&nbsp;&nbsp;
    💻 [GitHub](https://github.com/Utkarsh-1417)
    """)

st.divider()
st.caption("CardioTox-UR is an academic/research project and is intended for educational and "
           "early-stage screening purposes, not for clinical or regulatory decision-making.")
