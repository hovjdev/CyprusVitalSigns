import os
import uuid
from tools.file_utils import create_dir

OUTPUT_DIR = 'output/cvs_data_vids'
id=uuid.uuid4().hex

OUTPUT_DIR = os.path.join(OUTPUT_DIR, id)
create_dir(OUTPUT_DIR)


OUTPUT_DIR_AIRQ= os.path.join(OUTPUT_DIR, "airq")

cmd = f'python  cyprus_airquality.py -o {OUTPUT_DIR_AIRQ}'
os.system(cmd)