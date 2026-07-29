# Video Frame Extractor

A Python script to extract frames from a video and save them as `.jpg` images, controlled by the **desired output frames per second (FPS)** instead of manually setting the interval between frames.

## Features

- Extracts frames from any video format supported by OpenCV (`.mp4`, `.avi`, `.mov`, etc.)
- FPS-based control: specify how many frames per second you want to extract, and the script automatically calculates the interval (`frame_skip`) based on the video's original FPS
- Prints video info before processing (original FPS, computed frame interval, effective output FPS) and logs progress as frames are saved
- Automatically creates a timestamped output subfolder for each run, named `<YYYYMMDD_HHMMSS>_<video_name>`, so results from different runs never overwrite each other
- Sequential, standardized output file naming (`frame_00000.jpg`, `frame_00001.jpg`, ...)

## Requirements

- Python 3.7+
- [OpenCV](https://pypi.org/project/opencv-python/)

```bash
pip install opencv-python
```

## Usage

```bash
python video_to_images.py <video_path> <output_folder> [frame_skip]
```

- `video_path` — path to the input video file
- `output_folder` — base folder where a timestamped subfolder with the extracted frames will be created
- `frame_skip` *(optional)* — desired frames per second to extract. Defaults to `1` if omitted.

### Example

```bash
python video_to_images.py video.mp4 output_frames 2
```

This extracts frames from `video.mp4` at a rate of 2 frames per second and saves them into a new folder such as:

```
output_frames/20260729_143210_video/
```

## How it works

The script calculates the frame interval (`frame_skip` internally) based on the ratio between the video's original FPS and the desired FPS passed as argument:

```
frame_skip = round(original_fps / desired_fps)
```

For example, a 30 FPS video with a desired FPS of `2` results in a computed interval of `15`, meaning 1 frame is saved every 15 frames read.

> ⚠️ If the desired FPS is higher than the video's original FPS, the script will save every frame (extra frames cannot be "created").

## Notes

- If no third argument is passed, the script defaults to extracting **1 frame per second**.
- The output subfolder is named using the run's timestamp and the input video's filename (without extension), so re-running the script on the same video creates a new folder instead of overwriting previous results.
- Processing time depends on the video's resolution and duration.
