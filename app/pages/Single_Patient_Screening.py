import streamlit as st
import pandas as pd
from datetime import datetime
from utils import require_login, clinical_disclaimer, load_artifacts, FEATURE_COLUMNS, inject_custom_css

st.set_page_config(page_title="Single Patient Screening", page_icon="🩺", layout="wide")
inject_custom_css()
require_login()

st.title("🩺 Single Patient Screening")
st.write("Enter a patient's clinical measurements to estimate CVD risk.")

model, scaler = load_artifacts()

HIGH_RISK_PRESET = {
    "age": 63, "sex": 1, "cp": 4, "trestbps": 150, "chol": 290,
    "fbs": 0, "restecg": 2, "thalach": 110, "exang": 1,
    "oldpeak": 3.5, "slope": 2, "ca": 2, "thal": 7,
}

LOW_RISK_PRESET = {
    "age": 41, "sex": 0, "cp": 1, "trestbps": 115, "chol": 195,
    "fbs": 0, "restecg": 0, "thalach": 175, "exang": 0,
    "oldpeak": 0.0, "slope": 1, "ca": 0, "thal": 3,
}


def load_preset(preset: dict):
    for key, value in preset.items():
        st.session_state[key] = value


col_demo1, col_demo2 = st.columns(2)
with col_demo1:
    st.button(
        "⚠️ Load High-Risk Patient",
        use_container_width=True,
        on_click=load_preset,
        args=(HIGH_RISK_PRESET,),
    )
with col_demo2:
    st.button(
        "✅ Load Low-Risk Patient",
        use_container_width=True,
        on_click=load_preset,
        args=(LOW_RISK_PRESET,),
    )

st.divider()
st.header("Patient Information")

