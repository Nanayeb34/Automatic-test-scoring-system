import streamlit as st
import os
import tempfile
from PIL import Image
import base64
import pyarrow as pa
import time
from scoring_system import scan_without_dialog, reference_sheet, student_sheet, score
import logging
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

# def show_warning_and_get_input(index_numbers,student_id):
#     if f"corrected_index_input_{student_id}" not in st.session_state:
#         st.session_state[f"corrected_index_input_{student_id}"]=[]
#     if len(str(index_numbers)) != 7:
#         st.warning("Number of index numbers is not equal to 7.", icon="⚠️")
        
#         # Display the reference image using matplotlib
#         # pil_image=Image.open(image_path)
#         # st.image(pil_image, use_column_width=True, caption="Uploaded Image")

#         # Display current index numbers
#         # st.write(f"Current index numbers: {index_numbers}")
#         # stored_corrected_index = st.session_state.get(f"stored_corrected_index_{student_id}")
#         # Get user input for the corrected index number
#         corrected_index = st.text_input(
#             "Enter correct index number (7 digits):",
#             value=index_numbers
#             # format='%d',
#             # key=f"corrected_index_input_{student_id}"   # Using a key to track the session state of corrected_index
#         )
        
        # Store the new value in a separate session state variable
        # st.session_state[f"stored_corrected_index_{student_id}"] = corrected_index
        # new_results=corrected_index
        # if corrected_index:
        #     st.session_state[f"corrected_index_input_{student_id}"]=new_results
            # return corrected_index
#         if f"corrected_index_input_{student_id}" in st.session_state:
#             return corrected_index
# hi=show_warning_and_get_input(index_numbers=4567,student_id=789)
# st.write(hi)
# # def trial():
# corrected_index = st.text_input(
#     "Enter correct index number (7 digits):",
#     value=234,
#     key="ama"
# )
# yaw=corrected_index
# st.write(yaw)
#     return corrected_index
# returned_value=trial()
# st.write("Returned value:", returned_value)
# Configure logging to display debug messages
# logging.basicConfig(level=logging.DEBUG)

# Provide the path to the image
# image_path = r'C:\Users\Sam\AppData\Local\Temp\tmpp9xb9m8s.jpg'

# # Display the image
# try:
#     pil_image = Image.open(image_path)
#     st.image(pil_image, use_column_width=True)
# except Exception as e:
#     logging.error(f"An error occurred: {e}")
# Later in your code, after the user has interacted with the widget, you can access the value like this
# if corrected_index:
#     # Use the value entered by the user
#     st.write("User entered corrected index:", corrected_index)


                # # Create a list of file names for the dropdown menu
                # file_names = [os.path.basename(result["image_paths"]) for result in all_results]

                # # Display the dropdown menu
                # selected_file = st.sidebar.selectbox("Select Image File", file_names)

                # # Find the index of the selected file in the list of file names
                # selected_index = file_names.index(selected_file)

                # # Display the corresponding image
                # img = Image.open(all_results[selected_index]["image_paths"])
                # st.image(img, caption="Uploaded Image", use_column_width=True)
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




