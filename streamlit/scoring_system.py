import cv2
import numpy as np
import pandas as pd
from PIL import Image
import tempfile
import os
import win32com.client as wia
import pythoncom
import matplotlib.pyplot as plt
import time
import random
import string
import io
import streamlit as st


def create_temp_folder():
    temp_dir = 'scanned_sheets'
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir
def generate_unique_filename(folder, base_name):
    timestamp = time.strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    unique_name = f"{base_name}_{timestamp}_{random_suffix}"
    return os.path.join(folder, f"{unique_name}.jpg")
def scan_without_dialog(scanner_name):
    pythoncom.CoInitialize()
    try:
        # Create a WIA device manager
        device_manager = wia.Dispatch("WIA.DeviceManager")

        # Get the collection of available scanner devices
        device_infos = device_manager.DeviceInfos

        # Find the scanner with the specified name
        scanner = None
        for device_info in device_infos:
            if device_info.Properties("Name").Value == scanner_name:
                scanner = device_info.Connect()
                break

        if scanner is None:
            print(f"Scanner '{scanner_name}' not found.")
            return

        # Set the desired scanning parameters (e.g., DPI, color mode, format)
        # For example, set the scan resolution to 300 DPI and use color scanning
        properties = scanner.Items[1].Properties
        for prop in properties:
            if prop.Name == '6146':  # 6146 is the property ID for scan resolution (DPI)
                prop.Value = 300
            elif prop.Name == '6147':  # 6147 is the property ID for color mode (1: Color, 2: Grayscale, 4: Black and White)
                prop.Value = 1

        # Perform the scan and retrieve the scanned image
        image = scanner.Items[1].Transfer()
        temp_dir = create_temp_folder()
        
        # Save the scanned image to a file inside the temporary folder
        # Generate a unique image file path
        image_base_name = "sheet"
        image_path = generate_unique_filename(temp_dir, image_base_name)
        image.SaveFile(image_path)

        pythoncom.CoUninitialize()
        return image_path
    except Exception as e:
        # Handle exceptions, print an error message, etc.
        print("Error:", e)
        pythoncom.CoUninitialize()
        return None
# if __name__ == "__main__":
#     # Replace 'Scanner Name' with the name of your desired scanner
#     scanner_name = "HP Laser MFP 131 133 135-138"
#     scan_without_dialog(scanner_name)

def preprocess_image(image_path):
    # read image
    reference = cv2.imread(image_path)
    # Resize image
    reference = cv2.resize(reference, (2480, 3507))
    
    # Convert to grayscale
    gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
    
    # Perform median filtering
    median = cv2.medianBlur(gray, 5)
    
    # Apply adaptive histogram equalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    equalized = clahe.apply(median)
    
    
    return reference, equalized


def index_preprocess(image_path):
    reference=cv2.imread(image_path)
    reference=cv2.resize(reference, (2480,3507))
    gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
    normalized=normalize_brightness(gray)
    median = cv2.medianBlur(normalized, 5)

    return median

def normalize_brightness(image):
    # Compute the image's pixel distribution
    hist, bins = np.histogram(image.flatten(), 256, [0, 256])

    # Determine the desired minimum and maximum pixel values based on the pixel distribution
    cdf = hist.cumsum()
    cdf_normalized = cdf * hist.max() / cdf.max()
    desired_min = bins[np.argmax(cdf_normalized > 0.01 * cdf_normalized.max())]
    desired_max = bins[np.argmax(cdf_normalized > 0.99 * cdf_normalized.max())]

    # Normalize the brightness to the desired range of pixel values
    normalized = cv2.normalize(image, None, alpha=desired_min, beta=desired_max, norm_type=cv2.NORM_MINMAX)
    
    return normalized

def remove_noise(image):
    # Apply morphological operations to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened_image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    
    return opened_image

