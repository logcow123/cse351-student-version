"""
Course: CSE 351
Assignment: 06
Author: [Your Name]

Instructions:

- see instructions in the assignment description in Canvas

""" 

import multiprocessing as mp
import os
import cv2
import numpy as np

from cse351 import *

# Folders
INPUT_FOLDER = "faces"
STEP1_OUTPUT_FOLDER = "step1_smoothed"
STEP2_OUTPUT_FOLDER = "step2_grayscale"
STEP3_OUTPUT_FOLDER = "step3_edges"

# Parameters for image processing
GAUSSIAN_BLUR_KERNEL_SIZE = (5, 5)
CANNY_THRESHOLD1 = 75
CANNY_THRESHOLD2 = 155

# Allowed image extensions
ALLOWED_EXTENSIONS = ['.jpg']

# ---------------------------------------------------------------------------
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

# ---------------------------------------------------------------------------
def task_convert_to_grayscale(image):
    if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
        return image # Already grayscale
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# ---------------------------------------------------------------------------
def task_smooth_image(image, kernel_size):
    return cv2.GaussianBlur(image, kernel_size, 0)

# ---------------------------------------------------------------------------
def task_detect_edges(image, threshold1, threshold2):
    if len(image.shape) == 3 and image.shape[2] == 3:
        print("Warning: Applying Canny to a 3-channel image. Converting to grayscale first for Canny.")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif len(image.shape) == 3 and image.shape[2] != 1 : # Should not happen with typical images
        print(f"Warning: Input image for Canny has an unexpected number of channels: {image.shape[2]}")
        return image # Or raise error
    return cv2.Canny(image, threshold1, threshold2)

# ---------------------------------------------------------------------------
# def process_from_queue(input_queue, processing_function, **kwargs):

#     output_folder = kwargs.get(output_folder)
#     processing_args = kwargs.get(processing_args)
#     output_queue = kwargs.get(output_queue)
#     still_working = True
#     while still_working:
#         img_tup = input_queue.get()
#         if (img_tup != None):
#             img = img_tup[0]
#             filename = img_tup[1]
#             if processing_args:
#                 processed_img = processing_function(img, *processing_args)
#             else:
#                 processed_img = processing_function(img)
#             if output_queue:
#                 output_queue.put((processed_img, filename))
#             else:
#                 create_folder_if_not_exists(output_folder)
#                 output_image_path = os.path.join(output_folder, filename)
#                 cv2.imwrite(output_folder, processed_img)
#         else:
#             if output_queue:
#                 output_queue.put(None)
#             still_working = False

# def proccess_image_from_folder(input_folder, output_queue, processing_function, **kwargs):

#     load_args= kwargs.get(load_args)
#     processing_args = kwargs.get(processing_args)
#     processed_count = 0
#     for filename in os.listdir(input_folder):
#         file_ext = os.path.splitext(filename)[1].lower()
#         if file_ext not in ALLOWED_EXTENSIONS:
#             continue

#         input_image_path = os.path.join(input_folder, filename)

#         try:
#             # Read the image
#             if load_args is not None:
#                 img = cv2.imread(input_image_path, load_args)
#             else:
#                 img = cv2.imread(input_image_path)

#             if img is None:
#                 print(f"Warning: Could not read image '{input_image_path}'. Skipping.")
#                 continue

#             # Apply the processing function
#             if processing_args:
#                 processed_img = processing_function(img, *processing_args)
#             else:
#                 processed_img = processing_function(img)

#             # Save the processed image
#             output_queue.put((processed_img, filename))

#             processed_count += 1
#         except Exception as e:
#             print(f"Error processing file '{input_image_path}': {e}")

#     output_queue.put(None)
            
def smooth_process(folder, out_queue, processing_function, processing_args):
    processed_count = 0
    for filename in os.listdir(folder):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            continue

        input_image_path = os.path.join(folder, filename)

        try:
            # Read the image
            img = cv2.imread(input_image_path)

            if img is None:
                print(f"Warning: Could not read image '{input_image_path}'. Skipping.")
                continue

            # Apply the processing function
            if processing_args:
                processed_img = processing_function(img, *processing_args)
            else:
                processed_img = processing_function(img)

            # Save the processed image
            out_queue.put((processed_img, filename))

            processed_count += 1
        except Exception as e:
            print(f"Error processing file '{input_image_path}': {e}")
    out_queue.put(None)

def grayscale_process(in_queue, out_queue, process_func):
    still_working = True
    while still_working:
        try:
            img_tup = in_queue.get()
            if (img_tup == None):
                still_working = False
                break

            img = img_tup[0]
            filename = img_tup[1]

            if img is None:
                print(f"Warning: Could not read image  Skipping.")
                continue
            
            processed_img = process_func(img)

            out_queue.put((processed_img, filename))
        except Exception as e:
            print("ERROR OCCURED")
    out_queue.put(None)

