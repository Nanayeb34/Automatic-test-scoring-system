import streamlit as st
import os
import tempfile
from PIL import Image
import base64
import time
from scoring_system import student_sheet
import pandas as pd
favicon_path = os.path.join(os.getcwd(),'assets','black_favicon.ico')
favicon=Image.open(favicon_path)
st.set_page_config(
    page_title="Test Scoring System",
    page_icon=favicon,
    layout="wide"
)
# Add a custom image as the background using CSS
# background_image_url = 'https://images.app.goo.gl/LFCobouKtT7oZ7Qv7'  # Replace 'path_to_your_custom_image.jpg' with the path to your image
# st.markdown(
#     f"""
#     <style>
#     .reportview-container {{
#         background: url('{background_image_url}') no-repeat center center fixed;
#         background-size: cover;
#     }}
#     </style>
#     """,
#     unsafe_allow_html=True
# )


# Center the heading text using HTML and CSS
st.markdown(
    """
    <div style="display: flex; justify-content: center;">
        <h1>Automatic Test Scoring System ✍️</h1>
    </div>
    <div style="display: flex; justify-content: center;">
        <p style="text-align: center; font-size: 24px;">
             Hello! Welcome👋
        </p>
    </div>
    <div style="display: flex; justify-content: center;">
        <p style="text-align: justify; font-size: 24px;">
            Explore the Automatic Test Scoring System developed by KNUST students.
        </p>
    </div>
    <div style="display: flex; justify-content: justify;">
        <p style="text-align: justify; font-size: 20px;">
            The app supports Live Mode and Upload Mode
        </p>
    </div>
    <div style="display: flex; justify-content: justify;">
        <ul style="text-align: justify; font-size: 20px;">
            <li>Live Mode: Scan and grade sheets in real-time</li>
            <li>Upload Mode: Grade pre-scanned sheets</li>
        </ul>
    </div>
    <div style="display: flex; justify-content: center;">
        <p style="text-align: center; font-size: 20px; font-weight: bold;">
            👈 Select a mode from the dropdown on the left to get started.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    /* Add custom styles to the "Process Sheets" button when hovered */
    .stButton button:hover {
        background-color: green !important;
        border-color: green !important;
        color: white !important;
    }
    </style>

    """,
    unsafe_allow_html=True
)




