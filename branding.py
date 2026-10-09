import base64
from pathlib import Path
import streamlit as st

ASSETS = Path(__file__).parent / "assets"

WATERMARK_OPACITY = 0.10      # raise = stronger, lower = fainter
WATERMARK_SIZE = "min(70vw, 760px)"

@st.cache_resource
def _b64(name):
    return base64.b64encode((ASSETS / name).read_bytes()).decode()

@st.cache_resource
def _logo_bytes():
    return (ASSETS / "cardiotriad_ur_logo.png").read_bytes()

def inject_watermark():
    data = _b64("watermark.webp")
    st.markdown(f"""
    <style>
    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: url("data:image/webp;base64,{data}") no-repeat center 58% / {WATERMARK_SIZE} auto;
        opacity: {WATERMARK_OPACITY};
        pointer-events: none;
        z-index: 0;
    }}
    [data-testid="stMainBlockContainer"], .block-container {{
        position: relative;
        z-index: 1;
    }}
    </style>
    """, unsafe_allow_html=True)

def logo_download_button():
    st.sidebar.download_button(
        label="⬇️ Download App Logo",
        data=_logo_bytes(),
        file_name="CardioTriad-UR_logo.png",
        mime="image/png",
        key="download_logo_btn",
    )

def apply_branding():
    inject_watermark()
    logo_download_button()
