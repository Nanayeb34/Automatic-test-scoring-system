import streamlit as st
import os
import tempfile
from PIL import Image
import base64
import pandas as pd
import pyarrow as pa
import time
from scoring_system import scan_without_dialog, reference_sheet, student_sheet, score,show_warning_and_get_input

st.set_page_config(
    page_title="Upload Mode",
    page_icon="",
    layout="wide"
)

st.markdown(
    """
    <div style="display: flex; justify-content: center;">
        <h1>Upload Mode</h1>
    </div>
    </div>
    Instructions\n
    1. Upload Reference OMR sheet\n
    2. Upload folder containing student OMR sheets\n
    3. Click on 'Process sheets'\n
    4. View results afterwards\n
    """,
    unsafe_allow_html=True
)
# def show_warning_and_get_input(image_path, index_numbers,student_id):
#     if f"corrected_index_input_{student_id}" not in st.session_state:
#         st.session_state[f"corrected_index_input_{student_id}"]=[]
#         if len(str(index_numbers)) != 7:
#             st.warning("Number of index numbers is not equal to 7.", icon="⚠️")
#             corrected_index = st.text_input(
#                 "Enter correct index number (7 digits):",
#             )
#             # if corrected_index:
#             return corrected_index
# def show_warning_and_get_input(message, default_value):
#     """
#     Displays a warning message and gets input from the user.
#     """
#     st.write(message)
#     st.write("Please enter a value:")
#     input_value = st.text_input("", default_value)
#     return input_value
# new_index_numbers = show_warning_and_get_input('Enter new index numbers:', '').strip()
# st.write(new_index_numbers)
uploaded_reference = st.file_uploader("Upload Reference Sheet ", type=["jpg", "png", "jpeg"], key="reference_sheet")

# Add a button to upload the student sheet
uploaded_student = st.file_uploader("Upload Student Sheets", type=["jpg", "png", "jpeg"],accept_multiple_files=True, key="student_sheet")

# Process the reference and student sheets if uploaded
if uploaded_reference and uploaded_student:
    if st.button("Process Sheets",key="process_button", help="Click to process sheets"):
        # Show a spinner while processing
        with st.spinner("Processing..."):
            all_results = []

            with tempfile.NamedTemporaryFile(delete=False) as temp_ref:
                temp_ref.write(uploaded_reference.read())
                reference_path = temp_ref.name

            reference_answers = reference_sheet(reference_path)
            st.session_state['reference_answers'] = reference_answers
            os.remove(reference_path)

        
            for student_file in uploaded_student:
                # Generate a unique student_id based on hash and timestamp
                student_id = hash(str(time.time()))
                with tempfile.NamedTemporaryFile(delete=False) as temp_student:
                    temp_student.write(student_file.read())
                    student_path = temp_student.name

                index_numbers, student_answers, reference_image, answer_contours = student_sheet(student_path)
                new_index_numbers=show_warning_and_get_input(student_path, index_numbers,student_id)
                st.session_state['new_index_numbers'] = new_index_numbers  # This updates session state

                all_results.append({
                    "index_numbers": new_index_numbers,
                    "student_answers": student_answers,
                    "answer_contours": answer_contours,
                    "image_paths": student_path
                })
                    

                    # os.remove(student_path)


            st.session_state['all_results']=all_results


# # Check if 'all_results' exists in st.session_state
if 'all_results' in st.session_state:
    all_results=st.session_state['all_results']

    reference_answers=st.session_state['reference_answers'] 



    df = score(reference_answers, all_results)
    # Format the 'Index No' column to remove commas
    df['Index No'] = df['Index No'].apply(lambda x: int(str(x).replace(',', '')) if x is not None and str(x).replace(',', '').isdigit() else x)
    df['Score'] = df['Score'].apply(int)
    # Convert the 'Index No' column to strings to prevent automatic formatting
    df['Index No'] = df['Index No'].astype(str)
    with st.expander("View Results", expanded=False):
        if 'all_results' in st.session_state:
            # table = pa.Table.from_pandas(df)
            st.dataframe(df)