import os
import json
import uuid
import shutil
from pathlib import Path
from PIL import Image
from tools.file_utils import create_dir, delete_previous_files

INPUT_DIR = 'input/cvs_data_vids'
OUTPUT_DIR = 'output/cvs_data_vids'



def create_texture_image(dir_path):
    output_image = os.path.join(dir_path, f"texture_####.png")
    cmd = f'python  create_texture.py -o {output_image}'
    print(cmd)
    os.system(cmd)

    try:
        output_image = os.path.join(dir_path, f"texture_0001.png")
        assert os.path.exists(output_image)
        return output_image
    except Exception as e:
        print(str(e))

    return None

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


def enhance_images(dir_path):
    images = list(Path(dir_path).glob("*.png"))
    data_files = list(Path(dir_path).glob("*.npy"))

    images.sort()
    data_files.sort()

    has_data=False
    if data_files and len(data_files) == len(images):
        has_data=True

    if len(images) == 0:
        return
    if len(images) % 2 != 0:
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
        cmd = f'python  enhance_image_with_blender.py -o {output_image}'
        print(cmd)
        os.system(cmd)


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



if __name__ == "__main__":

    id=uuid.uuid4().hex

    OUTPUT_DIR = os.path.join(OUTPUT_DIR, id)
    create_dir(OUTPUT_DIR)
    create_dir(INPUT_DIR)


    script_items = get_script_items()

    for d in script_items:
        folder = d
        script = script_items[d]['script']
        OUTPUT_DIR_D= os.path.join(OUTPUT_DIR, folder)
        cmd = f'python  {script} -o {OUTPUT_DIR_D}'
        print(cmd)
        os.system(cmd)


        enhance_images(OUTPUT_DIR_D)
        texture_image = create_texture_image(OUTPUT_DIR_D)
        combine_frames_and_texture_images(OUTPUT_DIR_D)
