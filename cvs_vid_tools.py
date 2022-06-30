import os

import moviepy.editor as mp


from pathlib import Path
from pydub import AudioSegment

from cvs_text_to_audio import combine_wav_files


USE_FFMPEG=False


def create_vid_file(dir_path):

    current_dir = Path(__file__).parent.absolute()

    image_files = list(Path(dir_path).glob("frame*.png"))
    audio_files = list(Path(dir_path).glob("*.wav"))

    if len(image_files) < 1: return None
    if len(audio_files) < 1: return None


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


    output_video_file = os.path.join(current_dir, dir_path, "video.mp4")
    if USE_FFMPEG:
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

            image_file=os.path.join(current_dir, str(image_files[-1]))
            f.write(f"file '{image_file}'\n")
            f.write(f"outpoint {.1}\n\n")


        # create video
        output_video_file = os.path.join(current_dir, dir_path, "video.mp4")
        cmd = f'ffmpeg  -f concat -safe 0  -i "{ffmpeg_input_png_file}" -vf fps=12 "{output_video_file}"'
        print(cmd)
        os.system(cmd)
    else:
        files = []
        durations = []
        for image_file, audio_file in zip(image_files, audio_files):
                image_file=os.path.join(current_dir, str(image_file))
                audio_file=str(audio_file)
                wav = AudioSegment.from_wav(audio_file)
                duration =  len(wav)/1000 
                image_file=os.path.join(current_dir, str(image_files[-1]))

                files.append(image_file)
                durations.append(duration)
        print(f"files: {files}")
        print(f"durations: {durations}")
        clip = mp.ImageSequenceClip(sequence=files, durations=durations) 
        clip.write_videofile(output_video_file, fps = 12)


    output_audio_file = os.path.join(current_dir, dir_path, "audio.wav")
    if True:
        # create audio
        combine_wav_files(audio_files, output_audio_file, silence_duration_ms=0)



    output_video_with_audio_file = os.path.join(current_dir, dir_path, "video_with_audio.mp4")
    if USE_FFMPEG:
        # add audio to video
        output_video_with_audio_file = os.path.join(current_dir, dir_path, "video_with_audio.mp4")
        #cmd = f'ffmpeg -i "{output_video_file}" -i "{output_audio_file}" -vcodec libx264 -acodec libmp3lame  -strict -1 "{output_video_with_audio_file}"'
        cmd = f'ffmpeg -i "{output_video_file}" -i "{output_audio_file}" -map 0:v -map 1:a -c:v copy -shortest  "{output_video_with_audio_file}"'
        print(cmd)
        os.system(cmd)
    else:
        videoclip = mp.VideoFileClip(output_video_file)
        audioclip = mp.AudioFileClip(output_audio_file)
        new_audioclip = mp.CompositeAudioClip([audioclip])
        videoclip.audio = new_audioclip
        videoclip.write_videofile(output_video_with_audio_file, fps = 12)


    if os.path.exists(output_video_with_audio_file):
        return output_video_with_audio_file

    return None


def concat_video_files(video_files, output_video, crossfade_duration=1.5):

    dir_path = os.path.dirname(output_video)
    '''
    ffmpeg_input_mp4_file = os.path.join(dir_path, "ffmpeg_input_mp4_file.txt")


    with open(ffmpeg_input_mp4_file, "w") as f:

        f.write(f"ffconcat version 1.0\n\n")

        for mp4 in video_files:
            f.write(f"file '{mp4}'\n")

    cmd = f'ffmpeg -f concat -safe 0 -i "{ffmpeg_input_mp4_file}" -c copy "{output_video}"'

    print(cmd)
    os.system(cmd)
    ''' 

    clips = []

    for index, vid_file in enumerate(video_files):

        print(f"concat: {vid_file}")
        clip = mp.VideoFileClip(vid_file)
        if index > 0:
            clip=clip.crossfadein(crossfade_duration)
            print(f"Adding crossfade to: {vid_file}")
        clips.append(clip)


    concat_clip =  mp.concatenate_videoclips(clips, padding=-1*crossfade_duration, method="compose")
    concat_clip.write_videofile(output_video, fps = 12)


    if os.path.exists(output_video):
        return output_video

    return None



if __name__ == "__main__":
    
    id = 'd4d2b76b6e4d4bf8aa735afa4d365163'
    OUTPUT_DIR = f'output/cvs_data_vids/{id}'
    
    #create_vid_file(f'output/cvs_data_vids/{id}/end')

    video_files=[
        os.path.join(OUTPUT_DIR, 'intro/video_with_audio.mp4'),
        os.path.join(OUTPUT_DIR, 'euro/video_with_audio.mp4'),
        os.path.join(OUTPUT_DIR, 'wrbk/video_with_audio.mp4'),
        os.path.join(OUTPUT_DIR, 'airq/video_with_audio.mp4'),
        os.path.join(OUTPUT_DIR, 'end/video_with_audio.mp4'),

    ]
    output_video = os.path.join(OUTPUT_DIR, 'video.mp4')
    output_video=concat_video_files(video_files, output_video)
    