def edge_process(in_queue, output_folder, process_func, process_args):
    still_working = True
    while still_working:
        try:
            img_tup = in_queue.get()
            if (img_tup == None):
                still_working = False
                break

            img = img_tup[0]
            filename = img_tup[1]

            if img is None:
                print(f"Warning: Could not read image  Skipping.")
                continue
            
            processed_img = process_func(img, *process_args)

            create_folder_if_not_exists(output_folder)
            output_image_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_image_path, processed_img)
        except Exception as e:
            print("ERROR OCCURED")

# ---------------------------------------------------------------------------
def process_images_in_folder(input_folder,              # input folder with images
                             output_folder,             # output folder for processed images
                             processing_function,       # function to process the image (ie., task_...())
                             load_args=None,            # Optional args for cv2.imread
                             processing_args=None):     # Optional args for processing function

    create_folder_if_not_exists(output_folder)
    print(f"\nProcessing images from '{input_folder}' to '{output_folder}'...")

    processed_count = 0
    for filename in os.listdir(input_folder):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            continue

        input_image_path = os.path.join(input_folder, filename)
        output_image_path = os.path.join(output_folder, filename) # Keep original filename

        try:
            # Read the image
            if load_args is not None:
                img = cv2.imread(input_image_path, load_args)
            else:
                img = cv2.imread(input_image_path)

            if img is None:
                print(f"Warning: Could not read image '{input_image_path}'. Skipping.")
                continue

            # Apply the processing function
            if processing_args:
                processed_img = processing_function(img, *processing_args)
            else:
                processed_img = processing_function(img)

            # Save the processed image
            cv2.imwrite(output_image_path, processed_img)

            processed_count += 1
        except Exception as e:
            print(f"Error processing file '{input_image_path}': {e}")

    print(f"Finished processing. {processed_count} images processed into '{output_folder}'.")

# ---------------------------------------------------------------------------
def run_image_processing_pipeline():
    print("Starting image processing pipeline...")

    # TODO
    # - create queues
    queue_smooth = mp.Queue()
    queue_gray = mp.Queue()
    # - create barriers
    # - create the three processes groups
    process_smooth = mp.Process(target=smooth_process, args=(INPUT_FOLDER, queue_smooth, task_smooth_image, [GAUSSIAN_BLUR_KERNEL_SIZE]))
    process_gray = mp.Process(target=grayscale_process, args=(queue_smooth, queue_gray, task_convert_to_grayscale))
    process_edge = mp.Process(target=edge_process, args=(queue_gray, 'step3_edges', task_detect_edges, (CANNY_THRESHOLD1, CANNY_THRESHOLD2)))
    
    process_smooth.start()
    process_gray.start()
    process_edge.start()

    process_smooth.join()
    process_gray.join()
    process_edge.join()
    # - you are free to change anything in the program as long as you
    #   do all requirements.

    # --- Step 1: Smooth Images ---
    # process_images_in_folder(INPUT_FOLDER, STEP1_OUTPUT_FOLDER, task_smooth_image,
    #                          processing_args=(GAUSSIAN_BLUR_KERNEL_SIZE,))

    # # --- Step 2: Convert to Grayscale ---
    # process_images_in_folder(STEP1_OUTPUT_FOLDER, STEP2_OUTPUT_FOLDER, task_convert_to_grayscale)

    # # --- Step 3: Detect Edges ---
    # process_images_in_folder(STEP2_OUTPUT_FOLDER, STEP3_OUTPUT_FOLDER, task_detect_edges,
    #                          load_args=cv2.IMREAD_GRAYSCALE,        
    #                          processing_args=(CANNY_THRESHOLD1, CANNY_THRESHOLD2))

    # print("\nImage processing pipeline finished!")
    # print(f"Original images are in: '{INPUT_FOLDER}'")
    # print(f"Grayscale images are in: '{STEP1_OUTPUT_FOLDER}'")
    # print(f"Smoothed images are in: '{STEP2_OUTPUT_FOLDER}'")
    # print(f"Edge images are in: '{STEP3_OUTPUT_FOLDER}'")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    log = Log(show_terminal=True)
    log.start_timer('Processing Images')

    # check for input folder
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: The input folder '{INPUT_FOLDER}' was not found.")
        print(f"Create it and place your face images inside it.")
        print('Link to faces.zip:')
        print('   https://drive.google.com/file/d/1eebhLE51axpLZoU6s_Shtw1QNcXqtyHM/view?usp=sharing')
    else:
        run_image_processing_pipeline()

    log.write()
    log.stop_timer('Total Time To complete')
