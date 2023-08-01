import streamlit as st
import os
import tempfile
from PIL import Image
import base64
import pyarrow as pa
from scoring_system import reference_sheet, student_sheet, score

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
        <p style="text-align: center; font-size: 24px;">
            This is an automatic test test scoring system developed by students of KNUST.
        </p>
    </div>
    <div style="display: flex; justify-content: center;">
        <p style="text-align: center; font-size: 20px; font-weight: bold;">
            Ready to scan your answer sheets? Let's dive in
        </p>
    </div>
    Instructions\n
    1. Upload Reference OMR sheet\n
    2. Upload folder containing student OMR sheets\n
    3. Click on 'Process sheets'\n
    4. View results afterwards\n
    """,
    unsafe_allow_html=True
)



# Add a button to upload the reference sheet
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

                os.remove(student_path)

            st.session_state['all_results'] = all_results
        # Change the color of the button to indicate it's done
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
# Check if 'all_results' exists in st.session_state
if 'all_results' in st.session_state:
    all_results = st.session_state['all_results']
    reference_answers=st.session_state['reference_answers'] 


    df = score(reference_answers, all_results)
    with st.expander("View Results", expanded=False):
        if 'all_results' in st.session_state:
            table = pa.Table.from_pandas(df)
            st.dataframe(table)
# else:
#     st.write("Please upload and process the reference and student sheets first.")

# if st.sidebar.button('View Results'):
#     st.set_page_config(page_title="Test Scoring System - Results", layout="wide")

#     # Display the DataFrame on a separate page
#     st.write("## Results")
#     st.dataframe(df)

#     # Add a back arrow button to return to the home page
#     if st.button("⬅️ Back"):
#         st.set_page_config(page_title="Test Scoring System", layout="wide")
# Create a function for each menu option
# def option1():
#     st.write("This is Option 1")

# def option2():
#     st.write("This is Option 2")

# def option3():
#     st.write("This is Option 3")

# # Create the menu in the sidebar
# menu_selection = st.sidebar.button("Graded sheets")

# # Call the corresponding function based on the selected option
# if menu_selection == "Option 1":
#     option1()
# elif menu_selection == "Option 2":
#     option2()
# elif menu_selection == "Option 3":
#     option3()






