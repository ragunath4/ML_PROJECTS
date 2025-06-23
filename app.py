# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai

# Configure Gemini API key from .env
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to send resume + JD to Gemini model
def get_gemini_response(job_description, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([job_description, pdf_content[0], prompt])
    return response.text

# Convert uploaded PDF into image format for Gemini
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(
            uploaded_file.read(),
            poppler_path=r"C:\poppler\poppler-24.08.0\Library\bin"  # <-- Update this if your poppler is elsewhere
        )
        first_page = images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [{
            "mime_type": "image/jpeg",
            "data": base64.b64encode(img_byte_arr).decode()
        }]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit UI
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Resume Checker 💼")

input_text = st.text_area("📄 Paste Job Description", key="input")
uploaded_file = st.file_uploader("📁 Upload your Resume (PDF only)", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ PDF Uploaded Successfully")

submit1 = st.button("📄 Tell Me About the Resume")
submit3 = st.button("📊 Percentage Match")

# Gemini prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Evaluate the resume against the provided job description. Give me the percentage of match first, 
then list missing keywords, and finally provide final thoughts.
"""

# Handle button clicks
if submit1:
    if uploaded_file is not None and input_text:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt1)
        st.subheader("💬 Response:")
        st.write(response)
    else:
        st.warning("⚠️ Please upload a resume and enter a job description.")

elif submit3:
    if uploaded_file is not None and input_text:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt3)
        st.subheader("📈 Match Result:")
        st.write(response)
    else:
        st.warning("⚠️ Please upload a resume and enter a job description.")
