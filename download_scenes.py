import os
import shutil
from pytube import YouTube  
from pytube import Playlist


workdir='output/scenes'
link = 'https://www.youtube.com/watch?v=Bhl-YBhNFkA'

download_vid=True
vid_file=''

p = Playlist('https://www.youtube.com/playlist?list=PLYbhKoo69xSNy42PHYaiO88E3AI6t_B8w')

def make_directory(path):
    try:
        shutil.rmtree(path)
    except Exception as e:
        print(str(e))
        pass
    os.makedirs(path)

make_directory(workdir)


for v in p.videos:
  ys = v.streams.get_highest_resolution()
  vid_file=ys.default_filename
  ys.download(workdir)