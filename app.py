import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np
import os
import re

# Custom CSS for styling
st.markdown("""
    <style>
    body {
        background-color: #ffffff;
    }
    .stApp {
        max-width: 100%;
        padding: 1rem;
    }
    .stButton > button {
        background-color: #b49649 !important;
        color: white !important;
        font-weight: bold;
        border: none;
        padding: 0.6em 1.2em;
        border-radius: 5px;
    }
    .stButton > button:hover {
        background-color: #9e8540 !important;
    }
    h1, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #1e1e1e !important;
    }
    </style>
""", unsafe_allow_html=True)

# Admin access
with st.sidebar:
    access_code = st.text_input("Enter admin access code", type="password")
    is_admin = access_code == "admin123"

# Initialize easyocr reader
reader = easyocr.Reader(['en'])

# Load or initialize CSV
csv_file = "parsed_patients.csv"
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
else:
    df = pd.DataFrame(columns=[
        "Patient Name", "Date of Birth", "Scheme Number",
        "Scheme Name", "Patient Number", "Referring Doctor",
        "Treatment Dates", "ICD10 Codes", "Treatment Codes"
    ])

# Add branding
st.image("fdm_logo.png", width=200)
st.markdown("""
<h1 style='font-size: 30px; color: #1e1e1e;'>Areta – <span style='color: #b49649;'>Physiotherapy Claims Management System</span></h1>
""", unsafe_allow_html=True)

st.header("🩺 Upload Hospital Sticker & Submit Claim")

# Upload image
uploaded_file = st.file_uploader("Upload a hospital sticker image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded sticker", use_column_width=True)

    # Convert to NumPy array for easyocr
    image_np = np.array(image)

    # Perform OCR with easyocr
    results = reader.readtext(image_np)
    full_text = " ".join([res[1] for res in results])

    # Show extracted raw text
    with st.expander("🧾 View extracted text"):
        st.text(full_text)

    # Detect hospital name
    hospital = "Unknown"
    if "HEROLIM" in full_text.upper():
        hospital = "HEROLIM"
    elif "ST MARY" in full_text.upper():
        hospital = "St Mary’s"
    elif "CROSSMED" in full_text.upper():
        hospital = "Crossmed"

    # Initialize parsed values
    patient_name = ""
    dob = ""
    scheme_number = ""
    scheme_name = ""
    patient_number = ""
    referring_doctor = ""
    treatment_dates = ""
    icd10_codes = ""
    treatment_codes = ""

    # Apply hospital-specific parsing rules
    if hospital == "HEROLIM":
        dob_match = re.search(r'\d{2}/\d{2}/\d{4}', full_text)
        dob = dob_match.group(0) if dob_match else ""
        doctor_match = re.search(r'Dr\.?\s+[A-Z][a-z]+', full_text, re.IGNORECASE)
        referring_doctor = doctor_match.group(0) if doctor_match else ""
        scheme_number_match = re.search(r'\b\d{9}\b', full_text)
        scheme_number = scheme_number_match.group(0) if scheme_number_match else ""
        scheme_name_match = re.search(r'MED\s+SCHEME[:\s]+([A-Z ]+)', full_text, re.IGNORECASE)
        if scheme_name_match:
            scheme_name = scheme_name_match.group(1).strip()
        patient_number_match = re.search(r'PATIENT\s+NUMBER[:\s]+([A-Z0-9]+)', full_text, re.IGNORECASE)
        if patient_number_match:
            patient_number = patient_number_match.group(1).strip()
        name_match = re.search(r'^[A-Z][a-z]+,?\s+[A-Z][a-z]+\s+Mr|Mrs|Ms', full_text)
        if name_match:
            patient_name = name_match.group(0).strip()

    elif hospital == "St Mary’s" or hospital == "Crossmed":
        dob_match = re.search(r'\d{2}/\d{2}/\d{4}', full_text)
        dob = dob_match.group(0) if dob_match else ""
        doctor_match = re.search(r'Dr\.?\s+[A-Z][a-z]+', full_text, re.IGNORECASE)
        referring_doctor = doctor_match.group(0) if doctor_match else ""
        scheme_number_match = re.search(r'\b\d{9}\b', full_text)
        scheme_number = scheme_number_match.group(0) if scheme_number_match else ""
        scheme_name_match = re.search(r'GOVERNMENT EMPLOYEES|GEMS|DISCOVERY|BONITAS|MEDICAL SCHEME', full_text, re.IGNORECASE)
        if scheme_name_match:
            scheme_name = scheme_name_match.group(0).strip()
        patient_number_match = re.search(r'\b[M]\d{4,8}\b|\b\d{5,9}\b', full_text)
        if patient_number_match:
            patient_number = patient_number_match.group(0).strip()
        name_match = re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+\s+(Mr|Mrs|Ms)', full_text)
        if name_match:
            patient_name = name_match.group(0).strip()

    # Display form with prefilled fields (editable)
    st.subheader("Extracted / Manual Entry Fields")
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Patient Name", value=patient_name)
        dob = st.text_input("Date of Birth", value=dob)
        scheme_number = st.text_input("Scheme Number", value=scheme_number)
        treatment_dates = st.text_input("Treatment Dates", value=treatment_dates)
    with col2:
        scheme_name = st.text_input("Scheme Name", value=scheme_name)
        patient_number = st.text_input("Patient Number", value=patient_number)
        referring_doctor = st.text_input("Referring Doctor", value=referring_doctor)
        icd10_codes = st.text_input("ICD10 Codes", value=icd10_codes)
    treatment_codes = st.text_input("Treatment Codes", value=treatment_codes)

    if st.button("Save Patient"):
        new_row = {
            "Patient Name": patient_name,
            "Date of Birth": dob,
            "Scheme Number": scheme_number,
            "Scheme Name": scheme_name,
            "Patient Number": patient_number,
            "Referring Doctor": referring_doctor,
            "Treatment Dates": treatment_dates,
            "ICD10 Codes": icd10_codes,
            "Treatment Codes": treatment_codes
        }
        df = df.append(new_row, ignore_index=True)
        df.to_csv(csv_file, index=False)
        st.success("✅ Data saved!")

# Admin-only section for reports
if is_admin:
    st.header("📁 Admin – Saved Patient Reports")
    st.dataframe(df)
    st.download_button("Download CSV", data=df.to_csv(index=False), file_name="parsed_patients.csv")
