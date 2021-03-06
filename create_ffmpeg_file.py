
import tqdm
import os
from os import listdir
from os.path import isfile, join
from PIL import Image


path1="E:\\Joseph\\360-frames"
path2="D:\\Joseph\\360-frames"
path1="C:\\Users\\Joseph\\Desktop\\Blender\\VR\Intro\\end_frames"
vid1 = [join(path1, f) for f in listdir(path1) if isfile(join(path1, f))]
vid2 = [join(path2, f) for f in listdir(path2) if isfile(join(path2, f))]
vid2 = []

vid1 = sorted(vid1)
vid2 = sorted(vid2)

vid1.extend(vid2)
file_size=None

if True:
    with open("bad_png.txt", "w") as f:
        for v in tqdm.tqdm(vid1):
            v=v.replace('\\', '/')
            try:
                im = Image.open(v)
                im.verify() #I perform also verify, don't know if he sees other types o defects
                im.close() #reload is necessary in my case
                file_size = os.stat(v).st_size
                assert file_size > 30e6
            except Exception as e: 
                print(f"Problem with {v}, {e}, 'file_size', file_size")
                f.write(f"file '{v}'\n")
  


with open("ffmpeg_input_file_end.txt", "w") as f:
    for v in tqdm.tqdm(vid1):
        v=v.replace('\\', '/')
        f.write(f"file '{v}'\n")
        f.write(f"duration 0.033333333333\n")


exit(1)


'''
# ffmpeg_input_file.txt  generated by python script CyprusVitalSigns\create_ffmpeg_file.py
ffmpeg -r 30  -f concat -safe 0  -i "CyprusVitalSigns\CyprusVitalSigns\\ffmpeg_input_file.txt"  -c:v libx265 -preset slow -crf 17 -vf "scale=8192x8192" -pix_fmt yuv420p -an -movflags faststart -r 30 "Blender\VR\\test10.mp4"
ffmpeg -r 30  -f concat -safe 0  -i "CyprusVitalSigns\CyprusVitalSigns\\ffmpeg_input_file_intro.txt"  -c:v libx265 -preset slow -crf 17 -vf "scale=8192x8192" -pix_fmt yuv420p -an -movflags faststart -r 30 "Blender\VR\\test10_intro.mp4"
ffmpeg -r 30  -f concat -safe 0  -i "CyprusVitalSigns\CyprusVitalSigns\\ffmpeg_input_file_end.txt"  -c:v libx265 -preset slow -crf 17 -vf "scale=8192x8192" -pix_fmt yuv420p -an -movflags faststart -r 30 "Blender\VR\\test10_end.mp4"


# add audio to mp4
ffmpeg -i test10_intro.mp4  -i test10_intro_audio.flac  -map 0:v -map 1:a -c:v copy -shortest test10_intro_audio.mp4
ffmpeg -i test10_end.mp4  -i test10_end_audio.flac  -map 0:v -map 1:a -c:v copy -shortest test10_end_audio.mp4


# concat mp4 files
ffmpeg -f concat -safe 0 -i vidlist.txt -c copy test10_merged.mp4

ffmpeg -i "Blender\VR\test10.mp4" -i "Blender\VR\\audio_v7.flac" -map 0:v -map 1:a -c:v copy -shortest test9_with_audio_v7.mp4
'''

