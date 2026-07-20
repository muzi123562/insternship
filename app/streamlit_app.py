"""Streamlit app for Lead Generation Pipeline"""
import streamlit as st
import subprocess
import os

st.set_page_config(page_title="LeadGen Demo", layout="centered")
st.title("Automated Lead Generation & Outreach Demo")

st.markdown("Enter a business category and city, then run the pipeline.")
category = st.text_input("Business Category", value="Coffee shop")
city = st.text_input("City", value="San Francisco, CA")
num = st.number_input("Max results", min_value=1, max_value=50, value=10)

if st.button("Run Pipeline"):
    st.info("Starting pipeline — this may take a minute...")
    # Use subprocess to run the pipeline script so we keep the Streamlit process small
    cmd = ["python", "scripts/run_pipeline.py", "--category", category, "--city", city, "--num", str(num)]
    with st.spinner("Running..."):
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            st.write(line.strip())
    st.success("Pipeline finished. Check the storage (Google Sheets or CSV) and logs.")
