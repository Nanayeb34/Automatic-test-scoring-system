import streamlit as st
import os
import tempfile
from PIL import Image
import base64
import pyarrow as pa
from scoring_system import scan_without_dialog, reference_sheet, student_sheet, score

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
uploaded_reference = st.file_uploader("Upload Reference Sheet ", type=["jpg", "png", "jpeg"], key="reference")

# Add a button to upload the student sheet
uploaded_student = st.file_uploader("Upload Student Sheets", type=["jpg", "png", "jpeg"],accept_multiple_files=True, key="student")

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
                with tempfile.NamedTemporaryFile(delete=False) as temp_student:
                    temp_student.write(student_file.read())
                    student_path = temp_student.name

                index_numbers, student_answers, reference_image, answer_contours = student_sheet(student_path)

                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_ref:
                    reference_image.save(temp_ref.name)
                    all_results.append({"index_numbers": index_numbers, "student_answers": student_answers, "answer_contours": answer_contours, "image_paths": temp_ref.name})
                
                # st.experimental_set_query_params(processed="true")
                os.remove(student_path)


            st.session_state['all_results'] = all_results


# Check if 'all_results' exists in st.session_state
if 'all_results' in st.session_state:
    all_results = st.session_state['all_results']
    reference_answers=st.session_state['reference_answers'] 


    df = score(reference_answers, all_results)
    with st.expander("View Results", expanded=False):
        if 'all_results' in st.session_state:
            table = pa.Table.from_pandas(df)
            st.dataframe(table)