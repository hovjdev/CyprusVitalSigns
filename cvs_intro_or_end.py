import os
import pytz
import argparse

from datetime import datetime
from PIL import Image


from tools.file_utils import create_dir, delete_previous_files
from tools.misc import create_texture_image, fit_text_in_shape


OUTPUT_DIR = 'output/cvs_intro'
DO_INTRO=True


if __name__ == "__main__":

    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument("-o", "--output",  help = "Provide path to output forlder")
    parser.add_argument("-t", "--type",  help = "type: intro or end (default is intro)")


    # Read arguments from command line
    args = parser.parse_args()
   
    if args.type:
        if args.type=="end":
            DO_INTRO=False
            OUTPUT_DIR = 'output/cvs_end'

    if args.output:
        OUTPUT_DIR=args.output



    print(f"OUTPUT_DIR =  {OUTPUT_DIR}")
    create_dir(OUTPUT_DIR)
    delete_previous_files(OUTPUT_DIR)


    output_image = create_texture_image(dir_path=OUTPUT_DIR)
    text=''

    try:
        assert os.path.exists(output_image)
    except Exception as e:
        print(str(e))
        exit(1)


    if DO_INTRO:
        tz = pytz.timezone('EET')

        text="Cyprus Vital Signs\n"
        today=datetime.now(tz=tz).strftime("%Y-%m-%d")
        image = Image.open(output_image)
        imsize= image.size
        fit_text_in_shape(image=image, 
                x=int(imsize[0] * -0.1),
                y=int(imsize[1] * 0.4),
                w=int(imsize[0] * 1.2),
                h=int(imsize[1] * 0.23 ),
                text=text,
                font_file="input/fonts/bauhaus/BauhausBold.ttf")
        fit_text_in_shape(image=image, 
                x=int(imsize[0] * 0.3),
                y=int(imsize[1] * 0.9),
                w=int(imsize[0] * 0.4),
                h=int(imsize[1] * 0.1),
                text=today,
                font_file="input/fonts/bauhaus/BauhausRegular.ttf")            
        image.save(output_image, "png")


        dstr= now = datetime.now(tz=tz).strftime("%A %d, %B %Y")
        text = "This is the Cholo weather report for " + dstr + '.\n'
        text="This is the Cyprus Vital signs report, for:\n"
        text+=dstr
    else:
        text=''


    textfile = output_image[:-4]+".txt"
    with open(textfile, 'w') as f:
        f.write(text)









