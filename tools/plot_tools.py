import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from mpl_toolkits.basemap import Basemap


def prep_plot(font_scale = 2):
    plt.style.use('dark_background')

    sns.set(rc={'figure.figsize':(16,12)})
    sns.set(font_scale = font_scale)
    sns.set_style("dark", {'axes.grid' : False})
    plt.style.use("dark_background")
    fm.fontManager.addfont("input/fonts/bauhaus/BauhausRegular.ttf")
    plt.rcParams['font.family'] = 'Bauhaus'


def get_cyprus_map(figsize, dpi):
    
    figure, axes = plt.subplots(1, 1, figsize=figsize, dpi=dpi)
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

    return m, figure, axes