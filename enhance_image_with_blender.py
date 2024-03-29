import os
import argparse

DIRNAME = os.path.dirname(__file__)

BLENDER="blender"
IMAGE_PATH=""
OUTPUT_DIR=os.path.join(DIRNAME, "output", "blender")
INPUT_IMAGE=""
INPUT_BLENDER_FILE=os.path.join(DIRNAME, "input", "blender", "p1.blend")
INPUT_BLENDER_SCRIPT=os.path.join(DIRNAME, "input", "blender", "script1.py")
OUTPUT_IMAGE="frame_####.png"


OUTPUT_IMAGE = os.path.join(OUTPUT_DIR, OUTPUT_IMAGE)


DEBUG=True
BLENDER_DEBUG=">/dev/null 2>&1"
if DEBUG:
    BLENDER_DEBUG=""

if __name__ == "__main__":

    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument("-b", "--blend_file", help = "Provide path to blender file")
    parser.add_argument("-o", "--output", help = "Provide path to output image")
    parser.add_argument("-s", "--script", help = "Provide path to imput python script")


    # Read arguments from command line
    args = parser.parse_args()

    if args.blend_file:
        INPUT_BLENDER_FILE=args.blend_file

    if args.output:
        OUTPUT_IMAGE=args.output

    if args.script:
        INPUT_BLENDER_SCRIPT=args.script

    if INPUT_BLENDER_SCRIPT:
        cmd = f"{BLENDER} -b {INPUT_BLENDER_FILE} --python {INPUT_BLENDER_SCRIPT} -o {OUTPUT_IMAGE} -a {BLENDER_DEBUG}"
    else:
        cmd = f"{BLENDER} -b {INPUT_BLENDER_FILE} -o {OUTPUT_IMAGE} -a {BLENDER_DEBUG}"

    print(cmd)
    os.system(cmd)
