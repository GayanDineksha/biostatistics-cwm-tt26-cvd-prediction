import streamlit as st
import pandas as pd
from utils import require_login, clinical_disclaimer, load_artifacts, FEATURE_COLUMNS, inject_custom_css

st.set_page_config(page_title="Batch Processing", page_icon="📁", layout="wide")
inject_custom_css()
require_login()

st.title("📁 Batch Patient Processing")
st.write(
    "Upload a CSV file containing multiple patients (with the 13 clinical "
    "features below) to screen them all at once."
)
st.caption("Required columns: " + ", ".join(FEATURE_COLUMNS))

model, scaler = load_artifacts()

uploaded_file = st.file_uploader("Upload patient CSV", type=["csv"])

if uploaded_file is not None:
    try:
        batch_df = pd.read_csv(uploaded_file)
        missing_cols = [c for c in FEATURE_COLUMNS if c not in batch_df.columns]

        if missing_cols:
            st.error(f"Uploaded file is missing required columns: {missing_cols}")
        else:
            X_batch = batch_df[FEATURE_COLUMNS]
            X_batch_scaled = scaler.transform(X_batch)

            probs = model.predict_proba(X_batch_scaled)[:, 1]
            preds = model.predict(X_batch_scaled)

            results = batch_df.copy()
            results["cvd_risk_probability"] = probs.round(4)
            results["cvd_prediction"] = preds

            st.success(f"Processed {len(results)} patient(s).")

            col1, col2 = st.columns(2)
            col1.metric("Predicted CVD cases", int(preds.sum()))
            col2.metric("Predicted no-CVD cases", int(len(preds) - preds.sum()))

            st.dataframe(results, use_container_width=True)

            csv_out = results.to_csv(index=False).encode("utf-8")

            # --- Kaggle-format export: just Patient_ID + binary prediction ---
            if "id" in batch_df.columns:
                patient_ids = batch_df["id"]
            else:
                patient_ids = range(1, len(results) + 1)

            kaggle_df = pd.DataFrame({
                "Patient_ID": patient_ids,
                "target": preds,
            })
            kaggle_csv = kaggle_df.to_csv(index=False).encode("utf-8")

            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    "⬇️ Download Full Results (CSV)",
                    data=csv_out,
                    file_name="batch_screening_results.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with col_dl2:
                st.download_button(
                    "📥 Export Kaggle Submission (CSV)",
                    data=kaggle_csv,
                    file_name="kaggle_submission.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Awaiting CSV upload.")

clinical_disclaimer()