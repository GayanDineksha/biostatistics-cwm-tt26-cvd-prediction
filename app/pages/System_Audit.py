import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils import require_role, clinical_disclaimer, inject_custom_css

st.set_page_config(page_title="System Audit", page_icon="🛡️", layout="wide")
inject_custom_css()

# Only admins may view this page — anyone else gets an access-denied message
require_role("admin")

st.title("🛡️ System Audit Log")
st.write("Administrative view of recent system activity.")

now = datetime.now()
audit_data = [
    {"Timestamp": (now - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S"),
     "User ID": "clinician", "Role": "clinician",
     "Action": "Ran Single Patient Screening", "IP Address": "192.168.1.14"},
    {"Timestamp": (now - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
     "User ID": "analyst", "Role": "analyst",
     "Action": "Uploaded Batch CSV (42 patients)", "IP Address": "192.168.1.22"},
    {"Timestamp": (now - timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
     "User ID": "admin", "Role": "admin",
     "Action": "Logged in", "IP Address": "192.168.1.5"},
    {"Timestamp": (now - timedelta(hours=1, minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
     "User ID": "clinician", "Role": "clinician",
     "Action": "Downloaded Clinical Report", "IP Address": "192.168.1.14"},
    {"Timestamp": (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
     "User ID": "analyst", "Role": "analyst",
     "Action": "Exported Kaggle Submission CSV", "IP Address": "192.168.1.22"},
]
audit_df = pd.DataFrame(audit_data)

st.dataframe(audit_df, use_container_width=True, hide_index=True)

csv_out = audit_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Audit Log as CSV",
    data=csv_out,
    file_name=f"system_audit_log_{now.strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv",
    use_container_width=True,
)

st.caption(
    "Note: this is simulated audit data for demonstration purposes. A "
    "production system would log real authenticated actions server-side, "
    "not generate them client-side."
)

clinical_disclaimer()