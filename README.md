# Video Frame Tools

Python scripts to extract and pre-process video frames with OpenCV, built for preparing image datasets (e.g. 3D reconstruction, object detection).

## Requirements

- Python 3.7+
- [OpenCV](https://pypi.org/project/opencv-python/)

```bash
pip install opencv-python
```

## Scripts

- [`video_to_frame.py`](#video_to_framepy) — simple frame extraction controlled by desired output FPS.
- [`preprocess_video.py`](#preprocess_videopy) — crop, frame removal, and a preview step before processing the whole video.

---

## `video_to_frame.py`

A script to extract frames from a video and save them as `.jpg` images, controlled by the **desired output frames per second (FPS)** instead of manually setting the interval between frames.

### Features

- Extracts frames from any video format supported by OpenCV (`.mp4`, `.avi`, `.mov`, etc.)
- FPS-based control: specify how many frames per second you want to extract, and the script automatically calculates the interval (`frame_skip`) based on the video's original FPS
- Prints video info before processing (original FPS, computed frame interval, effective output FPS) and logs progress as frames are saved
- Automatically creates a timestamped output subfolder for each run, named `<YYYYMMDD_HHMMSS>_<video_name>`, so results from different runs never overwrite each other
- Sequential, standardized output file naming (`frame_00000.jpg`, `frame_00001.jpg`, ...)

### Usage

```bash
python video_to_frame.py <video_path> <output_folder> [frame_skip]
```

- `video_path` — path to the input video file
- `output_folder` — base folder where a timestamped subfolder with the extracted frames will be created
- `frame_skip` *(optional)* — desired frames per second to extract. Defaults to `1` if omitted.

#### Example

```bash
python video_to_frame.py video.mp4 output_frames 2
```

This extracts frames from `video.mp4` at a rate of 2 frames per second and saves them into a new folder such as:

```
output_frames/20260729_143210_video/
```

### How it works

The script calculates the frame interval (`frame_skip` internally) based on the ratio between the video's original FPS and the desired FPS passed as argument:

```
frame_skip = round(original_fps / desired_fps)
```

For example, a 30 FPS video with a desired FPS of `2` results in a computed interval of `15`, meaning 1 frame is saved every 15 frames read.

> ⚠️ If the desired FPS is higher than the video's original FPS, the script will save every frame (extra frames cannot be "created").

### Notes

- If no third argument is passed, the script defaults to extracting **1 frame per second**.
- The output subfolder is named using the run's timestamp and the input video's filename (without extension), so re-running the script on the same video creates a new folder instead of overwriting previous results.
- Processing time depends on the video's resolution and duration.

---

## `preprocess_video.py`

Pre-processes a video before generating the frame dataset: lets you **visually check the crop on the first frame before processing the whole video**, and choose between removing frames, cropping/resizing, or both.

### Features

- **Preview before processing**: shows the first frame (original and already cropped) in windows and asks for confirmation (`y/n`) before running the whole video — avoids processing everything with a wrong crop
- **Interactive menu** to choose the processing mode:
  1. Remove frames (reduce framerate / skip frames)
  2. Crop/resize the video size
  3. Both
- Automatically creates the destination folder if it doesn't exist
- Saves the processed video as `<output_dir>/dataframe_<video_name>.mp4`
- Saves individual frames in `<output_dir>/dataframe_<video_name>/`, sequentially named (`dataframe_<video_name>_00000.jpg`, ...)
- Progress printed to the terminal in real time during processing (current/total frame and % complete)

### Usage

```bash
python preprocess_video.py --source <video_path> --output_dir <destination_folder> [options]
```

| Argument | Description | Default |
|---|---|---|
| `--source` | `0` for webcam, or path to the video | `0` |
| `--output_dir` | Destination folder (created automatically if it doesn't exist) | `output` |
| `--crop_x` | Starting X position of the crop | `0` |
| `--crop_y` | Starting Y position of the crop | `0` |
| `--crop_w` | Crop width | full video width |
| `--crop_h` | Crop height | full video height |
| `--frame_skip` | Keep 1 out of every N frames (only used if the frame-removal mode is chosen) | `1` |
| `--no_preview` | Skips the first-frame preview step | disabled |

#### Example

```bash
python preprocess_video.py --source video.mp4 --crop_x 50 --crop_y 20 --crop_w 800 --crop_h 600 --output_dir results
```

This generates:

```
results/
├── dataframe_video.mp4
└── dataframe_video/
    ├── dataframe_video_00000.jpg
    ├── dataframe_video_00001.jpg
    └── ...
```

### How it works

1. Opens the video and reads the first frame.
2. Unless `--no_preview` is passed, displays the original frame and the already-cropped frame in windows, and asks for confirmation that the crop is correct before continuing.
3. Asks which operation to apply to the whole video: remove frames, crop/resize, or both.
4. If frame removal is chosen and `--frame_skip` wasn't set via command line, asks for the desired interval.
5. Processes the whole video applying the chosen mode(s), saving the output video and individual frames, with a progress indicator in the terminal.

### Notes

- The dataset name (`dataframe_<video_name>`) is automatically derived from the video file name (without extension); if the source is a webcam, it uses `"webcam"`.
- The crop is applied before the final resize — `--crop_w`/`--crop_h` directly define the output dimensions.
