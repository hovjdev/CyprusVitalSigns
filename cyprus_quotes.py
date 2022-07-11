import os
import re
import json
import random
import argparse

from datetime import datetime
from PIL import Image


from tools.file_utils import create_dir, delete_previous_files
from tools.misc import create_texture_image, fit_text_in_shape


DIRNAME = os.path.dirname(__file__)
INPUT_DIR = os.path.join(DIRNAME, 'input', 'cyprus_quotes')
OUTPUT_DIR = os.path.join(DIRNAME, 'output', 'cyprus_quotes')
DO_INTRO=True


if __name__ == "__main__":

    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument("-o", "--output",  help = "Provide path to output forlder")


    # Read arguments from command line
    args = parser.parse_args()
   

    if args.output:
        OUTPUT_DIR=args.output



    print(f"OUTPUT_DIR =  {OUTPUT_DIR}")
    create_dir(OUTPUT_DIR)
    delete_previous_files(OUTPUT_DIR)


    output_image = os.path.join(OUTPUT_DIR, "quote_image.png")
    from PIL import Image
    width=1920*2
    height=1080*2
    img = Image.new('RGB', (width, height), (0,0,0, 0))
    img.putalpha(255)
    img.save(output_image)

    text=''

    try:
        assert os.path.exists(output_image)
    except Exception as e:
        print(str(e))
        exit(1)


 

    # load quotes
    data=None
    with  open(os.path.join(INPUT_DIR,  'quotes.json')) as f:
        data = json.load(f)

    count=0
    quote_text=""
    while quote_text == "" and count < 1000:
        count +=1
        quote = random.choice(data['quotes'])

        owner=quote['owner']
        quote_text=quote['quote']
        topic=quote['topic']
        author=quote['author']
        about=quote['about']
        citation=quote['citation']
        link=quote['link']
        publication=quote['publication']


    image = Image.open(output_image)
    imsize= image.size

    x1=-.05
    w=1-2*x1

    y1=.05
    y2=y1+.72
    y3=y2+0.15
    y4=y3+0.
    y5=y4+.08

    h1=y2-y1
    h2=y3-y2
    h3=y4-y3
    h4=y5-y4 

    print(f"h1:{h1}, h2:{h2}, h3:{h3}, h4:{h4}")


    try:
        assert round(1-y5, 4)==round(y1,4)
    except Exception as e:
        print(str(e))
        print(f"1-y5={1-y5}, y1={y1}")
    

    fit_text_in_shape(image=image, 
            x=int(imsize[0] * x1),
            y=int(imsize[1] * y1),
            w=int(imsize[0] * w),
            h=int(imsize[1] * h1 ),
            text='"'+quote_text+'"',
            font_file="input/fonts/bauhaus/BauhausBold.ttf")
    fit_text_in_shape(image=image, 
            x=int(imsize[0] * x1),
            y=int(imsize[1] * y2),
            w=int(imsize[0] * w),
            h=int(imsize[1] * h2),
            text="- " + author + " -",
            font_file="input/fonts/bauhaus/BauhausRegular.ttf")
    if False:
        fit_text_in_shape(image=image, 
            x=int(imsize[0] * x1),
                y=int(imsize[1] * y3),
                w=int(imsize[0] * w),
                h=int(imsize[1] * h3),
                text=about,
                font_file="input/fonts/bauhaus/BauhausRegular.ttf")    
    fit_text_in_shape(image=image, 
           x=int(imsize[0] * x1),
            y=int(imsize[1] * y4),
            w=int(imsize[0] * w),
            h=int(imsize[1] * h4),
            text=citation,
            font_file="input/fonts/bauhaus/BauhausRegular.ttf")
    if False:
        fit_text_in_shape(image=image, 
            x=int(imsize[0] * x1),
                y=int(imsize[1] * y5),
                w=int(imsize[0] * w),
                h=int(imsize[1] * y1 ),
                text=link,
                font_file="input/fonts/bauhaus/BauhausRegular.ttf")                                             
    image.save(output_image, "png")


    about = re.sub(r"\(.*?\)", "", about)


    if owner == "person":
        text = random.choice(["And now let's end "]) 
        text += random.choice(["with a quote ", "with a citation "])
        text += random.choice(["on the topic of ", "on the subject of "])
        text += topic + ". "
        text += random.choice(['By '])
        text += random.choice(["distinguished ", "esteemed ", "renowned ", "illustrious ", "acclaimed "])
        text += author + ". \n"
        text += about + "\n"
        text += author + " "
        text += random.choice(['said:\n', 'is quoted to say:\n'])
        text += quote_text

        text = text.replace(" Dr.", " Doctor ")
        text = text.replace(" Prof.", " Professor ")
    else:
        text = random.choice(["And now let's end "]) 
        text += random.choice(["with a quote ", "with a citation "])
        text += random.choice(["on the topic of ", "on the subject of "])
        text += topic + ". "
        text += random.choice(['By the '])
        text += author + ". \n"
        text += about + "\n"
        text += 'The ' + author + " "
        text += random.choice(['said in \n', 'is quoted to say in \n'])
        text += publication + ":\n"       
        text += quote_text
       


    textfile = output_image[:-4]+".txt"
    with open(textfile, 'w') as f:
        f.write(text)









