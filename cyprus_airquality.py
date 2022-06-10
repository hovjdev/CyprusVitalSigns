
import requests
import json

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
{"code" : 2, "label": "NICRES","label_en":"Nicosia Residential", "label_el":'Λευκωσία - Οικιστικός Σταθμός', "index":2, "color":"aqua", "long":33.382275, "lat":35.185566},
{"code" : 3,"label": "LIMTRA", "label_en":"Limassol Traffic", "label_el":'Λεμεσός - Κυκλοφοριακός Σταθμός', "index":3, "color":"violet", "long":33.0413, "lat":34.6786},
{"code" : 5,"label": "LARTRA", "label_en":"Larnaca Traffic", "label_el":'Λάρνακα - Κυκλοφοριακός Σταθμός', "index":4, "color":"green", "long":33.6201, "lat":34.9182},
{"code" : 8, "label": "ZYGIND","label_en":"Zygi Industrial Station", "label_el":'Ζύγι - Βιομηχανικός Σταθμός', "index":5, "color":"red", "long":33.3333, "lat":34.7333},
{"code" : 10,"label": "AYMRNA", "label_en":"Ayia Marina Background Station", "label_el":'Αγία Μαρίνα Ξυλιάτου - Σταθμός Υποβάθρου', "index":6, "color":"magenta", "long":33.2981002, "lat":33.7360593},
{"code" : 9,"label": "MARIND", "label_en":"Mari Industrial Station", "label_el":'Μαρί - Βιομηχανικός Σταθμός', "index":7, "color":"gold", "long":33.2981002, "lat":34.7360593},
{"code" : 7,"label": "PAFTRA", "label_en":"Paphos Traffic", "label_el":'Πάφος - Κυκλοφοριακός Σταθμός', "index":8, "color":"blue", "long":32.4218, "lat":34.7754},
{"code" : 11,"label": "PARTRA", "label_en":"Paralimnni Traffic", "label_el":'Παραλίμνι - Κυκλοφοριακός Σταθμός', "index":9, "color":"black", "long":33.9823, "lat":35.0380},
{"code" : 12,"label": "KALIND", "label_en":"Kalavasos Industrial Station", "label_el":'Καλαβασός Βιομηχανικός Σταθμός', "index":10, "color":"olive", "long":33.30798, "lat":34.7584},
{"code" : 13,"label": "ORMIND", "label_en":"Ormidia Industrial Station", "label_el":'Ορμήδια Βιομηχανικός', "index":11, "color":"skyblue", "long":33.7803, "lat":34.9925},
]






url = requests.get("https://www.airquality.dli.mlsi.gov.cy/station_data/1/2021-05-31/2021-05-31")
text = url.text
print(text)



import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
#mpl.use('Agg')

from mpl_toolkits.basemap import Basemap

ratio = 720.0 / 1280.0 * 1.0
width = 1660.0

MYDPI = float(plt.gcf().get_dpi())
FIGSIZE = (width / MYDPI, width * ratio / MYDPI)

plt.figure(figsize=FIGSIZE, dpi=MYDPI)

m = Basemap(llcrnrlat=34, urcrnrlat=36,
            llcrnrlon=32, urcrnrlon=35,
            epsg=4230,
            projection='cyl',
            resolution='c' )


m.drawcoastlines(color='#6D5F47', linewidth=.4)
m.drawcountries(color='#6D5F47', linewidth=.4)

m.drawmeridians(np.arange(-180, 180, 10), color='#bbbbbb')
m.drawparallels(np.arange(-90, 90, 10), color='#bbbbbb')
m.arcgisimage(
    server='https://server.arcgisonline.com/arcgis',
    service='World_Imagery', xpixels = 3500, dpi=500, verbose= True)


for s in stations_list:
    lat=s['lat']
    long=s['long'] 
    label=s['label_en']
    label = label.split(' ')[0]
    x, y = m(long, lat)
    plt.text(
            x,
            y,
            label,
            color='white',
            fontsize=15,
            horizontalalignment='center',
            verticalalignment='top',
            zorder=6,
        )

plt.show()