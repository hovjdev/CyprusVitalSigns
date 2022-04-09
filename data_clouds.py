
import os
import re
import tqdm
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


def get_data(countries, series,
        seried_name_max_length=-1, min_data_count=-1,
        plot=True, show=True, test_png_exists=False):

    assert isinstance(countries, list)

    yname=series['value']
    if seried_name_max_length > 0 and len(yname) > seried_name_max_length:
        print(f'>>>> len({yname})={len(yname)} > {seried_name_max_length}')
        return

    os.makedirs(os.path.join(OUTPUT_DIR, 'data'), exist_ok=True)
    output_df = os.path.join(OUTPUT_DIR, 'data', series['id']+'.csv')


    if not os.path.exists(output_df):

        df=wb.data.DataFrame([series['id']], countries)
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



        df = df.melt('year', var_name='Countries', value_name=yname)
        print(df)
        print(df.dtypes)
        print(df.columns)

        for c in countries:
            df.loc[df['Countries'] == c, 'Countries'] = wb.economy.info(c).items[0]['value']

        if min_data_count > 0  and df[df['Countries']=='Cyprus'][yname].count() < min_data_count:
            print(f">>>> data count = {df[df['Countries']=='Cyprus'].count()} < min_data_count")
            return

        df.to_csv(output_df)

    if plot:
        os.makedirs(os.path.join(OUTPUT_DIR, 'plots'), exist_ok=True)
        output_png = os.path.join(OUTPUT_DIR, 'plots', series['id']+'.png')
        if os.path.exists(output_png) and test_png_exists:
            return

        try:
            prep_plot()
            plt.rcParams["figure.figsize"] = [16, 9]


            g1=sns.lineplot(data=df[df['Countries']!='Cyprus'], x='year', y=yname, hue='Countries', legend=True,  linewidth=2.0,  color='orange')
            box = g1.get_position()
            g1.set_position([box.x0, box.y0, box.width * 0.9, box.height])

            g2=sns.lineplot(data=df[df['Countries']=='Cyprus'], x='year', y=yname, legend=True,  linewidth=5.0,  color='orange')
            box = g2.get_position()
            g2.set_position([box.x0, box.y0, box.width * 0.9, box.height])


            handles, _ = g2.get_legend_handles_labels()
            line = mlines.Line2D([], [], color='orange', label='Cyprus', linewidth=5.0)
            handles.insert(0, line)

            # plot the legend
            plt.legend(handles=handles, loc='center right', bbox_to_anchor=(1.3, 0.5), ncol=1)
            plt.savefig(output_png, format='png', dpi=600)
            if show:
                plt.show()
            plt.close('all')
        except Exception as e:
            print(str(e))

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
    nb=1
    ww=19
    hh=10
    png_files=png_files[0:hh*ww*(nb**2)]
    nb = len(png_files)
    print(nb)
    ccim = None
    f=int(int(nb/(ww*hh))**.5)
    print(f)
    for i in tqdm.tqdm(range(f*ww)):
        for j in range(f*hh):
            index = j+i*(f*hh)
            try:
                im = Image.open(png_files[index])
            except Exception as e:
                print(str(e))
                continue

            s = im.size
            ratio = .2
            im = im.resize((int(s[0]*ratio), int(s[1]*ratio)), Image.LANCZOS)
            s = im.size
            if ccim is None:
                nw=int(s[0]*f*ww)
                nh=int(s[1]*f*hh)
                print((nw, nh))
                ccim = Image.new("RGB", (nw, nh), "white")
            ccim.paste(im, (int(s[0]*i), int(s[1]*j)))

    if ccim:
        ccim.save(os.path.join(OUTPUT_DIR, 'tiles.png'))



#data_info()

if True:
    countries=['CYP', 'FRA', 'GTM', 'GRC', 'TUR', 'MLT']
    #series=['NY.GDP.PCAP.CD']

    series=wb.series.info()
    for i in tqdm.tqdm(series.items):
        try:
            get_data(countries, i,
                     seried_name_max_length=55, min_data_count=10,
                     plot=False, show=False, test_png_exists=True)
        except Exception as e:
            print(str(e))



if False:
    concat_imges()
