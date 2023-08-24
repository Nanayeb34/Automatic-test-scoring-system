import streamlit as st
import os
import tempfile
from PIL import Image
import base64
import pandas as pd
import time
import sys
# Add the parent directory to the Python path
import sys
import os


from scoring_system import student_sheet,reference_sheet,score,show_warning_and_get_input

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

all_results=[]

def process_marking_key():
    with st.spinner("Processing..."):
        uploaded_reference=st.session_state['upload_reference']
        with tempfile.NamedTemporaryFile(delete=False) as temp_ref:
            temp_ref.write(uploaded_reference.read())
            reference_path = temp_ref.name

        reference_answers = reference_sheet(reference_path)
        marking_key={
            'index_numbers':0000000,
            'Answers':reference_answers
        }
        marking_key_df = pd.DataFrame([marking_key])
        st.session_state['reference_answers'] = reference_answers
        st.session_state['marking_key']=marking_key_df
        set_state(3)

def process_student_sheets(student_path):
    # global all_results
    with st.spinner("Processing..."):

        index_numbers, student_answers,reference_image, answer_contours = student_sheet(student_path)
        all_results.append({
            "index_numbers": index_numbers,
            "student_answers": student_answers,
            "answer_contours": answer_contours,
            "image_paths": student_path
        })

        st.session_state['all_results']=all_results
        # set_state(3)

def Grade_sheets():
    if 'all_results' in st.session_state or 'reference_answers' in st.session_state:
        all_results=st.session_state['all_results']
        reference_answers=st.session_state['reference_answers'] 
    if  'total_questions' in st.session_state:
        total_questions=st.session_state['total_questions']

        df = score(reference_answers, all_results,total_questions)
        df = df.applymap(lambda x: str(x).replace(',', ''))
        st.session_state['dataframe']=df
        set_state(6)
        # with st.expander("View Results", expanded=False):
        #     if 'all_results' in st.session_state:
        #         st.dataframe(df)

if 'stage' not in st.session_state:
    st.session_state.stage=0

def set_state(i):
    st.session_state.stage=i

if st.session_state.stage==0:
    st.text_input("Course code:",key='course_code',on_change=set_state,args=[1])
    
if st.session_state.stage>=1:
    num_sheets = st.number_input("Number of questions", min_value=1, value=1, step=1, key='total_questions', on_change=set_state, args=[2])

if st.session_state.stage >=2:
    uploaded_reference = st.file_uploader("Upload Reference Sheet ", type=["jpg", "png", "jpeg"], on_change=process_marking_key, key='upload_reference')
    
if st.session_state.stage>=3:    
    uploaded_student = st.file_uploader("Upload Student Sheets", type=["jpg", "png", "jpeg"],accept_multiple_files=True, key='upload_student',on_change=set_state, args=[4])
    

if st.session_state.stage >= 4:
    if 'upload_student' in st.session_state:
        uploaded_sheets=st.session_state['upload_student']
    for i in uploaded_sheets:
        with tempfile.NamedTemporaryFile(delete=False) as temp_student:
            temp_student.write(i.read())
            student_path = temp_student.name
        process_student_sheets(student_path)

        if 'all_results' in st.session_state:
            all_results=st.session_state['all_results']
            index_number=all_results[-1]['index_numbers']
            if len(str(index_number))!= 7:
                st.warning("Invalid Index Number:", icon="⚠️")
                pil_image=Image.open(all_results[-1]['image_paths'])
                st.image(pil_image, use_column_width=True, caption="Uploaded Image")
                new_index_input = st.text_input("Enter a valid index number:",value=index_number, key=f'index_number_{i}')
                all_results[-1]['index_numbers']=st.session_state[f'index_number_{i}']
                display_keys=['index_numbers','student_answers']
                detected_results = [{key: result[key] for key in display_keys} for result in all_results]
                detected_results_df=pd.DataFrame(detected_results)
                if 'marking_key' in st.session_state:
                    marking_key_df=st.session_state['marking_key']
                df = pd.concat([marking_key_df, detected_results_df.rename(columns={'student_answers':'Answers'})], ignore_index=True)
                df = df.applymap(lambda x: str(x).replace(',', ''))
                st.dataframe(df) 
            else:
                display_keys=['index_numbers','student_answers']
                detected_results = [{key: result[key] for key in display_keys} for result in all_results]
                detected_results_df=pd.DataFrame(detected_results)
                if 'marking_key' in st.session_state:
                    marking_key_df=st.session_state['marking_key']
                df = pd.concat([marking_key_df, detected_results_df.rename(columns={'student_answers':'Answers'})], ignore_index=True)
                df = df.applymap(lambda x: str(x).replace(',', ''))
                st.dataframe(df)  
    set_state(5)

# if st.session_state.stage==5:
#     st.button('Grade',on_click=set_state(6))
# if st.session_state.stage==6:
#     if 'dataframe' in st.session_state:
#         df=st.session_state['dataframe']
#     with st.expander("View Results", expanded=False):
#         st.dataframe(df)
if st.session_state.stage==5:
    if 'all_results' in st.session_state or 'reference_answers' in st.session_state:
        all_results=st.session_state['all_results']
        reference_answers=st.session_state['reference_answers'] 
    if  'total_questions' in st.session_state:
        total_questions=st.session_state['total_questions']
        df = score(reference_answers, all_results,total_questions)
        df = df.applymap(lambda x: str(x).replace(',', ''))
        with st.expander("View Results", expanded=False):
            # if 'all_results' in st.session_state:
            st.dataframe(df)
            set_state(7)

if st.session_state.stage == 7:
#     set_state(0)
    st.button('Start Over', on_click=set_state, args=[0])



