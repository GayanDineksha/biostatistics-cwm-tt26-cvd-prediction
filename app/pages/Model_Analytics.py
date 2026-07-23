import streamlit as st
import pandas as pd
import plotly.express as px
from utils import require_login, clinical_disclaimer, load_artifacts, FEATURE_COLUMNS, inject_custom_css

st.set_page_config(page_title="Model Analytics", page_icon="📊", layout="wide")
inject_custom_css()
require_login()

st.title("📊 Model Analytics & Explainability")
st.write(
    "Interactive charts generated directly from the trained model and "
    "training-data summary statistics — no static image exports required."
)

model, scaler = load_artifacts()

col1, col2 = st.columns(2)


with col1:
    st.subheader("Random Forest Feature Importance")
    importance_df = pd.DataFrame({
        "Feature": FEATURE_COLUMNS,
        "Importance": model.feature_importances_,
    }).sort_values("Importance", ascending=True)

    fig_importance = px.bar(
        importance_df, x="Importance", y="Feature", orientation="h",
        color="Importance", color_continuous_scale="Blues",
    )
    fig_importance.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#E8E8E8", showlegend=False, coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_importance, use_container_width=True)


with col2:
    st.subheader("Feature Correlation with CVD Diagnosis")
    correlation_with_target = {
        "thal": 0.52, "ca": 0.45, "exang": 0.45, "cp": 0.42, "oldpeak": 0.43,
        "slope": 0.34, "sex": 0.29, "age": 0.22, "restecg": 0.17,
        "trestbps": 0.14, "chol": 0.05, "fbs": -0.05, "thalach": -0.40,
    }
    corr_df = pd.DataFrame({
        "Feature": list(correlation_with_target.keys()),
        "Correlation": list(correlation_with_target.values()),
    }).sort_values("Correlation")

    fig_corr = px.bar(
        corr_df, x="Correlation", y="Feature", orientation="h",
        color="Correlation", color_continuous_scale="RdBu", range_color=[-0.5, 0.5],
    )
    fig_corr.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#E8E8E8", showlegend=False, coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_corr, use_container_width=True)

st.divider()
st.subheader("Key Evaluation Metrics")
m1, m2, m3 = st.columns(3)
m1.metric("Random Forest Accuracy", "81.63%")
m2.metric("Random Forest ROC-AUC", "0.888")
m3.metric("Neural Network ROC-AUC", "0.899")

st.divider()
st.subheader("🔬 What-If Sensitivity Analysis: Age vs CVD Risk")
st.write(
    "Adjust the slider to see how changing a patient's age alone (holding "
    "every other feature at a fixed, dataset-representative baseline) shifts "
    "the model's predicted risk."
)

BASELINE_PATIENT = {
    "age": 54, "sex": 1, "cp": 3, "trestbps": 131, "chol": 246,
    "fbs": 0, "restecg": 1, "thalach": 149, "exang": 0,
    "oldpeak": 1.0, "slope": 2, "ca": 1, "thal": 3,
}

selected_age = st.slider("Age", min_value=20, max_value=80, value=54)

age_range = list(range(20, 81, 2))
risk_curve = []
for a in age_range:
    patient = BASELINE_PATIENT.copy()
    patient["age"] = a
    patient_df = pd.DataFrame([patient], columns=FEATURE_COLUMNS)
    scaled = scaler.transform(patient_df)
    prob = model.predict_proba(scaled)[0][1]
    risk_curve.append(prob * 100)

chart_df = pd.DataFrame({"Age": age_range, "CVD Risk (%)": risk_curve})

fig_whatif = px.line(chart_df, x="Age", y="CVD Risk (%)", markers=True)
fig_whatif.add_vline(x=selected_age, line_dash="dash", line_color="#2E86AB")
fig_whatif.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font_color="#E8E8E8", margin=dict(l=10, r=10, t=10, b=10),
)
fig_whatif.update_traces(line_color="#2E86AB")
st.plotly_chart(fig_whatif, use_container_width=True)

patient_selected = BASELINE_PATIENT.copy()
patient_selected["age"] = selected_age
patient_df_sel = pd.DataFrame([patient_selected], columns=FEATURE_COLUMNS)
scaled_sel = scaler.transform(patient_df_sel)
prob_sel = model.predict_proba(scaled_sel)[0][1] * 100

st.metric(f"Predicted CVD Risk at Age {selected_age}", f"{prob_sel:.1f}%")
st.caption(
    "All other features fixed at baseline values (sex=Male, cp=Non-anginal "
    "pain, trestbps=131, chol=246, thalach=149, no exercise angina, "
    "oldpeak=1.0, slope=Flat, ca=1, thal=Normal). Only age varies."
)

clinical_disclaimer()