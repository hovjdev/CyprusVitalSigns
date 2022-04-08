import os
import re
import pathlib
import numpy as np
import pandas as pd
import seaborn as sns
import wbgapi as wb

from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from sklearn.random_projection import SparseRandomProjection
from tools.plot_tools import prep_plot




INPUT_DIR = "input/data_clouds"
OUTPUT_DIR = "output/data_clouds"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def plot(countries, series, show=True, test_png_exists=False):

    assert isinstance(countries, list)
    assert isinstance(series, list)    
    assert len(series)==1

    output_png = os.path.join(OUTPUT_DIR, series[0]+'.png')
    if os.path.exists(output_png) and test_png_exists:
        return

    df=wb.data.DataFrame(series, countries)
    columns=df.columns
    for col in columns:
        df=df.rename(columns={col: int(re.findall(r'\d+', col)[0])})
    df=df.T
    df=df.replace('..', value=np.nan)
    df=df.replace('NaN', value=np.nan)
    columns=df.columns
    for col in columns:
        df[col] = pd.to_numeric(df[col])
    try:
        df = df.interpolate(method = "linear", order=0, limit_direction = "both", limit_area='inside')
    except Exception as e:
        print(str(e))
    try:
        df = df.interpolate(method = "nearest", order=0, limit_direction = "both", limit_area='outside')
    except Exception as e:
        print(str(e))    
    df=df.reset_index()
    df=df.rename(columns={'index': 'year'})

    y=series[0]
    yname=wb.series.info(y).items[0]['value']
    df = df.melt('year', var_name='Countries', value_name=yname)
    print(df)
    print(df.dtypes)
    print(df.columns)

    for c in countries:
        df.loc[df['Countries'] == c, 'Countries'] = wb.economy.info(c).items[0]['value']

    print(df)

    prep_plot()
    plt.rcParams["figure.figsize"] = [16, 9]


    g1=sns.lineplot(data=df[df['Countries']!='Cyprus'], x='year', y=yname, hue='Countries', legend=True,  linewidth=1.0,  color='orange')
    box = g1.get_position()
    g1.set_position([box.x0, box.y0, box.width * 0.9, box.height]) 

    g2=sns.lineplot(data=df[df['Countries']=='Cyprus'], x='year', y=yname, legend=True,  linewidth=5.0,  color='orange')
    box = g2.get_position()
    g2.set_position([box.x0, box.y0, box.width * 0.9, box.height]) 


    handles, _ = g2.get_legend_handles_labels()
    line = mlines.Line2D([], [], color='orange', label='Cyprus', linewidth=5.0)
    handles.append(line) 

    # plot the legend
    plt.legend(handles=handles, loc='center right', bbox_to_anchor=(1.3, 0.5), ncol=1)
    plt.savefig(output_png, format='png', dpi=600)
    if show:
        plt.show()
    plt.close('all')


def data_info():
    series=wb.series.info()
    for i in series.items:
        print(i)
    regions=wb.region.info()
    for i in regions.items:
        print(i)
    economies=wb.economy.info()
    for i in economies.items:
        print(i)


def concat_images():
    png_files = [os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR) if os.path.isfile(os.path.join(OUTPUT_DIR, f)) and pathlib.Path(f).suffix=='.png']
    nb = len(png_files)
    print(nb)


    png_files=png_files[0:9*16*4]

    ccim = None
    f=int(int(nb/(16*9))**.5)
    for i in range(f*16):
        for j in range(f*9):
            index = j+i*(f*9)
            im = Image.open(png_files[index])
            if ccim is None:
                s = im.size
                ratio = .05
                im = im.resize((int(s[0]*ratio), int(s[1]*ratio)), Image.ANTIALIAS)
                s = im.size
                nw=int(s[0]*f*16)
                nh=int(s[1]*f*16)              
                print((nw, nh))  
                ccim = Image.new("RGB", (int(s[0]*f*16), int(s[1]*f*9)), "white")
            print(index)
            ccim.paste(im, (int(s[0]*i), int(s[0]*j)))

    if ccim:
        ccim.save("img1.png")
    


#data_info()

if False:
    countries=['CYP', 'FRA', 'GTM', 'GRC', 'TUR', 'MLT']
    #series=['NY.GDP.PCAP.CD']

    series=wb.series.info()
    for i in series.items:
        try:
            plot(countries, [i['id']], show=False, test_png_exists=True)
        except Exception as e:
            print(str(e))
        



concat_images()