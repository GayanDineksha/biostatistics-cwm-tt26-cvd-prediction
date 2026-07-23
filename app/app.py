import streamlit as st
from utils import clinical_disclaimer, inject_custom_css, USERS

st.set_page_config(page_title="CVD Clinical Portal - Login", page_icon="🔐", layout="centered")
inject_custom_css()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Hide the sidebar page navigation until the user logs in
if not st.session_state.authenticated:
    st.markdown(
        "<style>[data-testid='stSidebarNav'] {display: none;}</style>",
        unsafe_allow_html=True,
    )

st.title("🩺 CVD Clinical Decision Support Portal")
st.caption("Biostatistics CWM TT26 — Computational Intelligence Mini Project")

if st.session_state.authenticated:
    st.success(
        f"You are logged in as **{st.session_state.get('username', 'admin')}** "
        f"(role: **{st.session_state.get('role', 'unknown')}**)."
    )
    st.info(
        "Use the sidebar to navigate to the **Dashboard**, **Single Patient "
        "Screening**, **Batch Processing**, **Model Analytics**, or (admin "
        "only) **System Audit** pages."
    )
    if st.button("Log out"):
        st.session_state.authenticated = False
        st.rerun()
else:
    st.subheader("Clinician Login")
    st.caption(
        "Demo credentials — admin: `admin` / `password123` · "
        "clinician: `clinician` / `clin123` · analyst: `analyst` / `analyst123`"
    )

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In", use_container_width=True)

        if submitted:
            user_record = USERS.get(username)
            if user_record and user_record["password"] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.role = user_record["role"]
                st.rerun()
            else:
                st.error("Invalid username or password.")

clinical_disclaimer()