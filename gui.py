import streamlit as st
# from streamlit_session_state import session_state
import os
import tempfile
from PIL import Image
from scoring_system import reference_sheet, student_sheet,score

st.set_page_config(
    page_title="Test Scoring System",
    page_icon=":writing hand:",
    layout="wide"
)


# Outputs: value
# Define a function to get the session state
def get_session_state():
    return st.session_state


st.write("# Automatic Test Scoring System 👋")

st.markdown(
    """
    ### "Can an AI win Ghana’s National Science and Maths Quiz?". 
    
    This is the question posed by the NSMQ AI Grand Challenge 
    which is an AI Grand Challenge for Education using Ghana’s National 
    Science and Maths Quiz competition (NSMQ) as a case study. 
    
    The goal of nsmqai is build an AI to compete live in the NSMQ competition 
    and win — performing better than the best contestants in all rounds and stages of the competition.

    **👈 Select a demo from the dropdown on the left** to see some examples
    of what NSMQ AI can do!
    """
)
@st.cache
def load_image(image_path):
    # Load the image from disk or compute it
    reference_image = Image.open(image_path)
    return reference_image

# Add a button to upload the reference sheet
uploaded_reference = st.file_uploader("Upload Reference Sheet", type=["jpg", "png", "jpeg"])

# Add a button to upload the student sheet

uploaded_student = st.file_uploader("Upload Student Sheet", accept_multiple_files=True)

if uploaded_reference and st.button("Process Reference Sheet"):
    # Save the uploaded reference sheet temporarily
    with tempfile.NamedTemporaryFile(delete=False) as temp_ref:
        temp_ref.write(uploaded_reference.read())
        reference_path = temp_ref.name

    # reference_image = Image.open(uploaded_reference)
    # st.image(reference_image, caption='Reference Sheet', use_column_width=True)
    reference_answers = reference_sheet(reference_path)
    st.session_state['reference_answers'] = reference_answers
    # st.write("Reference Sheet Answers:", reference_answers)

    # Remove the temporary file after processing
    os.remove(reference_path)

elif 'reference_answers' in st.session_state:
    reference_answers = st.session_state['reference_answers']
    # st.write("Reference Sheet Answers:", reference_answers)





if uploaded_student and st.button("Process Student Sheet"):
    all_results = []
    # reference_image_paths = []  # List to store all processed reference images

    for file in uploaded_student:
        # Save the uploaded student sheet temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_student:
            temp_student.write(file.read())
            student_path = temp_student.name

        # student_image = Image.open(file)
        # st.image(student_image, caption='Student Sheet', use_column_width=True)
        index_numbers, student_answers, reference_image, answer_contours = student_sheet(student_path)
        # all_results.append({"index_numbers": index_numbers, "student_answers": student_answers, "answer_contours": answer_contours})

        with tempfile.NamedTemporaryFile(suffix=".jpg",delete=False) as temp_ref:
            reference_image.save(temp_ref.name)
            all_results.append({"index_numbers": index_numbers, "student_answers": student_answers, "answer_contours": answer_contours,"image_paths":temp_ref.name})
            # reference_image_paths.append(temp_ref.name)
            

        # Remove the temporary file after processing
        os.remove(student_path)

    # Store the values in session state after processing all student sheets
    # st.session_state['reference_image_paths'] = reference_image_paths  
    st.session_state['all_results'] = all_results


# Check if 'reference' exists in st.session_state
if 'all_results' in st.session_state:
    # Retrieve the value of 'reference' from st.session_state
    all_results = st.session_state['all_results']

    # Call the function and pass the data as arguments
    if st.button('Grade'):
        df = score(reference_answers, all_results)

        # Display the results DataFrame
        st.dataframe(df)
else:
    # 'reference' is not yet defined, display a message or perform a specific action
    st.write("Please upload and process the student sheet first.")