tab1, tab2 = st.tabs(["👤 Demographics & Vitals", "🫀 ECG & Heart Metrics"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("Age", min_value=18, max_value=100, key="age")
        sex = st.selectbox(
            "Sex", options=[0, 1], format_func=lambda x: "Female" if x == 0 else "Male", key="sex"
        )
        trestbps = st.number_input("Resting Blood Pressure (mm Hg)", min_value=80, max_value=220, key="trestbps")
    with c2:
        chol = st.number_input("Serum Cholesterol (mg/dl)", min_value=100, max_value=600, key="chol")
        fbs = st.selectbox(
            "Fasting Blood Sugar > 120 mg/dl?", options=[0, 1],
            format_func=lambda x: "No" if x == 0 else "Yes", key="fbs",
        )

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        cp = st.selectbox(
            "Chest Pain Type", options=[1, 2, 3, 4],
            format_func=lambda x: {1: "Typical angina", 2: "Atypical angina",
                                    3: "Non-anginal pain", 4: "Asymptomatic"}[x],
            key="cp",
        )
        restecg = st.selectbox(
            "Resting ECG Results", options=[0, 1, 2],
            format_func=lambda x: {0: "Normal", 1: "ST-T wave abnormality",
                                    2: "Left ventricular hypertrophy"}[x],
            key="restecg",
        )
        thalach = st.number_input("Max Heart Rate Achieved", min_value=60, max_value=220, key="thalach")
        exang = st.selectbox(
            "Exercise-Induced Angina?", options=[0, 1],
            format_func=lambda x: "No" if x == 0 else "Yes", key="exang",
        )
    with c2:
        oldpeak = st.number_input(
            "ST Depression (exercise vs rest)", min_value=0.0, max_value=10.0, step=0.1, key="oldpeak"
        )
        slope = st.selectbox(
            "Slope of Peak Exercise ST Segment", options=[1, 2, 3],
            format_func=lambda x: {1: "Upsloping", 2: "Flat", 3: "Downsloping"}[x],
            key="slope",
        )
        ca = st.selectbox("Number of Major Vessels (0-3, fluoroscopy)", options=[0, 1, 2, 3], key="ca")
        thal = st.selectbox(
            "Thalassemia", options=[3, 6, 7],
            format_func=lambda x: {3: "Normal", 6: "Fixed defect", 7: "Reversible defect"}[x],
            key="thal",
        )

st.divider()

if st.button("Predict CVD Risk", type="primary", use_container_width=True):
    input_data = pd.DataFrame(
        [[st.session_state[c] for c in FEATURE_COLUMNS]],
        columns=FEATURE_COLUMNS,
    )

    input_scaled = scaler.transform(input_data)
    probability = model.predict_proba(input_scaled)[0][1]
    prediction = model.predict(input_scaled)[0]
    risk_pct = probability * 100

    st.subheader("Result")

    # --- Dynamic visual risk banner ---
    if prediction == 1:
        st.markdown(
            f"""
            <div class="risk-card" style="background-color: rgba(220,53,69,0.15); border: 1px solid #dc3545;">
                <h2 style="color: #ff6b6b; margin: 0;">⚠️ HIGH RISK</h2>
                <p style="font-size: 1.3em; color: #ff6b6b; margin: 8px 0 0 0; font-weight: 600;">
                    Estimated CVD Probability: {risk_pct:.1f}%
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="risk-card" style="background-color: rgba(40,167,69,0.15); border: 1px solid #28a745;">
                <h2 style="color: #51cf66; margin: 0;">✅ LOW RISK</h2>
                <p style="font-size: 1.3em; color: #51cf66; margin: 8px 0 0 0; font-weight: 600;">
                    Estimated CVD Probability: {risk_pct:.1f}%
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.progress(min(int(risk_pct), 100))

    with st.expander("How to interpret this"):
        st.write(
            f"""
            The model estimates a **{risk_pct:.1f}%** probability that this patient's
            clinical profile is consistent with cardiovascular disease, based on
            patterns learned from 242 patients in the training dataset.

            This is a probability, not a certainty — the model has a test-set
            accuracy of ~82% and a ROC-AUC of ~0.89, meaning it is a useful but
            imperfect screening indicator, not a diagnosis.
            """
        )

    # --- Generate a downloadable clinical report ---
    report_text = f"""CVD CLINICAL SCREENING REPORT
==============================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Clinician: {st.session_state.get('username', 'N/A')}

PATIENT CLINICAL FEATURES
--------------------------
Age: {age}
Sex: {'Male' if sex == 1 else 'Female'}
Chest Pain Type (code): {cp}
Resting Blood Pressure: {trestbps} mm Hg
Serum Cholesterol: {chol} mg/dl
Fasting Blood Sugar > 120 mg/dl: {'Yes' if fbs == 1 else 'No'}
Resting ECG (code): {restecg}
Max Heart Rate Achieved: {thalach}
Exercise-Induced Angina: {'Yes' if exang == 1 else 'No'}
ST Depression (oldpeak): {oldpeak}
Slope of Peak Exercise ST Segment (code): {slope}
Number of Major Vessels: {ca}
Thalassemia (code): {thal}

PREDICTION RESULT
--------------------------
CVD Risk Probability: {risk_pct:.1f}%
Prediction: {'CVD Positive' if prediction == 1 else 'No CVD'}

MODEL INFO
--------------------------
Model: Random Forest Classifier (100 estimators)
Test Accuracy: ~81.63% | ROC-AUC: ~0.888

CLINICAL DISCLAIMER
--------------------------
This report is generated by a prototype developed exclusively for academic
research (Module: CIS 6005 Computational Intelligence). This is NOT a medical
diagnosis. Always consult a certified healthcare professional for medical advice.
"""

    st.download_button(
        "📄 Download Clinical Report (.txt)",
        data=report_text,
        file_name=f"Clinical_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True,
    )

    # --- Log this screening to session state ---
    if "screening_log" not in st.session_state:
        st.session_state.screening_log = []

    st.session_state.screening_log.insert(0, {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Age": age, "Sex": "Male" if sex == 1 else "Female",
        "Risk %": f"{risk_pct:.1f}%",
        "Prediction": "CVD" if prediction == 1 else "No CVD",
    })

st.divider()
st.subheader("Recent Screenings (this session)")
st.caption(
    "Stored in memory for this browser session only — not a persistent "
    "database. Resets when the app restarts or another user opens it."
)

log = st.session_state.get("screening_log", [])
if log:
    st.dataframe(pd.DataFrame(log), use_container_width=True, hide_index=True)
else:
    st.caption("No screenings recorded yet.")

clinical_disclaimer()