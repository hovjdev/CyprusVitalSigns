
import argparse
import requests
import json
import datetime
import os
import random
from unidecode import unidecode

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('Agg')

from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.font_manager as fm
import matplotlib.cm as cm
from pytz import timezone


from tools.file_utils import create_dir, delete_previous_files
from tools.plot_tools import get_cyprus_map

OUTPUT_DIR = 'output/cyprus_airquality'
DEBUG=False


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


    pollutants_list = [
    #{"code":  38, "label": "NO", "fullname" :"pollutant_38", "index":1, "color": 'lightgreen', "label_en": "Nitrogen monoxide (air)", "label_el":"Μονοξείδιο Αζώτου", "levels":[-1,-1,-1]},
    {"code": 8, "label": "NO₂", "fullname" :	"pollutant_8", "index":2 , "color": 'aqua', "label_en": "Nitrogen dioxide (air)", "label_el":"Διοξείδιο Αζώτου", "levels":[100, 150, 200]},
    #{"code": 9, "label": "NOx", "fullname" :"pollutant_9", "index":3, "color": 'violet' , "label_en": "Nitrogen oxides (air)", "label_el":"Οξείδια του Αζώτου", "levels":[-1,-1,-1]},
    #{"code": 1, "label": "SO₂", "fullname" :"pollutant_1", "index":4, "color": 'orange' , "label_en": "Sulphur dioxide (air)", "label_el":"Διοξείδιο Θείου", "levels":[-1,-1,-1]},
    {"code": 7, "label": "O₃", "fullname" :"pollutant_7", "index":5, "color": 'green', "label_en": "Ozone (air)", "label_el":"Όζον", "levels":[100,140,180]},
    {"code": 10, "label": "CO", "fullname" :"pollutant_10", "index":6, "color": 'gray' , "label_en": "Carbon monoxide (air)", "label_el":"Μονοξείδιο Άνθρακα", "levels":[7000,15000,20000]},
    #{"code": 5, "label": "PM₁₀", "fullname" :	"pollutant_5", "index":7, "color": 'blue' , "label_en": "Particulate matter less than 10 microns (aerosol)", "label_el":"Σωματίδια < 10 μm", "levels":[-1,-1,-1]},
    {"code": 6001, "label": "PM₂.₅", "fullname" :"pollutant_6001", "index":8 , "color": 'red', "label_en": "Particulate matter less than 2.5 microns (aerosol)", "label_el":"Σωματίδια < 2.5 μm", "levels":[25,50,100]},
    #{"code": 20, "label": "C₆H₆", "fullname" :	"pollutant_20", "index":9, "color": 'magenta' , "label_en": "Benzene (air)", "label_el":"Βενζόλιο", "levels":[-1,-1,-1]}
    ]


    stations_list = [
    {"code" : 1, "label": "NICTRA", "label_en":"Nicosia Traffic", "label_el":'Λευκωσία - Κυκλοφοριακός Σταθμός', "index":1, "color":"lightgreen", "long":33.382275, "lat":35.185566},
    #{"code" : 2, "label": "NICRES","label_en":"Nicosia Residential", "label_el":'Λευκωσία - Οικιστικός Σταθμός', "index":2, "color":"aqua", "long":33.382275, "lat":35.185566},
    {"code" : 3,"label": "LIMTRA", "label_en":"Limassol Traffic", "label_el":'Λεμεσός - Κυκλοφοριακός Σταθμός', "index":3, "color":"violet", "long":33.0413, "lat":34.6786},
    {"code" : 5,"label": "LARTRA", "label_en":"Larnaca Traffic", "label_el":'Λάρνακα - Κυκλοφοριακός Σταθμός', "index":4, "color":"green", "long":33.6201, "lat":34.9182},
    {"code" : 8, "label": "ZYGIND","label_en":"Zygi Industrial Station", "label_el":'Ζύγι - Βιομηχανικός Σταθμός', "index":5, "color":"red", "long":33.3333, "lat":34.7333},
    {"code" : 10,"label": "AYMRNA", "label_en":"Ayia Marina Background Station", "label_el":'Αγία Μαρίνα Ξυλιάτου - Σταθμός Υποβάθρου', "index":6, "color":"magenta", "long":33.0567, "lat":35.0492 },
    #{"code" : 9,"label": "MARIND", "label_en":"Mari Industrial Station", "label_el":'Μαρί - Βιομηχανικός Σταθμός', "index":7, "color":"gold", "long":33.2981002, "lat":34.7360593},
    {"code" : 7,"label": "PAFTRA", "label_en":"Paphos Traffic", "label_el":'Πάφος - Κυκλοφοριακός Σταθμός', "index":8, "color":"blue", "long":32.4218, "lat":34.7754},
    {"code" : 11,"label": "PARTRA", "label_en":"Paralimnni Traffic", "label_el":'Παραλίμνι - Κυκλοφοριακός Σταθμός', "index":9, "color":"black", "long":33.9823, "lat":35.0380},
    #{"code" : 12,"label": "KALIND", "label_en":"Kalavasos Industrial Station", "label_el":'Καλαβασός Βιομηχανικός Σταθμός', "index":10, "color":"olive", "long":33.30798, "lat":34.7584},
    {"code" : 13,"label": "ORMIND", "label_en":"Ormidia Industrial Station", "label_el":'Ορμήδια Βιομηχανικός', "index":11, "color":"skyblue", "long":33.7803, "lat":34.9925},
    ]


    create_dir(OUTPUT_DIR)
    delete_previous_files(OUTPUT_DIR)

    date_time = None
    for counter, p in enumerate(pollutants_list):

        pollutant_label= p['label']
        pollutant_label=unidecode(pollutant_label)
        pollutant_code= p['code']
        pollutant_fullname=p['fullname']
        pollutant_label_en=p['label_en'].split("(")[0]
        pollutant_levels=p["levels"]

        m, figure, axes =get_cyprus_map()

        tz = timezone('EET')
        now =datetime.datetime.now(tz)
        ytd = now - datetime.timedelta(days=1)

        #air_quality = { 'good':[], 'moderate':[],  'unhealthy':[], 'toxic':[] }
        air_quality = {}

        xs=[]
        ys=[]
        for s in stations_list:
            lat=s['lat']
            lon=s['long']
            code = s['code']
            label_en=s['label_en']
            label_en = label_en.split(' ')[0]  
            x, y = m(lon, lat)



            url=f"https://www.airquality.dli.mlsi.gov.cy/station_data/{code}/{ytd.year}-{ytd.month}-{ytd.day}:{ytd.hour}/{now.year}-{now.month}-{now.day}:{now.hour}"
            if DEBUG:
                print(url)
            res = requests.get(url)
            res = res.json()
            if DEBUG:
                print(res)

            pollution=''
            try:
                k=list(res['data'].keys())[-1]
                pollution=res['data'][k][pollutant_fullname]
                pollution=round(float(pollution))
                date_time=res['data'][k]['date_time']
            except Exception as e:
                print(str(e))


            if not pollution:
                continue

            xs.append(x)
            ys.append(y)

            text = f"{label_en}"

            plt.plot(x, y, marker="o", color="grey")

            plt.text(
                    x,
                    y-.01,
                    text,
                    color='black',
                    fontsize=40,
                    horizontalalignment='center',
                    verticalalignment='top',
                    zorder=6,
                )

            fp=float(pollution)
            if fp>= 0 and fp <pollutant_levels[0]:
                color="green"
                if 'good' not in air_quality:
                    air_quality['good']=[]
                air_quality['good'].append(label_en)
            if fp>= pollutant_levels[0] and fp < pollutant_levels[1]:
                color="orange"
                if 'moderate' not in air_quality:
                    air_quality['moderate']=[]
                air_quality['moderate'].append(label_en)
            if fp>= pollutant_levels[1] and fp < pollutant_levels[2]:
                color="red"
                if 'unhealthy' not in air_quality:
                    air_quality['unhealthy']=[]
                air_quality['unhealthy'].append(label_en)
            if fp>= pollutant_levels[2]:
                color="purple"
                if 'toxic' not in air_quality:
                    air_quality['toxic']=[]
                air_quality['toxic'].append(label_en)

            plt.text(
                    x,
                    y+.002,
                    pollution,
                    color=color,
                    fontsize=70,
                    horizontalalignment='center',
                    verticalalignment='bottom',
                    zorder=6,
                    weight="bold"
                )


        m.scatter(
            xs,
            ys,
            s=100,  # size
            c='black',  # color
            marker='o',  # symbol
            alpha=0.5,  # transparency
            zorder=2,  # plotting order
        )

        plt.title(f"Air Quality in Cyprus: {pollutant_label}", fontsize = 60, y=1.0, pad=-90)


        cmap = mpl.colors.ListedColormap(['green', 'green', 'orange', 'orange', 'red', 'red', 'purple', 'purple'])
        bounds = [0, 
                pollutant_levels[0]/2, 
                pollutant_levels[0] , 
                (pollutant_levels[0]+pollutant_levels[1])/2, 
                pollutant_levels[1],
                (pollutant_levels[1]+pollutant_levels[2])/2,
                pollutant_levels[2],
                (pollutant_levels[2]+pollutant_levels[2]*1.2)/2,
                pollutant_levels[2]*1.2]
        labels = [ 
                "Good",
                pollutant_levels[0] , 
                "Moderate",
                pollutant_levels[1],
                "Unhealthy",  
                pollutant_levels[2],
                "Toxic"]              
        ticks = bounds[1:-1]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)


        cb=m.colorbar( cmap=cmap,norm=norm, location="left",
            boundaries= bounds,
            ticks=ticks,
            spacing='proportional',
            fraction=0.046, pad=0)

        cb.ax.set_yticklabels(labels, va="center")
        cb.ax.tick_params(size=0)


        for i, t in enumerate(cb.ax.get_yticklabels()):
            t.set_fontsize(40)
            t.set_rotation(90)
            if i%2 == 0:
                t.set_rotation(90)
                t.set_fontsize(30)
                t.set_x(t._x-.7)


        # data source
        plt.text(0.01, 0.02, date_time, ha='left', va='center', transform=axes.transAxes, fontsize=30)
        
        # data source
        plt.text(.99, .02, 'data: https://www.airquality.dli.mlsi.gov.cy/', ha='right', va='center', transform=axes.transAxes, fontsize=30)


        png_file = os.path.join(OUTPUT_DIR, f'{counter}_airquality_{pollutant_code}.png')
        plt.savefig(png_file, bbox_inches='tight', dpi='figure',pad_inches=-.05)


        tmp = []
        for a in air_quality:
            tmp.append({'quality':a, 'locations':air_quality[a]})
        tmp = sorted(tmp, key=lambda d: len(d['locations']), reverse=True)


        def replace_last(string, find, replace):
            reversed = string[::-1]
            replaced = reversed.replace(find[::-1], replace[::-1], 1)
            return replaced[::-1]


        text_file = os.path.join(OUTPUT_DIR, f'{counter}_airquality_{pollutant_code}.txt')
        with open(text_file, "w") as f:
            if counter == 0:
                first=random.choice([
                                "Let's review ", 
                                "Let's take a look at ", 
                                "Let's review the data for "])
                f.write(f"{first}the air quality in Cyprus.\n")

            for t in tmp:
                if len(t['locations'])>0:
                    locations = t['locations']
                    locations = [f'"{l}"' for l in locations]
                    only_one_location=False
                    if len(locations)==1:
                        only_one_location=True
                    locations_joined = ', '.join(locations)
                    if len(locations) > 1:   
                        locations_joined = replace_last(locations_joined, ', ', ' and ')
                    
                    first=random.choice(["Today, ", "Now, ", "", "", "", ""])
                    levels=random.choice(["levels", "levels", "measurements", "concentrations"])
                    cities=random.choice(["in the following cities: ", "in these locations: ", "in", "in"])
                    if only_one_location:
                        cities="in"
                    quality = t['quality']
                    last=[f"{cities} {locations_joined}"]
                    if len(air_quality) == 1:
                        last=[f"in all measured locations", 
                                "throughout Cyprus", 
                                "all places", 
                                "across the island", 
                                "across Cyprus"]
                    last=random.choice(last)
                    f.write(f'{first}{pollutant_label_en} {levels} are {quality} {last}.\n')

