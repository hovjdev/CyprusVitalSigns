from distutils import text_file
import os
import json
import uuid
import shutil
from pathlib import Path
from PIL import Image


from tools.misc import create_texture_image
from tools.file_utils import create_dir, delete_previous_files
from cvs_text_to_audio import textfile_to_wav
from cvs_vid_tools import create_vid_file, concat_video_files
from upload_to_vimeo import upload_mp4_to_vimeo


DIRNAME = os.path.dirname(__file__)
INPUT_DIR = os.path.join(DIRNAME, 'input', 'cvs_data_vids')
OUTPUT_DIR = os.path.join(DIRNAME, 'output', 'cvs_data_vids')



def combine_frames_and_texture_images(dir_path):
    images = list(Path(dir_path).glob("frame*.png"))
    texture = list(Path(dir_path).glob("texture*.png"))

    try:
        assert len(texture) == 1
        assert len(images)>0
    except Exception as e:
        print(str(e))
        return
    for im in images:
        background = Image.open(texture[0])
        foreground = Image.open(im)

        background.paste(foreground, (0, 0), foreground)
        background.save(im)


def enhance_images(dir_path, enhance_with_blender=True):
    images = list(Path(dir_path).glob("*.png"))
    data_files = list(Path(dir_path).glob("*.npy"))

    images.sort()
    data_files.sort()

    has_data=False
    if data_files and len(data_files) == len(images):
        has_data=True

    if len(images) == 0:
        return

    images.append(images[0])

    files_path = os.path.join('input', 'blender', 'files')
    delete_previous_files(files_path)
    create_dir(files_path)

    for i in range(len(images)-1):

        try:
            shutil.copyfile(images[i], os.path.join(files_path, "image1.png"))
            shutil.copyfile(images[i+1], os.path.join(files_path, "image2.png"))
            if has_data:
                shutil.copyfile(data_files[i], os.path.join(files_path, "data.npy"))
                #print(f">>>>>>>> {images[i]}, {data_files[i]}")
            else:
                #print(f">>>>>>>> {images[i]}")
                os.remove(os.path.join(files_path, "data.npy"))

        except:
            pass


        output_image = os.path.join(dir_path, f"frame_{i}_####.png")
        if enhance_with_blender:
            
            cmd = f'python  enhance_image_with_blender.py -o {output_image}'
            print(cmd)
            os.system(cmd)
        else:
            output_image = os.path.join(dir_path, f"frame_{i}_0000.png")
            shutil.copyfile(images[i], output_image)


def get_script_items():
    json_file = os.path.join(INPUT_DIR, 'data_scripts.json')

    script_items=None
    '''
    script_items = {
        "airq" : {"script": "cyprus_airquality.py" },
        "wrbk" : {"script": "cyprus_worldbank.py" },
    }

    with open(json_file, 'w+') as f:
        json.dump(script_items, f, indent=2)
    '''

    with open(json_file) as f:
        data = f.read()
        print(data)
        script_items = json.loads(data)

    return script_items

def create_wav_files(dir_path, parrot=None):
    text_files = list(Path(dir_path).glob("*.txt"))
    text_files.sort()

    for t in text_files:
        t=str(t)
        assert t[-4:]=='.txt'
        wav_file = t[:-4]+'.wav'
        textfile_to_wav(t, wav_file, parrot)



if __name__ == "__main__":

    #exit(1)

    id=uuid.uuid4().hex

    OUTPUT_DIR = os.path.join(OUTPUT_DIR, id)
    create_dir(OUTPUT_DIR)
    create_dir(INPUT_DIR)

    script_items = get_script_items()

    video_files = []

    for d in script_items:
        print(f'>>>{d}')
        folder = d
        script = script_items[d]['script']

        skip=False
        if "skip" in script_items[d]:
            skip = script_items[d]['skip']

        if skip:
            print(f'>>> Skipping {d}')
            continue

        OUTPUT_DIR_D= os.path.join(OUTPUT_DIR, folder)
        
        enhance_with_blender = True
        if "enhance_with_blender" in script_items[d]:
            enhance_with_blender=script_items[d]['enhance_with_blender']
            print(f'enhance_with_blender: {enhance_with_blender}')

        cmd = f'python  {script} --output {OUTPUT_DIR_D}'
        print(cmd)
        os.system(cmd)


        print(f'>>>> enhance_images({OUTPUT_DIR_D})')
        enhance_images(OUTPUT_DIR_D, enhance_with_blender=enhance_with_blender)

        if enhance_with_blender:
            print(f'>>>> create_texture_image({OUTPUT_DIR_D})')
            create_texture_image(OUTPUT_DIR_D)

            print(f'>>>> combine_frames_and_texture_images({OUTPUT_DIR_D})')
            combine_frames_and_texture_images(OUTPUT_DIR_D)

        print(f'>>>> create_wav_files({OUTPUT_DIR_D})')
        create_wav_files(OUTPUT_DIR_D)

        print(f'>>>> create_vid_files({OUTPUT_DIR_D})')
        video_file = create_vid_file(OUTPUT_DIR_D)

        if  video_file:
            video_files.append(video_file)

    
    output_video = os.path.join(OUTPUT_DIR, 'video.mp4')
    output_video=concat_video_files(video_files, output_video)

    if output_video:
        data={
                'video_title': 'Cyprus Vital Signs',
                'video_file_path': output_video,
                'video_tags': 'Cyprus Vital Signs',
                'video_thumbnail_path': None,
                'public': False,
                'playlist_name': None
            }
        upload_mp4_to_vimeo(output_video, data)


   