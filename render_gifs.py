import os
import subprocess
import argparse

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate GIFs from image sequences using FFMPEG.")
    parser.add_argument("--resolution", type=str, required=True, help="Resolution (e.g., 320 for width)")
    parser.add_argument("--fps", type=int, required=True, help="Frames per second")
    parser.add_argument("--input_dir", type=str, required=True, help="Input directory containing subfolders with image sequences")
    args = parser.parse_args()

    resolution = args.resolution
    fps = args.fps
    input_dir = args.input_dir

    # Validate input directory
    if not os.path.isdir(input_dir):
        print(f"Error: {input_dir} is not a valid directory.")
        return

    # Process each subfolder in the input directory
    for subfolder in os.listdir(input_dir):
        subfolder_path = os.path.join(os.path.join(input_dir, subfolder), 'rgb')

        if os.path.isdir(subfolder_path):
            output_gif_path = os.path.join(subfolder_path, "output.gif")

            # Run FFMPEG command
            ffmpeg_command = [
                "ffmpeg",
                "-framerate", f"{fps}",
                "-i", os.path.join(subfolder_path, "%06d.png"),
                # "-vf", f"fps={fps},scale={resolution}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
                "-s", f"{resolution}:{resolution}",
                "-loop", "0",
                output_gif_path
            ]

            print(f"Processing subfolder: {subfolder_path}")
            try:
                subprocess.run(ffmpeg_command, check=True)
                print(f"Generated GIF: {output_gif_path}")
            except subprocess.CalledProcessError as e:
                print(f"Error processing subfolder {subfolder_path}: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()

