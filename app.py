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
        font-size: 1.3em;
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
        font-size: 1.1em;
    }
    .stButton > button:hover {
        background-color: #9e8540 !important;
    }
    h1, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #1e1e1e !important;
        font-size: 1.8em;
    }
    .stTextInput > div > input {
        font-size: 1.1em !important;
    }
    .stDownloadButton > button {
        font-size: 1.1em;
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
<h1 style='font-size: 30px; color: white;'>Areta – <span style='color: #b49649;'>Physiotherapy Claims Management System</span></h1>
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
    lines = [res[1] for res in results]
    full_text = " ".join(lines)

    with st.expander("🧾 View extracted text"):
        for line in lines:
            st.text(line)

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
    if hospital == "Crossmed":
        for line in lines:
            if "name" in line.lower():
                patient_name = line.split(":")[-1].strip().title()
            elif re.search(r'(\d{2}[\-/]\d{2}[\-/]\d{4})', line):
                dob = re.search(r'(\d{2}[\-/]\d{2}[\-/]\d{4})', line).group(0).replace('-', '/')
            elif "scheme" in line.lower():
                scheme_name = line.split(":")[-1].strip().title()
            elif "med" in line.lower() and "no" in line.lower():
                match = re.search(r'(\d{9})', line)
                if match:
                    scheme_number = match.group(1)
            elif "patient" in line.lower():
                match = re.search(r'(\d{5,9})', line)
                if match:
                    patient_number = match.group(1)
            elif "dr" in line.lower():
                referring_doctor = line.strip().title()

    elif hospital == "HEROLIM":
        for line in lines:
            if "patient no" in line.lower():
                match = re.search(r'(\d+)', line)
                if match:
                    patient_number = match.group(1)
            elif "scheme no" in line.lower():
                match = re.search(r'(\d+)', line)
                if match:
                    scheme_number = match.group(1)
            elif "med scheme" in line.lower():
                scheme_name = line.split(":")[-1].strip().title()
            elif "date of birth" in line.lower():
                match = re.search(r'(\d{2}/\d{2}/\d{4})', line)
                if match:
                    dob = match.group(1)
            elif "name" in line.lower():
                patient_name = line.split(":")[-1].strip().title()
            elif "doctor" in line.lower() or "dr" in line.lower():
                referring_doctor = line.strip().title()

    elif hospital == "St Mary’s":
        for line in lines:
            if re.search(r'\((\d{2}/\d{2}/\d{4})\)', line):
                dob = re.search(r'\((\d{2}/\d{2}/\d{4})\)', line).group(1)
            elif "med" in line.lower() and "no" in line.lower():
                match = re.search(r'(\d+)', line)
                if match:
                    scheme_number = match.group(1)
            elif "med" in line.lower() and "aid" in line.lower():
                scheme_name = line.split(":")[-1].strip().title()
            elif re.search(r'm\d{3,6}', line.lower()):
                patient_number = re.search(r'(m\d{3,6})', line.lower()).group(1).upper()
            elif "dr" in line.lower():
                referring_doctor = line.strip().title()
            elif "name" in line.lower():
                patient_name = line.split(":")[-1].strip().title()

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
