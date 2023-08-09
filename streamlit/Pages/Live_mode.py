import streamlit as st
import os
import tempfile
from PIL import Image
import base64
import pyarrow as pa
import time
from scoring_system import scan_without_dialog, reference_sheet, student_sheet, score

st.set_page_config(
    page_title="Live Mode",
    page_icon="",
    layout="wide"
)

st.markdown(
    """
    <div style="display: flex; justify-content: center;">
        <h1>Live Mode</h1>
    </div>
    </div>
    Instructions\n
    1. Scan marking key\n
    2. Scan student sheets\n
    3. Click on 'Process sheets'\n
    4. View results afterwards\n
    """,
    unsafe_allow_html=True
)
# Specify the number of student sheets to scan
num_sheets = st.number_input("Number of Student Sheets to Scan", min_value=1, value=1, step=1)
# Specify the delay between scans (in seconds)
scan_delay = st.number_input("Delay Between Scans (seconds)", min_value=0, value=2, step=1)
# Initialize all_results if not present
if 'all_results' not in st.session_state:
    st.session_state['all_results'] = []
if st.button("Scan marking key",key="button_button", help="Click to scan marking key sheet"):
    with st.spinner("Processing..."):
        image_path=scan_without_dialog(scanner_name = "HP Laser MFP 131 133 135-138")
        reference_answers = reference_sheet(image_path)
        st.session_state['reference_answers'] = reference_answers

if st.button("Start Batch Processing", help="Click to start batch processing"):
    with st.spinner("Batch Processing in Progress..."):
        for _ in range(num_sheets):
            image_path = scan_without_dialog(scanner_name="HP Laser MFP 131 133 135-138")
            index_numbers, student_answers, reference_image, answer_contours = student_sheet(image_path)

            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_ref:
                reference_image.save(temp_ref.name)

            # Append the current result to the list of all results
            all_results = st.session_state['all_results']
            all_results.append({
                "index_numbers": index_numbers,
                "student_answers": student_answers,
                "answer_contours": answer_contours,
                "image_paths": temp_ref.name
            })
            st.session_state['all_results'] = all_results  # Save updated all_results
            # Introduce a delay between scans
            time.sleep(scan_delay)
st.success(f"Batch Processing Complete. Processed {num_sheets} Student Sheets.")

# Display combined results
if 'all_results' in st.session_state:
    all_results = st.session_state['all_results']
    reference_answers = st.session_state['reference_answers']

    df = score(reference_answers, all_results)
    st.write(df)
    with st.expander("View Results", expanded=False):
        if 'all_results' in st.session_state:
            table = pa.Table.from_pandas(df)
            st.dataframe(table)