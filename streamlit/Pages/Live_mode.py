import streamlit as st
import os
import tempfile
from PIL import Image
import base64
import pandas as pd
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
all_results=[]
# if 'all_results' not in st.session_state:
#     st.session_state['all_results'] = []

def process_marking_key(reference_image_path):
    with st.spinner("Processing..."):
        reference_answers = reference_sheet(reference_image_path)
        marking_key={
            'index_numbers':0000000,
            'Answers':reference_answers
        }
        marking_key_df = pd.DataFrame([marking_key])
        st.session_state['reference_answers'] = reference_answers
        st.session_state['marking_key']=marking_key_df


def process_student_sheets(student_path):
    global all_results
    with st.spinner("Processing..."):
        index_numbers, student_answers,reference_image, answer_contours = student_sheet(student_path)
        all_results.append({
            "index_numbers": index_numbers,
            "student_answers": student_answers,
            "answer_contours": answer_contours,
            "image_paths": student_path
        })
        st.session_state['all_results']=all_results

if 'stage' not in st.session_state:
    st.session_state.stage=0

def set_state(i):
    st.session_state.stage=i

if st.session_state.stage==0:
    st.text_input("Course code:",key='course_code',on_change=set_state,args=[1])

if st.session_state.stage>=1:
    num_sheets = st.number_input("Number of questions", min_value=1, value=1, step=1, key='total_questions', on_change=set_state, args=[2])
    
if st.session_state.stage>=2:
    num_sheets = st.number_input("Number of Student Sheets to Scan", min_value=1,  step=1, key='total_sheets', on_change=set_state, args=[3])


if st.session_state.stage>=3:
    st.button("Scan marking key",key="button_button", help="Click to scan marking key sheet",on_click=set_state, args=[4])

if st.session_state.stage==4:
    with st.spinner("Processing..."):
        reference_image_path=scan_without_dialog(scanner_name = "HP Laser MFP 131 133 135-138")
        process_marking_key(reference_image_path)
        set_state(5)

if st.session_state.stage>=5:
    st.button("Scan student sheets", help="Click to start scanning",on_click=set_state,args=[6])

if st.session_state.stage>=6:
    scanned_images_path=[]
    scan_delay=10
    with st.spinner("Scanning in Progress..."):
        if 'total_sheets' in st.session_state:
            num_sheets=st.session_state['total_sheets']
        for _ in range(num_sheets):
            image_path = scan_without_dialog(scanner_name="HP Laser MFP 131 133 135-138")
            scanned_images_path.append(image_path)
            time.sleep(scan_delay)
        st.session_state['scanned_images_path']=scanned_images_path
        set_state(7)

if st.session_state.stage>=7:
    if 'scanned_images_path' in st.session_state:
        scanned_images_path=st.session_state['scanned_images_path']
    for i in scanned_images_path:
        process_student_sheets(i)
            
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
            else:
                display_keys=['index_numbers','student_answers']
                detected_results = [{key: result[key] for key in display_keys} for result in all_results]
                detected_results_df=pd.DataFrame(detected_results)
                if 'marking_key' in st.session_state:
                    marking_key_df=st.session_state['marking_key']
                df = pd.concat([marking_key_df, detected_results_df.rename(columns={'student_answers':'Answers'})], ignore_index=True)
                df = df.applymap(lambda x: str(x).replace(',', ''))
        st.dataframe(df) 
    set_state(8)

# st.success(f"Batch Processing Complete. Processed {num_sheets} Student Sheets.")

# if st.session_state.stage==8:
#     st.button('Grade',on_click=set_state(9))

if st.session_state.stage==8:
    if 'all_results' in st.session_state or 'reference_answers' in st.session_state:
        all_results=st.session_state['all_results']
        reference_answers=st.session_state['reference_answers'] 
    if  'total_questions' in st.session_state:
        total_questions=st.session_state['total_questions']

        df = score(reference_answers, all_results,total_questions)
        df = df.applymap(lambda x: str(x).replace(',', ''))
        with st.expander("View Results", expanded=False):
            st.dataframe(df)
            set_state(9)
        
if st.session_state.stage == 9:
#     set_state(0)
    st.button('Start Over', on_click=set_state, args=[0])