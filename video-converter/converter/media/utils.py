import ffmpeg
import os

def convert(input_path, output_path):
    input_path = input_path.replace("\\", "/")
    output_path = output_path.replace("\\", "/")
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path,
                     vf="scale=640:380, fps=10",
                    vcodec="libx264",
                    crf=26,
                    preset="medium",
                     acodec='aac',
                     ar=22050,
                     **{'b:a': '33k'})
            .overwrite_output()
            .run(quiet=True)
        )
        return True
    except ffmpeg.Error as e:
        print("FFmpeg Error:", e)
        return False