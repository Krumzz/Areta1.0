import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np
import os

# Initialize easyocr reader
reader = easyocr.Reader(['en'])

# Load or initialize CSV
csv_file = "parsed_patients.csv"
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
else:
    df = pd.DataFrame(columns=[
        "Patient Name", "Date of Birth", "Scheme Number",
        "Scheme Name", "Patient Number", "Referring Doctor"
    ])

st.title("Areta1.0 - Hospital Sticker Parser")

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

    # Let user manually correct/add parsed fields
    st.subheader("Extracted / Manual Entry Fields")
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Patient Name")
        dob = st.text_input("Date of Birth")
        scheme_number = st.text_input("Scheme Number")
    with col2:
        scheme_name = st.text_input("Scheme Name")
        patient_number = st.text_input("Patient Number")
        referring_doctor = st.text_input("Referring Doctor")

    if st.button("Save to CSV"):
        new_row = {
            "Patient Name": patient_name,
            "Date of Birth": dob,
            "Scheme Number": scheme_number,
            "Scheme Name": scheme_name,
            "Patient Number": patient_number,
            "Referring Doctor": referring_doctor,
        }
        df = df.append(new_row, ignore_index=True)
        df.to_csv(csv_file, index=False)
        st.success("✅ Data saved!")

# Display saved data
st.subheader("📋 Saved Patient Entries")
st.dataframe(df)
