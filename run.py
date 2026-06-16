import streamlit as st
from database.connection import init_db

st.set_page_config(
    page_title="SkyPredict | AI Airline Analytics",
    page_icon="\u2708\ufe0f",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme toggle
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

DARK_CSS = "<style>" \
    "[data-testid='stAppViewContainer'] {background:#0A0E1A; color:#E8EEF7;}" \
    "[data-testid='stSidebar'] {background:#0F1626; border-right:1px solid #1E2A45;}" \
    "[data-testid='stSidebar'] * {color:#C8D8F0 !important;}" \
    "h1,h2,h3,h4,h5,h6{color:#E8EEF7 !important;}" \
    ".stButton>button{border-radius:8px; color:white; background:#0066CC;}" \
    "[data-testid='stMetricValue']{color:#00A8E8 !important; font-weight:700;}" \
    "</style>"

LIGHT_CSS = "<style>" \
    "[data-testid='stAppViewContainer'] {background:#F0F4FF; color:#0A1A3A;}" \
    "[data-testid='stSidebar'] {background:#FFFFFF; border-right:1px solid #D0DCF0;}" \
    "[data-testid='stSidebar'] * {color:#1A2A4A !important;}" \
    "h1,h2,h3,h4,h5,h6{color:#0A1A3A !important;}" \
    ".stButton>button{border-radius:8px; color:white; background:#0066CC;}" \
    "[data-testid='stMetricValue']{color:#0055AA !important; font-weight:700;}" \
    "</style>"

# Apply theme
if st.session_state.dark_mode:
    st.markdown(DARK_CSS, unsafe_allow_html=True)
else:
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    icon = "\u1f319" if st.session_state.dark_mode else "\u2600\ufe0f"
    label = f"{icon}  Switch to {'Light' if st.session_state.dark_mode else 'Dark'} Mode"
    st.button(label, on_click=toggle_theme, use_container_width=True)
    st.divider()
    st.caption("\u2708\ufe0f SkyPredict v1.0")
    st.caption("PIA Airline Analytics Platform")

# Hero section
st.markdown("""
<div style='text-align:center; padding:2rem 0 1rem 0;'>
    <h1 style='font-size:3rem; font-weight:800; letter-spacing:-1px;'>
        \u2708\ufe0f SkyPredict
    </h1>
    <p style='font-size:1.2rem; opacity:0.7; margin-top:-0.5rem;'>
        AI-Powered Airline Passenger Demand Forecasting &amp; Analytics
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.info("\u1f4ca **Executive Dashboard**\nNetwork-wide KPIs at a glance")
with col2:
    st.info("\u1f4c8 **Demand Forecasting**\nSARIMA & ETS models with confidence intervals")
with col3:
    st.info("\u1f052 **AI Recommendations**\nHigh/Medium/Low confidence route actions")

st.divider()

# DB Init
try:
    init_db()
    st.success("\u2705 Database connected and schema ready.")
except Exception as e:
    st.error(f"Failed to connect to database: {e}")
    st.info("Check your .env file \u2014 ensure DB_USER, DC_PASSWORD and DB_NAME are correct.")
