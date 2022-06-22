import os
from pathlib import Path
from pydub import AudioSegment
from PIL import Image

def create_vid_files(dir_path):
    image_files = list(Path(dir_path).glob("frame*.png"))
    audio_files = list(Path(dir_path).glob("*.mp3"))

    image_files.sort()
    audio_files.sort()

    try:
        assert len(image_files) == len(audio_files)
    except Exception as e:
        print(str(e))
        return

    scale=None
    ffmpeg_input_file = os.path.join(dir_path, "ffmpeg_input_file.txt")

    with open(ffmpeg_input_file, "w") as f:
        for image_file, audio_file in zip(image_files, audio_files):
            f.write(f"file '{image_file}'\n")
            
            mp3 = AudioSegment.from_mp3(audio_file)
            duration= len(mp3) / 1000 + 1
            
            f.write(f"duration {duration}\n")

            im = Image.open(image_file)
            scale=str(im.size[0])+"x"+str(im.size[1])




    output_video_file = os.path.join(dir_path, "video.mp4")
    cmd = f'ffmpeg -r 24 -f concat -safe 0 -i "{ffmpeg_input_file}" \
        -c:v libx265 -preset slow -crf 17 -vf "scale={scale}" -pix_fmt yuv420p -an -movflags faststart -r 24 "{output_video_file}"'
    
    print(cmd)
    os.system(cmd)

