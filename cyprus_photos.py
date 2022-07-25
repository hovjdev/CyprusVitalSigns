import os
import urllib
import cv2
import random
import ast
import argparse
import pytz
import datetime

import flickrapi


from tqdm import tqdm

from tools.file_utils import create_dir, delete_previous_files

from local_settings import FLICKR_KEY, FLICKR_SECRET

OUTPUT_DIR = 'output/cyprus_photos'
BBOX = "32.1,34.45,34.72,35.75"
NB_DAYS=700
USE_KDE_METHOD=True
NB_FLICKR_FETCHES=5
KERNEL_DENSITY_BANDWIDTH=1
DEBUG=False
NB_PHOTOS=24

def create_photo_display(output_dir=OUTPUT_DIR,
                      api_key = FLICKR_KEY,
                      secret_api_key = FLICKR_SECRET,
                      min_taken_date=None,
                      text="",
                      bbox=BBOX,
                      accuracy=12):

    flickr = flickrapi.FlickrAPI(api_key, secret_api_key)


    def get_data(page=1, text=text, min_taken_date=min_taken_date,bbox=bbox, accuracy=accuracy):
        byte_str = flickr.photos.search(
                text=text, 
                format="json",
                extras='url_c', 
                has_geo=False,
                page=page, 
                min_taken_date=min_taken_date,
                bbox=bbox,
                per_page=500,
                accuracy=accuracy,
                content_type=1,
                safe_search=1,
                privacy_filter=1,
            )
        dict_str = byte_str.decode("UTF-8")
        data = ast.literal_eval(dict_str)
        return data


    photos_fetched=[]
    N=10000
    for _ in tqdm(range(NB_FLICKR_FETCHES)): # to get more consistent data iterate NB_FLICKR_FETCHES times
        try:
            data = get_data()
            pages = data['photos']['pages']
            for page in tqdm(range(1,pages+1)):
                data = get_data(page=page)
                photos = data['photos']['photo']
                for photo in photos:
                    #print(photo)
                    photos_fetched.append(photo)
                    #if len(photos_fetched) > N * NB_PHOTOS:
                    #    break
                if len(photos_fetched) > N * NB_PHOTOS:
                    break
            if len(photos_fetched) > N * NB_PHOTOS:
                break                
        except Exception as e:
            print(str(e))
            continue

        if len(photos_fetched) > N * NB_PHOTOS:
            break  

    print(f"found {len(photos_fetched)} photos")
    #print(photos_selected)
    random.shuffle(photos_fetched)

    # download photos
    photos=photos_fetched[:NB_PHOTOS]
    photo_files=[]
    for count, photo in enumerate(photos):
        photo_file=os.path.join(output_dir, "photo_" + str(count) +".jpg")
        #print(f'Downloading: {photo}')
        try:
            url=photo.get('url_c')
            url = url.replace('\\', '')
            #print(f"url: {url}")
            
            urllib.request.urlretrieve(url, photo_file)
            photo_files.append(photo_file)
        except Exception as e:
            print(str(e))
            print('failed to download image')

    # blur peopple and faces
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    for photo_file in photo_files:

        image = cv2.imread(photo_file)
        h, w = image.shape[:2]
        kernel_width = (w//7) | 1
        kernel_height = (h//7) | 1
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(image, scaleFactor=1.02, minNeighbors=3)

        for x, y, w, h in faces:
            face_roi = image[y:y+h, x:x+w]
            blurred_face = cv2.GaussianBlur(face_roi, (kernel_width, kernel_height), 0)
            image[y:y+h, x:x+w] = blurred_face


        winStride=(4,4)
        padding=(32,32)
        meanShift=-1
        scale=1.05
        (rects, weights) = hog.detectMultiScale(image, winStride=winStride,
	            padding=padding, scale=scale, useMeanshiftGrouping=meanShift)

 
        for x, y, w, h in rects:
            face_roi = image[y:y+h, x:x+w]
            blurred_face = cv2.GaussianBlur(face_roi, (kernel_width, kernel_height), 0)
            image[y:y+h, x:x+w] = blurred_face

        cv2.imwrite(photo_file, image)




if __name__ == "__main__":

    # Initialize parser
    parser = argparse.ArgumentParser()
    
    # Adding optional argument
    parser.add_argument("-o", "--output", help = "Provide path to output forlder")
    
    # Read arguments from command line
    args = parser.parse_args()
    
    if args.output:
        OUTPUT_DIR=args.output
    
    print(f"OUTPUT_DIR =  {OUTPUT_DIR}")

    create_dir(OUTPUT_DIR)
    delete_previous_files(OUTPUT_DIR)

    output_dir=OUTPUT_DIR
    api_key = FLICKR_KEY
    secret_api_key = FLICKR_SECRET



    tz = pytz.timezone('EET')
    now =datetime.datetime.now(tz)
    nb_days=NB_DAYS
    min_taken_date = now  - datetime.timedelta(days=nb_days)
    min_taken_date=min_taken_date.strftime("%Y-%m-%d")
    print(min_taken_date)

    places = ['paphos', 'nicosia', 'limassol', 'protaras', 'troodos']
    text=random.choice(places)

    output_image_file = create_photo_display(output_dir=OUTPUT_DIR,
                      api_key = FLICKR_KEY,
                      secret_api_key = FLICKR_SECRET,
                      min_taken_date=min_taken_date,
                      text=text,
                      bbox=BBOX)

