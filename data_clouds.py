
import copy
import os
import re
import tqdm
import pathlib
import numpy as np
import pandas as pd
import seaborn as sns
import wbgapi as wb

from PIL import Image
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from sklearn.svm import SVR
from sklearn.manifold import TSNE
from tools.plot_tools import prep_plot


INPUT_DIR = "input/data_clouds"
OUTPUT_DIR = "output/data_clouds"
matplotlib.use('pdf')

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

    df = pd.read_csv(output_df)

    if plot:
        os.makedirs(os.path.join(OUTPUT_DIR, 'plots'), exist_ok=True)
        output_png = os.path.join(OUTPUT_DIR, 'plots', series['id']+'.png')
        if os.path.exists(output_png) and test_png_exists:
            return

        try:
            prep_plot()
            plt.rcParams["figure.figsize"] = [16, 9]


            g1=sns.lineplot(data=df[df['Countries']!='Cyprus'], x='year', y=yname, hue='Countries', legend=True,  linewidth=3.0,  color='orange')
            box = g1.get_position()
            g1.set_position([box.x0, box.y0, box.width * 0.9, box.height])

            g2=sns.lineplot(data=df[df['Countries']=='Cyprus'], x='year', y=yname, legend=True,  linewidth=6.0,  color='orange')
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
            plt.clf()
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
    png_files = [os.path.join(OUTPUT_DIR,'plots', f) for f in os.listdir(os.path.join(OUTPUT_DIR, 'plots')) if os.path.isfile(os.path.join(OUTPUT_DIR, 'plots', f)) and pathlib.Path(f).suffix=='.png']
    nb_files = len(png_files)
    assert nb_files > 0
    im_size = Image.open(png_files[0]).size
    
    w=19
    h=10
    ratio = .1
    
    ni=1
    nj=1

    while ni*nj < nb_files:
        if (ni*im_size[0])/(nj*im_size[1]) > w/h:
            nj=nj+1
        else:
            ni=ni+1
    
    if ni*nj > nb_files:
        if (ni*im_size[0])/(nj*im_size[1]) > w/h:
            ni=ni-1
        else:
            nj=nj-1    

    print(f'ni={ni}, nj={nj}, ni*nj={ni*nj}, nb_files={nb_files}')
    assert ni*nj < nb_files
    
    ccim = None
    for i in tqdm.tqdm(range(ni)):
        for j in range(nj):
            index = j+i*nj
            try:
                im = Image.open(png_files[index])
            except Exception as e:
                print(str(e))
                continue

            im = im.resize((int(im_size[0]*ratio), int(im_size[1]*ratio)), Image.LANCZOS)
            s =im.size

            if ccim is None:
                nw=int(s[0]*ni)
                nh=int(s[1]*nj)
                print((nw, nh))
                ccim = Image.new("RGB", (nw, nh), "white")
            ccim.paste(im, (int(s[0]*i), int(s[1]*j)))

    if ccim:
        ccim.save(os.path.join(OUTPUT_DIR, 'tiles.png'))


def reduce_dimensions(show=True):
    csv_files = [os.path.join(OUTPUT_DIR, 'data', f) for f in os.listdir(os.path.join(OUTPUT_DIR, 'data')) if os.path.isfile(os.path.join(OUTPUT_DIR,'data', f)) and pathlib.Path(f).suffix=='.csv']

    nb_rows = None
    yy=[]
    xx=None
    uniques=None
    for f in csv_files:
        df = pd.read_csv(f)
        if nb_rows is None:
            nb_rows = df.shape[0]
        assert df.shape[0] == nb_rows

        df['Countries'], uniques = pd.factorize(df['Countries'])
        cols = df.columns

        df1=df.copy()
        df1 = df1.dropna()
        X= df1[cols[1:-1]].to_numpy()
        Y = df1[cols[-1:]].to_numpy()
        assert not np.isnan(X).any()
        assert not np.isnan(Y).any()

        reg = SVR(C=1.0, epsilon=0.2)
        reg.fit(X, Y.ravel())
        df2=df.copy()
        X= df2[cols[1:-1]].to_numpy()
        Y = df2[cols[-1:]].to_numpy()
        Ypred = reg.predict(X)
        Ypred = Ypred.ravel()
        Y = Y.ravel()
        inds = np.where(np.isnan(Y))
        Y[inds]=Ypred[inds]

        assert not np.isnan(X).any()
        assert not np.isnan(Y).any()

        if xx is None:
            xx=X

        assert np.array_equal(X,xx)
        yy.append([Y])

    yy=np.concatenate(yy, axis=0)
    yy=np.swapaxes(yy,0,1)
    print(xx.shape)
    print(yy.shape)

    yy_embeded = TSNE(n_components=2, learning_rate='auto', init='random').fit_transform(yy)
    data=np.concatenate([xx, yy_embeded], axis=1)
    print(data.shape)
    prep_plot()
    plt.rcParams["figure.figsize"] = [16, 9]
    df = pd.DataFrame(data, columns = ['Year', 'Countries', 'X','Y'])

    for c, country in enumerate(uniques):
        df.loc[df['Countries'] == c, 'Countries'] = country


    prep_plot()
    plt.rcParams["figure.figsize"] = [16, 9]

    g1=sns.scatterplot(data=df[df['Countries']!='Cyprus'], x='X', y='Y', hue='Countries', size='Year', legend=True,   sizes=(10, 400),)
    box = g1.get_position()
    g1.set_position([box.x0, box.y0, box.width * 0.9, box.height])

    g2=sns.scatterplot(data=df[df['Countries']=='Cyprus'], x='X', y='Y',  size='Year', legend=False,   sizes=(10, 400),  color='orange')
    box = g2.get_position()
    g2.set_position([box.x0, box.y0, box.width * 0.9, box.height])

    handles, _ = g2.get_legend_handles_labels()
    h = copy.copy(handles[1])
    h.set_label('Cyprus')
    h.set_color('orange')
    handles.insert(1, h)

    for h in handles:
        l = h.get_label()
        res = re.match(r"\d\d\d\d",l)
        if res is not None:
            cs=False
            h.set_color('grey')
        if isinstance(h, matplotlib.collections.PathCollection)and res is None:
            h.set_sizes(h.get_sizes()*10)
    # plot the legend
    plt.legend(handles=handles, loc='center right', bbox_to_anchor=(1.3, 0.5), ncol=1)

    output_png = os.path.join(OUTPUT_DIR, 'reduced.png')
    plt.savefig(output_png, format='png', dpi=600)
    if show:
        plt.show()
    plt.close('all')
    plt.clf()


if __name__ == "__main__":

    if False:
        data_info()

    if False:
        countries=['CYP', 'GRC', 'TUR', 'MLT', 'PRT', 'FRA', 'GTM']
        #series=['NY.GDP.PCAP.CD']

        series=wb.series.info()
        for i in tqdm.tqdm(series.items):
            try:
                get_data(countries, i,
                         seried_name_max_length=55, min_data_count=10,
                         plot=True, show=False, test_png_exists=True)
            except Exception as e:
                print(str(e))

    if True:
        concat_images()

    if True:
        reduce_dimensions()
