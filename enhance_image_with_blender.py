import os

BLENDER="blender"
IMAGE_PATH=""
OUTPUT_DIR="output/blender"
INPUT_IMAGE=""
INPUT_BLENDER_FILE="input/blender/p1.blend"
INPUT_BLENDER_SCRIPT="input/blender/script1.py"
OUTPUT_IMAGE="frame_####.png"

cmd = f"{BLENDER} -b {INPUT_BLENDER_FILE} --python {INPUT_BLENDER_SCRIPT} -o {OUTPUT_DIR}/{OUTPUT_IMAGE} -a"
os.system(cmd)