def find_contours(image, median=None):
    # Threshold image
    thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)   
    
    if median is not None:
        # Adaptive threshold to identify index numbers
        adap_thresh = cv2.adaptiveThreshold(median, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 5)
        index_contours, _ = cv2.findContours(adap_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours, index_contours, adap_thresh
    else:
        return contours

def find_largest_contour(contours):
    largest_contour = max(contours, key=cv2.contourArea)
    return largest_contour

def filter_contours(contours, largest_contour,normalized):
    filtered_contours = []
    for contour in contours:
        [x, y, w, h] = cv2.boundingRect(contour)
        if y > largest_contour[0][0][1] and 1.5 <= w / h <= 2.5:
            roi = normalized[y:y+h, x:x+w]
            avg_intensity = np.mean(roi)
        #     # Define threshold for minimum intensity
            min_intensity_thresh = 150
            max_intensity_thresh=200
        #     # # If intensity or texture is below threshold, discard contour
            if min_intensity_thresh < avg_intensity < max_intensity_thresh:
    
                area = cv2.contourArea(contour)
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                if hull_area > 0:
                    solidity = float(area)/hull_area
                    if solidity > 0.5 or solidity==0.5:
                        epsilon = cv2.arcLength(contour,True)
                        if epsilon >100:
                            filtered_contours.append(contour)
    return filtered_contours

def sort_index_contours(index_contours, adap_thresh, reference):
    index_sorted_contours = []

    index_contours = sorted(index_contours, key=cv2.contourArea, reverse=True)
    third_largest_contour = index_contours[2] if len(index_contours) >= 3 else None

    if third_largest_contour is not None:
        [x, y, w, h] = cv2.boundingRect(third_largest_contour)
        index_roi = adap_thresh[y:y+h, x:x+w]
        index_rgb=reference[y:y+h, x:x+w]
        sorted_contours, _ = cv2.findContours(index_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        index_sorted_contours = sorted(sorted_contours, key=lambda c: (cv2.boundingRect(c)[0], cv2.boundingRect(c)[1]))

    return index_sorted_contours,index_rgb

def filter_index_contours(index_sorted_contours,normalized,index_rgb):
    index_numbers=[]
    for contour in index_sorted_contours:
        [x, y, w, h] = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        if hull_area > 0:
            solidity = float(area)/hull_area
            if solidity > 0.5:
                epsilon = cv2.arcLength(contour,True)
                if epsilon >100:
                    roi = normalized[y:y+h, x:x+w]
                    avg_intensity = np.mean(roi)
                    min_intensity_thresh = 100
                    max_intensity_thresh=280
                    if min_intensity_thresh < avg_intensity < max_intensity_thresh and 1.5 <= w / h <= 2.5:
                            cv2.rectangle(index_rgb, (x, y), (x+w, y+h), (0, 255, 0), 5)
                            if 150<y<190:
                                index_numbers.append('0')
                            elif 195<y<225:
                                index_numbers.append('1')
                            elif 230<y<265:
                                index_numbers.append('2')
                            elif 270<y<300:
                                index_numbers.append('3')
                            elif 305<y<340:
                                index_numbers.append('4')
                            elif 340<y<375:
                                index_numbers.append('5')
                            elif 380<y<415:
                                index_numbers.append('6')
                            elif 420<y<450:
                                index_numbers.append('7')  
                            elif 455<y<490:
                                index_numbers.append('8')
                            elif 495<y<530:
                                index_numbers.append('9')   
    
    # Convert the list of integers to a single integer
    # index_numbers = int(''.join(map(str, index_numbers)))  
    index_numbers = int(''.join(index_numbers))
    # if len(str(index_numbers)) != 7:
    #     # unique_key = f'index_{id(index_numbers)}'
        # index_numbers = show_warning_and_get_input(reference, index_numbers)
    # print(index_numbers)
    return index_numbers 


def show_warning_and_get_input(image_path, index_numbers):
    # if f"corrected_index_input_{student_id}" not in st.session_state:
    #     st.session_state[f"corrected_index_input_{student_id}"]=[]
    if len(str(index_numbers)) != 7:
        st.warning("Number of index numbers is not equal to 7.", icon="⚠️")
        
        # Display the reference image using matplotlib
        # pil_image=Image.open(image_path)
        # st.image(pil_image, use_column_width=True, caption="Uploaded Image")


def group_contours(contours):
    # Define the ranges for grouping
    range1 = (200, 550)
    range2 = (600, 1000)
    range3 = (1050, 1400)

    # Group the contours based on x-value ranges
    group1 = sorted([c for c in contours if range1[0] <= cv2.boundingRect(c)[0] <= range1[1]], key=lambda c: cv2.boundingRect(c)[1])
    group2 = sorted([c for c in contours if range2[0] <= cv2.boundingRect(c)[0] <= range2[1]], key=lambda c: cv2.boundingRect(c)[1])
    group3 = sorted([c for c in contours if range3[0] <= cv2.boundingRect(c)[0] <= range3[1]], key=lambda c: cv2.boundingRect(c)[1])

    concatenated_contours = group1 + group2 + group3
    return concatenated_contours

def process_contour(x, y, w, h, index, reference, student_answers, answer_contours=None):
    answer = None  # Variable to store the answer

    if (220 <= x <= 290) or (660 <= x <= 710) or (1084 <= x <= 1130):
        answer = f'{index+1}.A'
    elif (300 <= x <= 355) or (720 <= x <= 770) or (1140 <= x <= 1190):
        answer = f'{index+1}.B'
    elif (357 <= x <= 410) or (780 <= x <= 830) or (1200 <= x <= 1250):
        answer = f'{index+1}.C'
    elif (415 <= x <= 470) or (841 <= x <= 895) or (1260 <= x <= 1310):
        answer = f'{index+1}.D'
    elif (480 <= x <= 530) or (900 <= x <= 955) or (1320 <= x <= 1370):
        answer = f'{index+1}.E'

    if answer is not None:
        student_answers.append(answer)
        if answer_contours is not None:
            answer_contours.append([x, y, w, h])
            cv2.rectangle(reference, (x, y), (x+w, y+h), (0, 255, 0), 5)
        else:
            cv2.rectangle(reference, (x, y), (x+w, y+h), (0, 255, 0), 5)
def student_sheet(image_path):
    reference, equalized = preprocess_image(image_path)
    median = index_preprocess(image_path)
    normalized = normalize_brightness(equalized)
    opened_image = remove_noise(normalized)
    contours, index_contours, adap_thresh = find_contours(opened_image, median)
    index_sorted_contours, index_rgb = sort_index_contours(index_contours, adap_thresh, reference)
    index_numbers = filter_index_contours(index_sorted_contours, normalized, index_rgb)
    largest_contour = find_largest_contour(contours)
    filtered_contours = filter_contours(contours, largest_contour, normalized)
    concatenated_contours = group_contours(filtered_contours)
    student_answers = []
    answer_contours = []
    for index, contour in enumerate(concatenated_contours):
        [x, y, w, h] = cv2.boundingRect(contour)
        process_contour(x, y, w, h, index, reference, student_answers, answer_contours)
    return index_numbers, student_answers, reference, answer_contours




def reference_sheet(image_path):
    reference, equalized = preprocess_image(image_path)
    normalized = normalize_brightness(equalized)
    opened_image = remove_noise(normalized)
    contours= find_contours(opened_image)
    largest_contour=find_largest_contour(contours)
    filtered_contours=filter_contours(contours,largest_contour,normalized)
    concatenated_contours = group_contours(filtered_contours)
    reference_answers = []
    for index, contour in enumerate(concatenated_contours):
        [x, y, w, h] = cv2.boundingRect(contour)
        process_contour(x,y,w,h, index, reference, reference_answers)
    # cv2.imwrite('reference.jpg',reference)
    return reference_answers




def score(reference_answers, all_results,total_questions):
    data = []  # List to hold the data for the DataFrame

    for i, result in enumerate(all_results):
        reference = cv2.imread(all_results[i]['image_paths'])
        score = 0
        for value_a in reference_answers:
            correct = False
            for value_b in all_results[i]['student_answers']:
                if value_a == value_b:
                    score += 1
                    correct = True
                    break
            
            answer_contours = all_results[i]['answer_contours']
            if correct:
                cv2.rectangle(reference, (answer_contours[i][0], answer_contours[i][1]), (answer_contours[i][0] + answer_contours[i][2], answer_contours[i][1] + answer_contours[i][3]), (0, 255, 0), 2)
            else:
                cv2.rectangle(reference, (answer_contours[i][0], answer_contours[i][1]), (answer_contours[i][0] + answer_contours[i][2], answer_contours[i][1] + answer_contours[i][3]), (255, 0, 0), 2)

        new_index_numbers = all_results[i]['index_numbers']
        scores = score  # The corrected score value for this iteration

        # Append the data for this iteration to the list
        data.append({'Index No': new_index_numbers, 'Score': f"{scores}/{total_questions}"})

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)

    return df

