"""
Shared utilities for the CVD Clinical Decision Support Portal.
Used by app.py and every file in pages/.
"""

import streamlit as st
import joblib

FEATURE_COLUMNS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal",
]

USERS = {
    "admin": {"password": "password123", "role": "admin"},
    "clinician": {"password": "clin123", "role": "clinician"},
    "analyst": {"password": "analyst123", "role": "analyst"},
}


@st.cache_resource
def load_artifacts():
    """Load the trained Random Forest model and fitted scaler."""
    model = joblib.load("rf_model.joblib")
    scaler = joblib.load("scaler.joblib")
    return model, scaler


def require_login():
    """
    Gatekeeper for every page in pages/. If the user hasn't logged in
    via app.py, stop rendering the rest of the page.
    """
    if not st.session_state.get("authenticated", False):
        st.error("🔒 Please log in from the main page first.")
        st.stop()


def require_role(*allowed_roles):
    """
    Gatekeeper for role-restricted pages (e.g. admin-only). Checks login
    first, then checks the logged-in user's role against allowed_roles.
    Usage: require_role("admin")  or  require_role("admin", "analyst")
    """
    require_login()
    if st.session_state.get("role") not in allowed_roles:
        st.error(
            f"🚫 Access Denied — this page is restricted to: {', '.join(allowed_roles)}. "
            f"Your role: {st.session_state.get('role', 'unknown')}."
        )
        st.stop()


def inject_custom_css():
    """
    Global styling applied on every page. Call once, right after
    st.set_page_config(), at the top of every page file (and app.py).
    """
    st.markdown(
        """
        <style>
        /* Metric cards: subtle border, dark card background, rounded corners */
        div[data-testid="stMetric"] {
            background-color: #1A2332;
            border: 1px solid #2E3A4D;
            padding: 16px 18px;
            border-radius: 14px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.25);
        }
        div[data-testid="stMetric"] label {
            color: #9BA8BC !important;
        }

        /* Primary action buttons (e.g. Predict CVD Risk, Log In) */
        button[kind="primary"] {
            background: linear-gradient(90deg, #2E86AB, #1B5E7D);
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.65em 1.3em;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        button[kind="primary"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 14px rgba(46,134,171,0.45);
        }

        /* Secondary/regular buttons */
        .stButton > button, .stDownloadButton > button {
            border-radius: 10px;
        }

        /* Tabs — rounded top corners, comfortable padding */
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px 10px 0 0;
            padding: 10px 18px;
            background-color: #1A2332;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2E86AB !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #0B0F17;
            border-right: 1px solid #2E3A4D;
        }

        /* Dataframes / tables: rounded corners */
        div[data-testid="stDataFrame"] {
            border-radius: 10px;
            overflow: hidden;
        }

        /* Cards used for the risk banner and similar custom containers */
        .risk-card {
            border-radius: 14px;
            padding: 22px;
            text-align: center;
            margin: 14px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def clinical_disclaimer():
    """Standard footer disclaimer, shown on every page."""
    st.markdown(
        """
        <div style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #333;">
            <p style="font-size: 0.8em; font-style: italic; color: gray; text-align: center;">
            ⚠️ Clinical Disclaimer: This application is a prototype developed exclusively
            for academic research (Module: CIS 6005 Computational Intelligence).
            The machine learning models and probabilities presented are not intended
            for medical diagnosis, treatment, or clinical use. Always consult a certified
            healthcare professional for medical advice.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )