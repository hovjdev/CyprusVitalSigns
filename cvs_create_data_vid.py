import os
import uuid
from tools.file_utils import create_dir

OUTPUT_DIR = 'output/cvs_data_vids'
id=uuid.uuid4().hex

OUTPUT_DIR = os.path.join(OUTPUT_DIR, id)
create_dir(OUTPUT_DIR)


data_items = {
    "airq" : {"script": "cyprus_airquality.py" },
    "wrbk" : {"script": "cyprus_worldbank.py" },
}

for d in data_items:
    folder = d
    script = data_items[d]['script']
    OUTPUT_DIR_D= os.path.join(OUTPUT_DIR, folder)
    cmd = f'python  {script} -o {OUTPUT_DIR_D}'
    print(cmd)
    os.system(cmd)


