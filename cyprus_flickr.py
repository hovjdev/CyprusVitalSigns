import os
import math
import random
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
from sklearn.neighbors import KernelDensity



from tqdm import tqdm

from tools.file_utils import create_dir, delete_previous_files
from tools.plot_tools import get_cyprus_map

from local_settings import FLICKR_KEY, FLICKR_SECRET

OUTPUT_DIR = 'output/cyprus_flickr'
BBOX = "32.1,34.45,34.72,35.75"
NB_DAYS=365 #365
USE_KDE_METHOD=True
NB_FLICKR_FETCHES=5
KERNEL_DENSITY_BANDWIDTH=1
DEBUG=False

def create_flickr_map(output_dir=OUTPUT_DIR,
                      api_key = FLICKR_KEY,
                      secret_api_key = FLICKR_SECRET,
                      min_taken_date=None,
                      tags="",
                      bbox=BBOX,
                      accuracy=12):

    flickr = flickrapi.FlickrAPI(api_key, secret_api_key)


    def get_data(page=1, tags=tags, min_taken_date=min_taken_date,bbox=bbox, accuracy=accuracy):
        byte_str = flickr.photos.search(
                tags=tags, 
                format="json", 
                extras="geo", 
                has_geo=True,
                page=page, 
                min_taken_date=min_taken_date,
                bbox=bbox,
                accuracy=accuracy)
        dict_str = byte_str.decode("UTF-8")
        data = ast.literal_eval(dict_str)
        return data



    lats = []
    longs = []
    for _ in tqdm(range(NB_FLICKR_FETCHES)): # to get more consistent data iterate NB_FLICKR_FETCHES times
        try:
            data = get_data()
            pages = data['photos']['pages']
            for page in tqdm(range(1,pages+1)):
                data = get_data(page=page)
                photos = data['photos']['photo']
                for photo in photos:
                    lat = photo['latitude']
                    long = photo['longitude']

                    #print(lat, long)

                    lats.append(float(lat))
                    longs.append(float(long))
        except Exception as e:
            print(str(e))
            continue

    assert len(lats) == len(longs)
    print(f"found {len(lats)} localized photos")

    m, figure, axes=get_cyprus_map()

    xxs=[]
    yys=[]
    zzs=[]
    sizes=[]
    xmin=1e9
    ymin=1e9
    xmax=-1e9
    ymax=-1e9
    for lat, long in zip(lats, longs):
        x, y = m(long, lat)
        if x>xmax: xmax=x
        if y>ymax: ymax=y
        if x<xmin: xmin=x
        if y<ymin: ymin=y        

        x += random.randint(-100, 100)/20000 # jitter
        y += random.randint(-100, 100)/20000 # jitter

        xxs.append(x)
        yys.append(y)

    noise_n=1000
    if USE_KDE_METHOD:
        tmp_xxs = np.random.uniform(low=xmin, high=xmax, size=(noise_n,)).tolist() # noise
        tmp_yys = np.random.uniform(low=ymin, high=ymax, size=(noise_n,)).tolist() # noise
        tmp_xxs.extend(xxs)
        tmp_yys.extend(yys)
        k = gaussian_kde(np.vstack([tmp_xxs, tmp_yys]), bw_method='silverman')
        if DEBUG:
            xxs=tmp_xxs
            yys=tmp_yys
        density=k(np.vstack([xxs, yys])).flatten()
        zzs.extend(density.tolist())
    else:
        tmp_xxs = np.random.uniform(low=xmin, high=xmax, size=(noise_n,)).tolist() # noise
        tmp_yys = np.random.uniform(low=ymin, high=ymax, size=(noise_n,)).tolist() # noise
        tmp_xxs.extend(xxs)
        tmp_yys.extend(yys)
        kde = KernelDensity(
            bandwidth=KERNEL_DENSITY_BANDWIDTH, metric="haversine", kernel="gaussian", algorithm="ball_tree"
        )
        tmpx=np.vstack([tmp_xxs, tmp_yys]).T
        #print(f"tmpx.shape: {tmpx.shape}")
        kde.fit(tmpx)
        if DEBUG:
            xxs=tmp_xxs
            yys=tmp_yys        
        tmpx=np.vstack([xxs, yys]).T            
        zzs.extend(kde.score_samples(tmpx).tolist())

    sizes=[500]*len(xxs)

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

    clouds_x=[]
    clouds_y=[]
    clouds_concentration=[] 
    concentrations=[]

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

        dist_facor=100
        concentration=[]
        a=[]        
        nb_cloud_points=100
        if USE_KDE_METHOD:
            for _ in range(nb_cloud_points):
                r=random.randint(0,dist_facor)/1000
                ang=random.randint(0,1000)/30
                a_=[x+r*math.cos(ang), y+r*math.sin(ang)]
                a.append(a_)
                tmp=k(a_)
                concentration.append(tmp)
            a=np.array(a)      
            concentration = np.array(concentration).flatten()
            concentrations.append({'concentration':concentration.mean(), 'name':current_city})                 
        else:
            for _ in range(nb_cloud_points):
                r=random.randint(0,dist_facor)/1000
                ang=random.randint(0,1000)/30
                a.append([x+r*math.cos(ang), y+r*math.sin(ang)])
            a=np.array(a)
            concentration=kde.score_samples(a)
            #print(f"concentration.shape: {concentration.shape}")
            concentrations.append({'concentration':concentration.mean(), 'name':current_city})

        if DEBUG:
            clouds_x.extend(a[:,0].tolist())
            clouds_y.extend(a[:,1].tolist())
            clouds_concentration.extend(concentration.tolist())

  

    if DEBUG:
        xxs.extend(clouds_x)
        yys.extend(clouds_y)
        zzs.extend(clouds_concentration)
        sizes.extend([100]*len(clouds_x))
  

    zzs = np.array(zzs)
    low=np.percentile(zzs, 5)
    high=np.percentile(zzs, 50)
    zzs[zzs<low]=low
    zzs[zzs>high]=high
    zzs=zzs.tolist()


    m.scatter( #data
        xxs,
        yys,
        s=sizes,  # size
        c=zzs,  # color
        cmap="RdYlBu_r",
        marker='o',  # symbol
        alpha=0.4,  # transparency
        zorder=2,  # plotting order
        )

    m.scatter( # cities
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


    # date
    plt.text( .01, .02, f"From {from_date}, to {today}", ha='left', va='center', transform=axes.transAxes, fontsize=30)

    # data source
    plt.text(.99, .02, 'data: https://flickr.com/', ha='right', va='center', transform=axes.transAxes, fontsize=30)

    output_image_file = os.path.join(output_dir, "flickr_photo_map.png")
    plt.title(f"Cyprus tourism concentration", fontsize = 60, y=1.0, pad=-90)
    plt.savefig(output_image_file, bbox_inches='tight', dpi='figure',pad_inches=-.05)
    plt.close('all')



    output_text_file = os.path.join(output_dir, "flickr_photo_map.txt")
    concentrations = sorted(concentrations, key=lambda d: d['concentration'], reverse=True)
    print(f"concentrations: {concentrations}")

    locations = f"{concentrations[0]['name']}, {concentrations[1]['name']}, {concentrations[2]['name']} and {concentrations[3]['name']}"

    first = random.choice([
        "concentrating",
        "gathering",
    ])

    second = random.choice([
        "shows",
        "indicates",
    ])

    third = random.choice([
        "concentrating",
        "gathering",
    ])    

    with open(output_text_file, "w") as f:
        AA=random.choice([
            "And now, let's take a look at",
            "Let's continue by examining",
            "Next, we shall look at",
            "Let's discuss"
        ])
        f.write(f"{AA} places where tourists have been {first} over the last {round(NB_DAYS/30.5)} months.\n")
        f.write(f"The map of geotagged photo locations {second} that tourists have been {third} the most in {locations}.\n")


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

