# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 08:33:08 2026

@author: vinicius.ferreira

Example to run: python preprocess_video.py --source video.mp4 --crop_x 50 --crop_y 20 --crop_w 800 --crop_h 600 --output_dir results

"""

import argparse
import os
import sys
import cv2


def get_first_frame(source):
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print("Error: could not open video source.")
        sys.exit(1)
    ret, frame = cap.read()
    if not ret:
        print("Error: could not read the first frame.")
        cap.release()
        sys.exit(1)
    return cap, frame


def apply_crop(frame, x, y, w, h):
    fh, fw = frame.shape[:2]
    x2, y2 = min(x + w, fw), min(y + h, fh)
    return frame[y:y2, x:x2]


def preview_frame(frame, window_name):
    cv2.imshow(window_name, frame)
    print(f"[{window_name}] Press any key in the image window to continue...")
    cv2.waitKey(0)
    cv2.destroyWindow(window_name)


def get_video_name(source):
    if isinstance(source, int):
        return "webcam"
    return os.path.splitext(os.path.basename(source))[0]


def choose_mode():
    print("\nWhat do you want to do with the video?")
    print("  1) Remove frames (reduce framerate / skip frames)")
    print("  2) Crop/resize the video size")
    print("  3) Both")
    while True:
        choice = input("Choose (1/2/3): ").strip()
        if choice in ("1", "2", "3"):
            return choice
        print("Invalid option.")


def main():
    parser = argparse.ArgumentParser(
        description="LingBot-MAP: video pre-processing (crop + frame removal)"
    )
    parser.add_argument("--source", type=str, default="0", help="0 for webcam, or path to the video")
    parser.add_argument("--output_dir", type=str, default="output", help="Destination folder (created if it doesn't exist)")
    parser.add_argument("--crop_x", type=int, default=0)
    parser.add_argument("--crop_y", type=int, default=0)
    parser.add_argument("--crop_w", type=int, default=None, help="Crop width (default: full width)")
    parser.add_argument("--crop_h", type=int, default=None, help="Crop height (default: full height)")
    parser.add_argument("--frame_skip", type=int, default=1, help="Keep 1 out of every N frames (1 = keep all)")
    parser.add_argument("--no_preview", action="store_true", help="Skip the first-frame preview step")
    args = parser.parse_args()

    source = int(args.source) if args.source.isdigit() else args.source

    video_name = get_video_name(source)
    dataset_name = f"dataframe_{video_name}"
    os.makedirs(args.output_dir, exist_ok=True)
    video_output_path = os.path.join(args.output_dir, f"{dataset_name}.mp4")
    frames_dir = os.path.join(args.output_dir, dataset_name)

    # --- Step 1: capture and show the first frame before processing everything ---
    cap, first_frame = get_first_frame(source)
    fh, fw = first_frame.shape[:2]
    crop_w = args.crop_w or fw
    crop_h = args.crop_h or fh
    cropped_preview = apply_crop(first_frame, args.crop_x, args.crop_y, crop_w, crop_h)

    if not args.no_preview:
        print(f"Original frame: {fw}x{fh} | Requested crop: {crop_w}x{crop_h} starting at ({args.crop_x},{args.crop_y})")
        preview_frame(first_frame, "Original frame")
        preview_frame(cropped_preview, "Cropped frame (check before continuing)")
        confirm = input("Does the crop look correct? (y/n): ").strip().lower()
        if confirm != "y":
            print("Adjust --crop_x/--crop_y/--crop_w/--crop_h and run again.")
            cap.release()
            sys.exit(0)

    # --- Step 2: choose what to do with the whole video ---
    mode = choose_mode()
    do_crop = mode in ("2", "3")
    do_skip = mode in ("1", "3")

    if do_skip and args.frame_skip <= 1:
        val = input("Frame interval to keep (e.g. 2 = keep 1 out of every 2): ").strip()
        args.frame_skip = int(val) if val.isdigit() and int(val) > 1 else 2

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or None
    # out_w = crop_w if do_crop else fw
    # out_h = crop_h if do_crop else fh
    if do_crop:
        # Use the actual crop dimensions, not the requested dimensions
        test_frame = apply_crop(
            first_frame,
            args.crop_x,
            args.crop_y,
            crop_w,
            crop_h
        )
    
        out_h, out_w = test_frame.shape[:2]
    
    else:
        out_w = fw
        out_h = fh
    
    out_fps = fps / args.frame_skip if do_skip else fps

    os.makedirs(frames_dir, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(video_output_path, fourcc, out_fps, (out_w, out_h))

    print("\n--- VIDEO WRITER DEBUG ---")
    print(f"Writer opened: {writer.isOpened()}")
    print(f"Expected size: {out_w}x{out_h}")
    print(f"Output FPS: {out_fps}")
    print("Codec: mp4v")
    print("--------------------------")

    # Rewind capture to the start to process the whole video
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    frame_idx = 0
    written = 0
    print("\nProcessing video...")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if do_skip and (frame_idx % args.frame_skip != 0):
            frame_idx += 1
            continue
        if do_crop:
            frame = apply_crop(frame, args.crop_x, args.crop_y, crop_w, crop_h)
            
        
        h, w = frame.shape[:2]

        if written == 0:
            print("\n--- FIRST OUTPUT FRAME ---")
            print(f"Frame size: {w}x{h}")
            print(f"Frame shape: {frame.shape}")
            print(f"Frame dtype: {frame.dtype}")
            print(f"Writer expects: {out_w}x{out_h}")
            print("--------------------------")
        
        if (w, h) != (out_w, out_h):
            raise RuntimeError(
                f"Frame size mismatch at frame {frame_idx}: "
                f"frame={w}x{h}, writer={out_w}x{out_h}"
            )
                
        
        writer.write(frame)
        frame_path = os.path.join(frames_dir, f"{dataset_name}_{written:05d}.jpg")
        cv2.imwrite(frame_path, frame)
        written += 1
        frame_idx += 1

        if total_frames:
            pct = (frame_idx / total_frames) * 100
            print(f"\rFrame {frame_idx}/{total_frames} ({pct:5.1f}%) | saved: {written}", end="", flush=True)
        else:
            print(f"\rFrame read: {frame_idx} | saved: {written}", end="", flush=True)

    print()  # newline after the progress bar
    cap.release()
    writer.release()
    print(f"\nDone: {written} frames processed.")
    print(f"Video saved to: '{video_output_path}'")
    print(f"Frames saved to: '{frames_dir}' ({out_w}x{out_h} @ {out_fps:.1f} fps)")


if __name__ == "__main__":
    main()

