import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import io
import os
import re
from datetime import datetime

# Initialize the CSV file
CSV_FILE = "parsed_patients.csv"
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=[
        "Patient Name", "Date of Birth", "Scheme Number", "Scheme Name",
        "Patient Number", "Referring Doctor", "ICD-10 Code", "Treatment Date", "Notes"
    ])
    df.to_csv(CSV_FILE, index=False)

# Helper: parse text from hospital sticker OCR
def parse_sticker_text(text):
    lines = text.splitlines()
    data = {
        "Patient Name": "",
        "Date of Birth": "",
        "Scheme Number": "",
        "Scheme Name": "",
        "Patient Number": "",
        "Referring Doctor": ""
    }

    for line in lines:
        if re.search(r"\b\d{2}/\d{2}/\d{4}\b", line):
            data["Date of Birth"] = re.search(r"\b\d{2}/\d{2}/\d{4}\b", line).group()
        if "Dr" in line or "DR" in line:
            data["Referring Doctor"] = line.strip()
        if re.search(r"\b\d{8,}\b", line):
            if not data["Scheme Number"]:
                data["Scheme Number"] = re.search(r"\b\d{8,}\b", line).group()
        if "GOVERNMENT" in line.upper() or "DISCOVERY" in line.upper() or "GEMS" in line.upper():
            data["Scheme Name"] = line.strip()
        if re.search(r"^[A-Z]*\d+$", line):
            data["Patient Number"] = line.strip()
        if any(name_part in line for name_part in ["Mr", "Mrs", "Ms", "Miss"]):
            data["Patient Name"] = line.strip()

    return data

# Streamlit UI
st.title("Hospital Sticker Parser + Patient Data Form")
st.markdown("Upload a sticker photo, and add treatment details.")

uploaded_file = st.file_uploader("Upload hospital sticker image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Sticker", use_column_width=True)

    # OCR
    with st.spinner("Extracting text with OCR..."):
        text = pytesseract.image_to_string(image)
        parsed = parse_sticker_text(text)

    st.success("Sticker data parsed. You can edit/add info below.")

    # Editable form
    with st.form("patient_form"):
        patient_name = st.text_input("Patient Name", parsed["Patient Name"])
        dob = st.text_input("Date of Birth (DD/MM/YYYY)", parsed["Date of Birth"])
        scheme_number = st.text_input("Scheme Number", parsed["Scheme Number"])
        scheme_name = st.text_input("Scheme Name", parsed["Scheme Name"])
        patient_number = st.text_input("Patient Number", parsed["Patient Number"])
        doctor = st.text_input("Referring Doctor", parsed["Referring Doctor"])

        # Extra fields
        icd10 = st.text_input("ICD-10 Code")
        treatment_date = st.date_input("Treatment Date")
        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Save Entry")

        if submitted:
            new_row = {
                "Patient Name": patient_name,
                "Date of Birth": dob,
                "Scheme Number": scheme_number,
                "Scheme Name": scheme_name,
                "Patient Number": patient_number,
                "Referring Doctor": doctor,
                "ICD-10 Code": icd10,
                "Treatment Date": treatment_date.strftime("%d/%m/%Y"),
                "Notes": notes
            }
            df = pd.read_csv(CSV_FILE)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)
            st.success("Patient entry saved to CSV.")

# View saved data
if st.checkbox("Show saved patients"):
    df = pd.read_csv(CSV_FILE)
    st.dataframe(df)
    st.download_button("Download CSV", data=df.to_csv(index=False), file_name="parsed_patients.csv")
