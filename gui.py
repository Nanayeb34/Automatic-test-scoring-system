import streamlit as st
import os
import tempfile
from PIL import Image
import base64
from scoring_system import reference_sheet, student_sheet, score

im = Image.open(r"C:\Users\Sam\Desktop\project\ocr_code\Automatic-test-scoring-system\assets\favicon.ico")
st.set_page_config(
    page_title="Test Scoring System",
    page_icon=im,
    layout="wide"
)
# Add a custom image as the background using CSS
background_image_url = 'https://images.app.goo.gl/LFCobouKtT7oZ7Qv7'  # Replace 'path_to_your_custom_image.jpg' with the path to your image
st.markdown(
    f"""
    <style>
    .reportview-container {{
        background: url('{background_image_url}') no-repeat center center fixed;
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    body {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

set_png_as_page_bg(r'https://images.app.goo.gl/LFCobouKtT7oZ7Qv7')

# Center the heading
# Center the heading text using HTML and CSS
st.markdown(
    """
    <div style="display: flex; justify-content: center;">
        <h1>Automatic Test Scoring System ✍️</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Center the other text as well
st.markdown(
    """
    <div style="display: flex; justify-content: center;">
        <p style="text-align: center; font-size: 24px;">
             Hello! Welcome👋
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="display: flex; justify-content: center;">
        <p style="text-align: center; font-size: 24px;">
            This is an automatic test test scoring system developed by students of KNUST.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="display: flex; justify-content: center;">
        <p style="text-align: center; font-size: 20px; font-weight: bold;">
            Ready to scan your answer sheets? Let's dive in
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# st.markdown(
#     """
#     ### "Hello! Welcome👋". 
    
#     This is an automatic test test scoring system developed by students of KNUST.

#     **Ready to scan your answer sheets? Let's dive in**
#     """
# )

# Add a button to upload the reference sheet
uploaded_reference = st.file_uploader("Upload Reference Sheet ('.jpg', '.png', '.jpeg')", type=["jpg", "png", "jpeg"], key="reference")

# Add a button to upload the student sheet
uploaded_student = st.file_uploader("Upload Student Sheet ('.jpg', '.png', '.jpeg')", accept_multiple_files=True, key="student")

# Process the reference and student sheets if uploaded
if uploaded_reference and uploaded_student and st.button("Process Sheets"):
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

# Check if 'all_results' exists in st.session_state
if 'all_results' in st.session_state:
    all_results = st.session_state['all_results']
    reference_answers=st.session_state['reference_answers'] 

    if st.button('Grade'):
        df = score(reference_answers, all_results)

        # Display the results DataFrame
        st.dataframe(df)
else:
    st.write("Please upload and process the reference and student sheets first.")
