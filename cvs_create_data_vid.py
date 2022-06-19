import os
import uuid
import shutil
from pathlib import Path
from tools.file_utils import create_dir, delete_previous_files

OUTPUT_DIR = 'output/cvs_data_vids'
id=uuid.uuid4().hex

OUTPUT_DIR = os.path.join(OUTPUT_DIR, id)
create_dir(OUTPUT_DIR)


data_items = {
    "airq" : {"script": "cyprus_airquality.py" },
    "wrbk" : {"script": "cyprus_worldbank.py" },
}


def enhance_images(dir_path):
    images = list(Path(dir_path).glob("*.png"))
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
        except:
            pass

        output_image = os.path.join(dir_path, f"frame_{i}.png")
        cmd = f'python  enhance_image_with_blender.py -o {output_image}'
        print(cmd)
        os.system(cmd)


for d in data_items:
    folder = d
    script = data_items[d]['script']
    OUTPUT_DIR_D= os.path.join(OUTPUT_DIR, folder)
    cmd = f'python  {script} -o {OUTPUT_DIR_D}'
    print(cmd)
    os.system(cmd)


    enhance_images(OUTPUT_DIR_D)
