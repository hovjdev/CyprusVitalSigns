import os
import shutil
import cv2
from deepface import DeepFace
from pytube import YouTube  


#workdir='output/faces/frames_gut'
#link = 'https://www.youtube.com/watch?v=WZzMAuBtBeU'
workdir='output/faces/frames_urs'
link = 'https://www.youtube.com/watch?v=Bhl-YBhNFkA'

download_vid=True
vid_file=''

def make_directory(path):
    try:
        shutil.rmtree(path)
    except:
        pass
    os.makedirs(path)

make_directory(f"{workdir}")



if download_vid==True:
  yt = YouTube(link)
  ys = yt.streams.get_highest_resolution()
  vid_file=ys.default_filename
  ys.download(workdir)
  

vidcap = cv2.VideoCapture(os.path.join(workdir, vid_file))
count = -1
success=True
backend = 'mtcnn'

while success:
  count += 1
  if count % 100 == 0: print(count) 
  success,image = vidcap.read()
  if count < 515:
    continue
  try:
    cv2.imwrite(f"{workdir}/tmp.jpg", image)      
    detected_face = DeepFace.detectFace(f"{workdir}/tmp.jpg", detector_backend = backend, target_size = (500, 500))
    im = cv2.cvtColor(detected_face * 255, cv2.COLOR_BGR2RGB)
    cv2.imwrite(f"{workdir}/face_{count}.jpg", im)
  except Exception as e:
    print(str(e))
    continue

