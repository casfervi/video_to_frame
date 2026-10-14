# -*- coding: utf-8 -*-
"""
DAV to MP4 Converter

Created on Fri Oct 2 13:19:09 2026

@author: vinicius.ferreira
"""

import os
import argparse
import subprocess


def run_ffmpeg(command):
    """Executa FFmpeg e retorna True em caso de sucesso."""
    try:
        result = subprocess.run(command)
        return result.returncode == 0
    except FileNotFoundError:
        raise RuntimeError(
            "FFmpeg was not found. Make sure FFmpeg is installed "
            "and available in the system PATH."
        )


def convert_dav_to_mp4(input_file):
    """Converte um arquivo DAV para MP4."""

    input_file = os.path.abspath(input_file)

    # ---------------------------------------------------------
    # Validate input
    # ---------------------------------------------------------

    if not os.path.isfile(input_file):
        raise FileNotFoundError(
            f"File not found:\n{input_file}"
        )

    if not input_file.lower().endswith(".dav"):
        raise ValueError(
            "Input file must have .dav extension."
        )

    # ---------------------------------------------------------
    # Create output directory
    # ---------------------------------------------------------

    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.basename(input_file)
    name = os.path.splitext(filename)[0]

    output_file = os.path.join(
        output_dir,
        f"{name}.mp4"
    )

    print()
    print("=" * 60)
    print("DAV to MP4 Converter")
    print("=" * 60)
    print(f"Input : {input_file}")
    print(f"Output: {output_file}")
    print()

    # ---------------------------------------------------------
    # Attempt 1 - Remux without re-encoding
    # ---------------------------------------------------------

    print("[1/2] Trying fast conversion without re-encoding...")
    print()

    command_copy = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-map", "0:v:0",
        "-map", "0:a?",
        "-c", "copy",
        "-movflags", "+faststart",
        output_file,
    ]

    if run_ffmpeg(command_copy):

        print()
        print("=" * 60)
        print("Conversion completed successfully!")
        print("Mode   : Stream copy (no re-encoding)")
        print("Quality: Original")
        print(f"Output : {output_file}")
        print("=" * 60)

        return

    # ---------------------------------------------------------
    # Attempt 2 - Re-encode to H.264
    # ---------------------------------------------------------

    print()
    print("[WARNING] Direct stream copy failed.")
    print("[2/2] Trying H.264 re-encoding...")
    print()

    # Remove incomplete MP4 from first attempt
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except OSError:
            pass

    command_encode = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-map", "0:v:0",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_file,
    ]

    if run_ffmpeg(command_encode):

        print()
        print("=" * 60)
        print("Conversion completed successfully!")
        print("Mode   : H.264 re-encoding")
        print("CRF    : 20")
        print(f"Output : {output_file}")
        print("=" * 60)

        return

    # ---------------------------------------------------------
    # Both methods failed
    # ---------------------------------------------------------

    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except OSError:
            pass

    raise RuntimeError(
        "Conversion failed using both stream copy and H.264 re-encoding."
    )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Convert DAV video files to MP4. "
            "The program first attempts stream copy and automatically "
            "falls back to H.264 encoding if necessary."
        )
    )

    parser.add_argument(
        "input",
        help="Path to the input .dav file"
    )

    args = parser.parse_args()

    try:
        convert_dav_to_mp4(args.input)

    except Exception as error:
        print()
        print("[ERROR]")
        print(error)


if __name__ == "__main__":
    main()