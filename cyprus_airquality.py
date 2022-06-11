
import requests
import json
import datetime
import os
import shutil

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
#mpl.use('Agg')

from mpl_toolkits.basemap import Basemap
from pytz import timezone

OUTPUT_DIR = 'output/cyprus_airquality'


def create_dir(path):
    created=False
    try:
        if not os.path.isdir(path):
            os.mkdir(path)
            created=True
    except Exception as e:
        print(str(e))
    return created

def delete_previous_files(path):
    try:
        if os.path.isdir(path):
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {str(e)}')
    except Exception as e:
        print(str(e))
    return



pollutants_list = [
{"code":  38, "label": "NO", "fullname" :"pollutant_38", "index":1, "color": 'lightgreen', "label_en": "Nitrogen monoxide (air)", "label_el":"Μονοξείδιο Αζώτου"},
{"code": 8, "label": "NO₂", "fullname" :	"pollutant_8", "index":2 , "color": 'aqua', "label_en": "Nitrogen dioxide (air)", "label_el":"Διοξείδιο Αζώτου"},
{"code": 9, "label": "NOx", "fullname" :"pollutant_9", "index":3, "color": 'violet' , "label_en": "Nitrogen oxides (air)", "label_el":"Οξείδια του Αζώτου"},
{"code": 1, "label": "SO₂", "fullname" :"pollutant_1", "index":4, "color": 'orange' , "label_en": "Sulphur dioxide (air)", "label_el":"Διοξείδιο Θείου"},
{"code": 7, "label": "O₃", "fullname" :"pollutant_7", "index":5, "color": 'green', "label_en": "Ozone (air)", "label_el":"Όζον"},
{"code": 10, "label": "CO", "fullname" :"pollutant_10", "index":6, "color": 'gray' , "label_en": "Carbon monoxide (air)", "label_el":"Μονοξείδιο Άνθρακα"},
{"code": 5, "label": "PM₁₀", "fullname" :	"pollutant_5", "index":7, "color": 'blue' , "label_en": "Particulate matter < 10 μm (aerosol)", "label_el":"Σωματίδια < 10 μm"},
{"code": 6001, "label": "PM₂.₅", "fullname" :"pollutant_6001", "index":8 , "color": 'red', "label_en": "Particulate matter < 2.5 μm (aerosol)", "label_el":"Σωματίδια < 2.5 μm"},
{"code": 20, "label": "C₆H₆", "fullname" :	"pollutant_20", "index":9, "color": 'magenta' , "label_en": "Benzene (air)", "label_el":"Βενζόλιο"}
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

plt.figure(figsize=FIGSIZE, dpi=MYDPI)

m = Basemap(llcrnrlat=34.5, urcrnrlat=35.8,
            llcrnrlon=32.2, urcrnrlon=34.6,
            epsg=4230,
            projection='cyl',
            resolution='c' )


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


for s in stations_list:
	lat=s['lat']
	lon=s['long']
	code = s['code']
	label=s['label_en']
	label = label.split(' ')[0]
	x, y = m(lon, lat)

	url=f"https://www.airquality.dli.mlsi.gov.cy/station_data/{code}/{ytd.year}-{ytd.month}-{ytd.day}:{ytd.hour}/{now.year}-{now.month}-{now.day}:{now.hour}"
	print(url)
	res = requests.get(url)
	res = res.json()
	print(res)

	pollution=''
	try:
		k=list(res['data'].keys())[-1]
		pollution=res['data'][k]['pollutant_6001']
		pollution=round(float(pollution))
	except Exception as e:
		print(str(e))


	if not pollution:
		continue

	text = f"{label}"

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
	if fp> 0:
		color="green"
	if fp> 25:
		color="orange"
	if fp> 50:
		color="red"
	if fp> 100:
		color="purple"

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
	plt.title("Air Quality in Cyprus: PM 2.5", fontsize = 40)




create_dir(OUTPUT_DIR)
delete_previous_files(OUTPUT_DIR)
plt.savefig(os.path.join(OUTPUT_DIR, 'airquality.png'))
