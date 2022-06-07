
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


def prep_plot(font_scale = 2):
    plt.style.use('dark_background')

    sns.set(rc={'figure.figsize':(16,12)})
    sns.set(font_scale = font_scale)
    sns.set_style("dark", {'axes.grid' : False})
    plt.style.use("dark_background")
    fm.fontManager.addfont("input/fonts/bauhaus/BauhausRegular.ttf")
    plt.rcParams['font.family'] = 'Bauhaus'
