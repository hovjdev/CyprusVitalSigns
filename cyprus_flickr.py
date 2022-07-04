import os
import ast
import argparse
import pytz
import datetime

import flickrapi

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('Agg')

from scipy.stats.kde import gaussian_kde


from tqdm import tqdm

from tools.file_utils import create_dir, delete_previous_files
from tools.plot_tools import get_cyprus_map

from local_settings import FLICKR_KEY, FLICKR_SECRET

OUTPUT_DIR = 'output/cyprus_flickr'
BBOX = "32.1,34.45,34.72,35.75"
NB_DAYS=365/2

def create_flickr_map(output_dir=OUTPUT_DIR,
                      api_key = FLICKR_KEY,
                      secret_api_key = FLICKR_SECRET,
                      min_taken_date=None,
                      tags="",
                      bbox=BBOX):

    flickr = flickrapi.FlickrAPI(api_key, secret_api_key)


    def get_data(page=1, tags=tags, min_taken_date=min_taken_date,bbox=bbox):
        byte_str = flickr.photos.search(
                tags=tags, 
                format="json", extras=["geo"], 
                has_geo=True,
                page=page, 
                min_taken_date=min_taken_date,
                bbox=bbox)
        dict_str = byte_str.decode("UTF-8")
        data = ast.literal_eval(dict_str)
        return data

    data = get_data()
    pages = data['photos']['pages']

    lats = []
    longs = []

    for page in tqdm(range(1,pages+1)):
        data = get_data(page=page)
        photos = data['photos']['photo']
        for photo in photos:
            lat = photo['latitude']
            long = photo['longitude']

            #print(lat, long)

            lats.append(float(lat))
            longs.append(float(long))

    assert len(lats) == len(longs)
    print(f"found {len(lats)} localized photos")

    m, figure, axes=get_cyprus_map()

    xs=[]
    ys=[]
    for lat, long in zip(lats, longs):
        x, y = m(long, lat)
        xs.append(x)
        ys.append(y)

    k = gaussian_kde(np.vstack([xs, ys]))
    zs= k(np.vstack([xs, ys]))

    m.scatter(
        xs,
        ys,
        s=1000,  # size
        c=zs,  # color
        cmap="autumn_r",
        marker='o',  # symbol
        alpha=0.3,  # transparency
        zorder=2,  # plotting order
        )



    cities = {
        "Nicosia":{"long":33.382275, "lat":35.185566},
        "Limassol":{"long":33.0413, "lat":34.6786},
        "Larnaca":{"long":33.6201, "lat":34.9182},
        #"Strovolos":{"long":33.3598, "lat": 35.1338},
        #"Famagusta":{"long":33.623172, "lat":34.900253},
        "Paphos":{"long":32.4218, "lat":34.7754},
        "Kyrenia":{"long":33.3167, "lat":35.3417},
        "Protaras":{"long":34.0542, "lat":35.015},
        "Pergamos":{"long":33.6959, "lat":35.0487},
        "Morfou":{"long":32.9776, "lat":35.2123},
        #"Aradippou":{"long":33.59, "lat":34.9528},
        #"Paralimnni":{"long":33.9823, "lat":35.0380},
        #"Zygi":{"long":33.3333, "lat":34.7333},
        #"Ayia":{"long":33.0567, "lat":35.0492 },
        #"Ormidia":{"long":33.7803, "lat":34.9925},
        "Rizokarpaso":{"long":34.408730, "lat":35.617683},
    }

    xs=[]
    ys=[]
    concetrations=[]
    for current_city in cities:
        long = cities[current_city]['long']
        lat = cities[current_city]['lat']
        x, y = m(long, lat)
        plt.text(
            x,
            y-.015,
            current_city,
            color='black',
            fontsize=40,
            horizontalalignment='center',
            verticalalignment='top',
            zorder=6,
        )
        xs.append(x)
        ys.append(y)
        concentration = k([x,y])
        concetrations.append({'concentration':concentration, 'name':current_city})



    m.scatter(
        xs,
        ys,
        s=100,  # size
        c='black',  # color
        marker='o',  # symbol
        alpha=0.5,  # transparency
        zorder=2,  # plotting order
    )

    # Dates label
    now =datetime.datetime.now(tz)
    today=datetime.datetime.now(tz=tz).strftime("%A %d, %B %Y")
    nb_days=NB_DAYS
    from_date = now  - datetime.timedelta(days=nb_days)
    from_date = from_date.strftime("%A %d, %B %Y")

    figure.text(
        .8,
        .17,
        f"From {from_date}  to  {today}",
        color='black',
        fontsize=20,
        horizontalalignment='center',
        verticalalignment='top',
        zorder=6,
    )

    output_image_file = os.path.join(output_dir, "flickr_photo_map.png")
    plt.title(f"Cyprus tourism concentration", fontsize = 60, y=1.0, pad=-90)
    plt.savefig(output_image_file, bbox_inches='tight', dpi='figure',pad_inches=-.05)
    plt.close('all')



    output_text_file = os.path.join(output_dir, "flickr_photo_map.txt")
    concetrations = sorted(concetrations, key=lambda d: d['concentration'], reverse=True)
    locations = f"{concetrations[0]['name']}, {concetrations[1]['name']} and {concetrations[2]['name']}"

    with open(output_text_file, "w") as f:
        f.write("And now, let's take a look at places where tourists have been concentrating in the last 6 months.\n")
        f.write(f"The map of geotagged photo locations shows that tourists have been concentrating the most in {locations}.\n")

    


    if os.path.exists(output_image_file):
        return output_image_file

    return None



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

    output_image_file = create_flickr_map(output_dir=OUTPUT_DIR,
                      api_key = FLICKR_KEY,
                      secret_api_key = FLICKR_SECRET,
                      min_taken_date=min_taken_date,
                      tags="",
                      bbox=BBOX)

