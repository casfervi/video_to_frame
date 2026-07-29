# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 17:14:27 2026

@author: vinicius.ferreira
"""

import cv2
import os
import sys
from datetime import datetime

def video_to_images(video_path, output_folder, desired_fps = 2):
    """
    Extract frames from a video and save them as images.

    :param video_path: Path to the input video file.
    :param output_folder: Folder where images will be saved.
    :param desired_fps: Save desired_fps frames per second (default=2 frames per second).
    """
    # Validate video file
    if not os.path.isfile(video_path):
        print(f"Error: Video file '{video_path}' not found.")
        return

    
    # Open the video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video '{video_path}'.")
        return

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    if video_fps <= 0:
        raise ValueError("Não foi possível obter o FPS do vídeo")
        
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
   
    frame_count = 0
    saved_count = 0

    frame_skip = max(1, round(video_fps / desired_fps))
    print(f"FPS do vídeo: {video_fps:.2f} | Salvando 1 a cada {frame_skip} frames "
      f"(~{video_fps/frame_skip:.2f} fps de saída)")
    
    #Get datetime to save in a specific folder
    today = datetime.today()
    formatted_date = str(today.strftime('%Y%m%d_%H%M%S'))
    
    video_name = video_path.split("\\")[-1].split(".")[0]

    customized_output_folder_path = f"{output_folder}/{formatted_date}_{video_name}"

    # Create output folder if it doesn't exist
    os.makedirs(customized_output_folder_path, exist_ok=True)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # End of video

        # Save only every Nth frame
        if frame_count % frame_skip == 0:
            img_name = os.path.join(customized_output_folder_path, f"frame_{saved_count:05d}.jpg")
            cv2.imwrite(img_name, frame)
            saved_count += 1
            print(f"Saving frame number {frame_count}. Video has a total of {total_frames} frames.")

        frame_count += 1
        
    cap.release()
    print(f"✅ Done! Saved {saved_count} images to '{customized_output_folder_path}'.")

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 3:
        print("Usage: python video_to_images.py <video_path> <output_folder> [frame_skip]")
        sys.exit(1)

    video_path = sys.argv[1]
    output_folder = sys.argv[2]
    frame_skip = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    video_to_images(video_path, output_folder, frame_skip)
