import os
import argparse


BLENDER="blender"
IMAGE_PATH=""
OUTPUT_DIR="output/blender"
INPUT_IMAGE=""
INPUT_BLENDER_FILE="input/blender/p1.blend"
INPUT_BLENDER_SCRIPT="input/blender/script1.py"
OUTPUT_IMAGE="frame_####.png"


OUTPUT_IMAGE = os.path.join(OUTPUT_DIR, OUTPUT_IMAGE)


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
        cmd = f"{BLENDER} -b {INPUT_BLENDER_FILE} --python {INPUT_BLENDER_SCRIPT} -o {OUTPUT_IMAGE} -a"
    else:
        cmd = f"{BLENDER} -b {INPUT_BLENDER_FILE} -o {OUTPUT_IMAGE} -a"

    os.system(cmd)
