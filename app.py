import pandas as pd
import streamlit as st
from src.services import PredictionService

# Page setup
st.set_page_config(
    page_title="SIRA - Incident Classifier",
    page_icon="🚨",
    layout="centered",
)

st.title("🚨 SIRA: Smart Incident Report Analyzer")
st.markdown(
    "Automated NLP classification engine for oil & gas operational safety reports."
)

# Load prediction service once (cached for speed)
@st.cache_resource
def load_service():
    return PredictionService()

try:
    service = load_service()
    st.success("Model artifacts loaded successfully!", icon="✅")
except Exception as e:
    st.error(f"Failed to load model artifacts: {e}")
    st.stop()

# Tabbed UI
tab1, tab2 = st.tabs(["Single Incident Classifier", "Batch File Processing"])

with tab1:
    st.subheader("Analyze Single Log")
    user_input = st.text_area(
        "Enter Incident Report Narrative:",
        height=120,
        placeholder="e.g., Gas leak detected near pressure control valve in Block B manifold...",
    )

    if st.button("Classify Incident", type="primary"):
        if user_input.strip():
            prediction = service.predict_single(user_input)
            st.markdown(f"### **Predicted Category:** `{prediction}`")
        else:
            st.warning("Please enter a valid report description before analyzing.")

with tab2:
    st.subheader("Batch Process CSV")
    uploaded_file = st.file_uploader("Upload CSV containing report text", type=["csv"])

    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
        text_column = st.selectbox("Select Text Column:", batch_df.columns)

        if st.button("Process Batch Predictions"):
            with st.spinner("Classifying reports..."):
                batch_df["Predicted_Category"] = batch_df[text_column].apply(
                    lambda x: service.predict_single(str(x))
                )
            st.dataframe(batch_df, use_container_width=True)

            csv_data = batch_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Categorized Results",
                data=csv_data,
                file_name="classified_incidents.csv",
                mime="text/csv",
            )