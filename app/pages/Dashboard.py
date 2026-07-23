import streamlit as st
from utils import require_login, clinical_disclaimer, inject_custom_css

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
inject_custom_css()
require_login()

st.title("🏠 Dashboard")
st.write(f"Welcome, **{st.session_state.get('username', 'Doctor')}**.")

col1, col2, col3 = st.columns(3)
col1.metric("Random Forest Accuracy", "81.63%")
col2.metric("Random Forest ROC-AUC", "0.888")
col3.metric("Neural Network ROC-AUC", "0.899")

st.divider()

st.subheader("About this Portal")
st.write(
    """
    This portal uses a **Random Forest Classifier** trained on the Cleveland
    Heart Disease dataset (242 patients, 13 clinical features) to estimate
    cardiovascular disease risk.

    Use the sidebar to navigate:

    - **🩺 Single Patient Screening** — enter one patient's details for an instant risk estimate
    - **📁 Batch Processing** — upload a CSV of multiple patients for bulk screening
    - **📊 Model Analytics** — review EDA and model evaluation charts
    """
)

st.divider()
st.subheader("Recent Activity")
log = st.session_state.get("screening_log", [])
if log:
    st.write(f"{len(log)} screening(s) recorded this session.")
else:
    st.caption("No screenings recorded yet this session. Visit Single Patient Screening to begin.")

clinical_disclaimer()