import cv2
import numpy as np
import pandas as pd
from PIL import Image
import tempfile

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
    
    return reference,equalized
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
            min_intensity_thresh = 90
            max_intensity_thresh=160
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
    index_numbers = int(''.join(map(str, index_numbers)))   
    return index_numbers
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

    reference,equalized= preprocess_image(image_path)
    median=index_preprocess(image_path)
    normalized = normalize_brightness(equalized)
    opened_image = remove_noise(normalized)
    contours,index_contours,adap_thresh = find_contours(opened_image,median)
    index_sorted_contours,index_rgb=sort_index_contours(index_contours,adap_thresh,reference)
    index_numbers=filter_index_contours(index_sorted_contours,normalized,index_rgb)
    largest_contour=find_largest_contour(contours)
    filtered_contours=filter_contours(contours,largest_contour,normalized)
    concatenated_contours = group_contours(filtered_contours)

    student_answers = []
    answer_contours=[]
    # Iterate over the contours
    for index, contour in enumerate(concatenated_contours):
        [x, y, w, h] = cv2.boundingRect(contour)
        process_contour(x, y, w, h, index, reference, student_answers,answer_contours)
    # cv2.imwrite('sheet.jpg',reference)
    # Convert the NumPy array to a PIL image
    reference_image = Image.fromarray(reference)
        # Save the processed reference image to a temporary file and get its path
    # with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
    #     reference_image.save(temp_file.name)
    return index_numbers,student_answers,reference_image,answer_contours

def reference_sheet(image_path):

    reference, equalized = preprocess_image(image_path)
    normalized = normalize_brightness(equalized)
    opened_image = remove_noise(normalized)
    contours= find_contours(opened_image)
    largest_contour=find_largest_contour(contours)
    filtered_contours=filter_contours(contours,largest_contour,normalized)
    concatenated_contours = group_contours(filtered_contours)

    reference_answers = []

    # Iterate over the contours
    for index, contour in enumerate(concatenated_contours):
        [x, y, w, h] = cv2.boundingRect(contour)
        process_contour(x,y,w,h, index, reference, reference_answers)
    # cv2.imwrite('reference.jpg',reference)
    return reference_answers

def score(reference_answers,all_results):
    score=0
    index_numbers=[]
    scores=[]
    for i, value in enumerate(all_results):
        reference=cv2.imread(all_results[i]['image_paths'])
        for index, value in enumerate(reference_answers):
            if value== all_results[i]['student_answers'][index]:
                score+=1
                answer_contours=all_results[i]['answer_contours']
                # Answer is correct, draw green bounding box
                cv2.rectangle(reference, (answer_contours[i][0], answer_contours[i][1]), (answer_contours[i][0] + answer_contours[i][2], answer_contours[i][1] + answer_contours[i][3]), (0, 255, 0), 2)
            else:
                # Answer is incorrect, draw red bounding box
                cv2.rectangle(reference, (answer_contours[i][0], answer_contours[i][1]), (answer_contours[i][0] + answer_contours[i][2], answer_contours[i][1] + answer_contours[i][3]), (255, 0, 0), 2)
        index_numbers.append(all_results[i]['index_numbers'])
        scores.append(score)
    df=pd.DataFrame({
    'Index No':[index_numbers],
    'Score':[scores]
    })
    return df