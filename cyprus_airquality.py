
import argparse
import requests
import json
import datetime
import os
import shutil
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

OUTPUT_DIR = 'output/cyprus_airquality'


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


    ratio = 720.0 / 1280.0 * 1.0
    width = 1660.0

    MYDPI = float(plt.gcf().get_dpi())
    FIGSIZE = (width / MYDPI, width * ratio / MYDPI)


    create_dir(OUTPUT_DIR)
    delete_previous_files(OUTPUT_DIR)

    date_time = None
    for p in pollutants_list:

        pollutant_label= p['label']
        pollutant_label=unidecode(pollutant_label)
        pollutant_code= p['code']
        pollutant_fullname=p['fullname']
        pollutant_label_en=p['label_en'].split("(")[0]
        pollutant_levels=p["levels"]

        #figure = plt.figure(figsize=FIGSIZE, dpi=MYDPI)
        figure, axes = plt.subplots(1, 1, figsize=FIGSIZE, dpi=MYDPI)
        fm.fontManager.addfont("input/fonts/bauhaus/BauhausRegular.ttf")
        plt.rcParams['font.family'] = 'Bauhaus'

        m = Basemap(llcrnrlat=34.45, urcrnrlat=35.75,
                    llcrnrlon=32.1, urcrnrlon=34.72,
                    epsg=4230,
                    projection='cyl',
                    resolution='c',
                    ax=axes)


        m.drawcoastlines(color='#6D5F47', linewidth=.4)
        m.drawcountries(color='#6D5F47', linewidth=.4)

        m.drawmeridians(np.arange(-180, 180, 10), color='#bbbbbb')
        m.drawparallels(np.arange(-90, 90, 10), color='#bbbbbb')
        m.arcgisimage(
            server='https://server.arcgisonline.com/arcgis',
            service='World_Shaded_Relief', xpixels = 3500, dpi=500, verbose= True)
        #m.bluemarble(scale=8)
        #m.etopo(scale=10, alpha=0.5)

        tz = timezone('EET')
        now =datetime.datetime.now(tz)
        ytd = now - datetime.timedelta(days=1)

        air_quality = { 'good':[], 'moderate':[],  'unhealthy':[], 'toxic':[] }

        for s in stations_list:
            lat=s['lat']
            lon=s['long']
            code = s['code']
            label_en=s['label_en']
            label_en = label_en.split(' ')[0]  
            x, y = m(lon, lat)

            url=f"https://www.airquality.dli.mlsi.gov.cy/station_data/{code}/{ytd.year}-{ytd.month}-{ytd.day}:{ytd.hour}/{now.year}-{now.month}-{now.day}:{now.hour}"
            print(url)
            res = requests.get(url)
            res = res.json()
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

            text = f"{label_en}"

            plt.plot(x, y, marker="o", color="grey")

            plt.text(
                    x,
                    y-.01,
                    text,
                    color='black',
                    fontsize=20,
                    horizontalalignment='center',
                    verticalalignment='top',
                    zorder=6,
                )

            fp=float(pollution)
            if fp>= 0 and fp <pollutant_levels[0]:
                color="green"
                air_quality['good'].append(label_en)
            if fp>= pollutant_levels[0] and fp < pollutant_levels[1]:
                color="orange"
                air_quality['moderate'].append(label_en)
            if fp>= pollutant_levels[1] and fp < pollutant_levels[2]:
                color="red"
                air_quality['unhealthy'].append(label_en)
            if fp>= pollutant_levels[2]:
                color="purple"
                air_quality['toxic'].append(label_en)

            plt.text(
                    x,
                    y+.01,
                    pollution,
                    color=color,
                    fontsize=40,
                    horizontalalignment='center',
                    verticalalignment='bottom',
                    zorder=6,
                    weight="bold"
                )

            plt.title(f"Air Quality in Cyprus: {pollutant_label}", fontsize = 30, y=1.0, pad=-45)


        cmap = mpl.colors.ListedColormap(['green', 'green', 'orange', 'orange', 'red', 'red', 'purple', 'purple'])
        bounds = [0, 
                pollutant_levels[0]/2, 
                pollutant_levels[0] , 
                (pollutant_levels[0]+pollutant_levels[1])/2, 
                pollutant_levels[1],
                (pollutant_levels[1]+pollutant_levels[2])/2,
                pollutant_levels[2],
                (pollutant_levels[2]+pollutant_levels[2]*1.4)/2,
                pollutant_levels[2]*1.3]
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
            t.set_fontsize(20)
            t.set_rotation(90)
            if i%2 == 0:
                t.set_rotation(90)
                t.set_fontsize(15)
                t.set_x(t._x-.7)


        plt.text(0.06, 0.02,date_time, ha='center', va='center', transform=axes.transAxes)


        png_file = os.path.join(OUTPUT_DIR, f'airquality_{pollutant_code}.png')
        plt.savefig(png_file, bbox_inches='tight', dpi='figure',pad_inches=-.05)


        tmp = []
        for a in air_quality:
            tmp.append({'quality':a, 'locations':air_quality[a]})
        tmp = sorted(tmp, key=lambda d: len(d['locations']), reverse=True)


        text_file = os.path.join(OUTPUT_DIR, f'airquality_{pollutant_code}.txt')
        with open(text_file, "w") as f:
            for t in tmp:
                if len(t['locations'])>0:
                    locations = ', '.join(t['locations'])
                    f.write(f"{pollutant_label_en} levels are {t['quality']} in {locations}\n")

