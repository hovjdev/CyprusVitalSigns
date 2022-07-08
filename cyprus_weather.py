import random
import argparse
import datetime
import os
import pytz

from unidecode import unidecode
from PIL import Image, ImageChops

import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('Agg')
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import matplotlib.patheffects as PathEffects
from matplotlib.pyplot import imread


from tools.file_utils import create_dir, delete_previous_files
from tools.plot_tools import get_cyprus_map


import forecastio
from local_settings import WEATHER_API_KEY



OUTPUT_DIR = 'output/cyprus_weather'


def narrate_map(forecasts, output_text_file, show_weather_icons=True, show_temperatures=False):


    with open(output_text_file, "w") as f:


        tz = pytz.timezone('EET')
        today=datetime.datetime.now(tz=tz).strftime("%A %d, %B %Y")

        if show_weather_icons:
            first=random.choice(["Now,", "And here is,", "And now, let's take a look at"])
            f.write(f"{first} the weather forecast for Cyprus on {today}.\n")
        else:
            first=random.choice(["Now,", "And here is,", "And now, let's take a look at"])
            f.write(f"And here is the temperature forecast for Cyprus on {today}.\n")

        dic_weather = {}
        dic_temp = {}

        for forecast in forecasts:

            long = forecast['long']
            lat = forecast['lat']
            current_city=forecast["city"]
            current=forecast["forecast"]
            current_summary = current.summary
            current_icon = current.icon
            current_time = current.time
            current_temperature = current.temperature
            current_temperature=round(current_temperature)
            current_precipProbability = current.precipProbability
       
            if not current_summary in dic_weather:
                dic_weather[current_summary] = []
            dic_weather[current_summary].append(current_city)

            if not current_temperature in dic_temp:
                dic_temp[current_temperature] = []
            dic_temp[current_temperature].append(current_city)
        
        def replace_last(string, find, replace):
            reversed = string[::-1]
            replaced = reversed.replace(find[::-1], replace[::-1], 1)
            return replaced[::-1]

        if show_weather_icons:
            weathers=[]
            for weather in dic_weather:
                weathers.append(weather)
            weathers.sort()
            for weather in weathers:
                cities=', '.join(dic_weather[weather])
                if len(dic_weather[weather]) > 1:   
                    cities = replace_last(cities, ', ', ' and ')

                f.write(f"{weather} in {cities}.\n")
        else:
            temps=[]
            for temp in dic_temp:
                temps.append(temp)
            temps.sort()         
            for temp in temps:
                cities=', '.join(dic_temp[temp])
                if len(dic_temp[temp]) > 1:   
                    cities = replace_last(cities, ', ', 'and ')   
                f.write(f"{temp} in {cities}.\n")






def draw_map(forecasts, output_image_file, show_weather_icons=True, show_temperatures=False):
    

    m, figure, axes=get_cyprus_map()

    xs=[]
    ys=[]
    
    icon_files_dict = {
        "clear-day": "Sun.png",
        "clear-night": "Moon.png",
        "rain": "Cloud-Rain.png",
        "snow": "Cloud-Snow.png",
        "sleet": "Cloud-Hail-Alt.png",
        "wind": "Wind.png",
        "fog": "Cloud-Fog.png",
        "cloudy": "Cloud.png",
        "partly-cloudy-day": "Cloud-Sun.png",
        "partly-cloudy-night": "Cloud-Moon.png",
        "hail": "Cloud-Hail.png",
        "thunderstorm": "Cloud-Lightning.png",
        "tornado": "Tornado.png"
    }

    for forecast in forecasts:

        long = forecast['long']
        lat = forecast['lat']
        x, y = m(long, lat)
        current_city=forecast["city"]
        current=forecast["forecast"]
        current_summary = current.summary
        current_icon = current.icon
        current_time = current.time
        current_temperature = current.temperature
        current_precipProbability = current.precipProbability
        icon_file = os.path.join("input", "weather", "PNG", icon_files_dict[current_icon])

        xs.append(x)
        ys.append(y)


        if show_weather_icons:
            # add icon
            try:
                # print(icon)
                im_arr = imread(icon_file)
                imagebox = OffsetImage(im_arr, zoom=1, interpolation='spline16')
                xy = [x, y]     # coordinates to position icon
                ab = AnnotationBbox(imagebox, xy,
                                    box_alignment=(0.5, 0.25),
                                    xycoords='data',
                                    frameon=False)
                m._check_ax().add_artist(ab)
            except:
                pass


        if show_temperatures:
                tmp = round(current_temperature)
                color = 'cyan'
                if tmp > 0:
                    color = 'blue'
                if tmp > 10:
                    color = 'green'
                if tmp > 20:
                    color = 'orange'
                if tmp > 30:
                    color = 'red'
                if tmp > 40:
                    color = 'magenta'
                txt = plt.text(
                    x,
                    y+.002,
                    tmp,
                    color=color,
                    weight='bold',
                    fontsize=64,
                    horizontalalignment='center',
                    verticalalignment='bottom',
                    zorder=6,
                )
                txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='b')])


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

    
    tz = pytz.timezone('EET')
    today=datetime.datetime.now(tz=tz).strftime("%A %d, %B %Y")
    figure.text(
        .85,
        .17,
        f"{today}",
        color='black',
        fontsize=20,
        horizontalalignment='center',
        verticalalignment='top',
        zorder=6,
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



    if show_weather_icons:
        plt.title(f"Cyprus weather forecast", fontsize = 60, y=1.0, pad=-90)

    else:
         plt.title(f"Cyprus temperature forecast", fontsize = 60, y=1.0, pad=-90)


    plt.savefig(output_image_file, bbox_inches='tight', dpi='figure',pad_inches=-.05)

    plt.close('all')


    if os.path.exists(output_image_file):
        return output_image_file

    return None

def create_cyprus_weather(output_dir=OUTPUT_DIR):

    
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


    forecasts = []

    for city in cities:
        lat = cities[city]['lat']
        long = cities[city]['long']

        tz = pytz.timezone('EET')
        now =datetime.datetime.now(tz)
        time = datetime.datetime(now.year, now.month, now.day, 12)
        forecast = forecastio.load_forecast(WEATHER_API_KEY, lat=lat, lng=long, units='si', time=time)
        current = forecast.currently()

        data = {"city":city, "lat":lat, "long":long, "forecast":current}
        forecasts.append(data)


    output_image_file = os.path.join(output_dir, "weather_map_icons.png")
    draw_map(forecasts, output_image_file, show_weather_icons=True, show_temperatures=False)
    output_text_file = os.path.join(output_dir, "weather_map_icons.txt")
    narrate_map(forecasts, output_text_file, show_weather_icons=True, show_temperatures=False)

    output_image_file = os.path.join(output_dir, "weather_map_temps.png")
    draw_map(forecasts, output_image_file, show_weather_icons=False, show_temperatures=True)
    output_text_file = os.path.join(output_dir, "weather_map_temps.txt")
    narrate_map(forecasts, output_text_file, show_weather_icons=False, show_temperatures=True)


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

    create_cyprus_weather(output_dir=OUTPUT_DIR)









