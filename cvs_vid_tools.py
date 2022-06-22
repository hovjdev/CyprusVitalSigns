import os
from pathlib import Path
from pydub import AudioSegment
from PIL import Image


from cvs_text_to_audio import combine_wav_files

def create_vid_files(dir_path):

    current_dir = Path(__file__).parent.absolute()

    image_files = list(Path(dir_path).glob("frame*.png"))
    audio_files = list(Path(dir_path).glob("*.wav"))

    image_files.sort()
    audio_files.sort()

    print(f"image_files: {image_files}")
    print(f"audio_files: {audio_files}")


    try:
        print(f"assert {len(image_files)} == {len(audio_files)}")
        assert len(image_files) == len(audio_files)
    except Exception as e:
        print(str(e))
        return

    scale=None
    ffmpeg_input_png_file = os.path.join(dir_path, "ffmpeg_input_png_file.txt")

    with open(ffmpeg_input_png_file, "w") as f:

        f.write(f"ffconcat version 1.0\n\n")


        for image_file, audio_file in zip(image_files, audio_files):
            image_file=os.path.join(current_dir, str(image_file))
            audio_file=str(audio_file)

            f.write(f"file '{image_file}'\n")
            
            wav = AudioSegment.from_wav(audio_file)
            outpoint =  len(wav)/1000  
            
            f.write(f"outpoint {outpoint}\n\n")

            im = Image.open(image_file)
            scale=str(im.size[0])+"x"+str(im.size[1])

        image_file=os.path.join(current_dir, str(image_files[-1]))
        f.write(f"file '{image_file}'\n")
        f.write(f"outpoint {.1}\n\n")


    # create video
    output_video_file = os.path.join(current_dir, dir_path, "video.mp4")
    cmd = f'ffmpeg  -f concat -safe 0  -i "{ffmpeg_input_png_file}" -vf fps=24 "{output_video_file}"'
    print(cmd)
    os.system(cmd)


    # create audio
    output_audio_file = os.path.join(current_dir, dir_path, "audio.wav")
    combine_wav_files(audio_files, output_audio_file, silence_duration_ms=0)


    output_video_with_audio_file = os.path.join(current_dir, dir_path, "video_with_audio.mp4")
    cmd = f'ffmpeg -i "{output_video_file}" -i "{output_audio_file}" -vcodec libx264 -acodec libmp3lame "{output_video_with_audio_file}"'
    print(cmd)
    os.system(cmd)
    


if __name__ == "__main__":
    create_vid_files('output/cvs_data_vids/05b33fdd58414e229a77ae097a09bb40/airq')