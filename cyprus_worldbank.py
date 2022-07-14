import argparse
import requests
import os
import re
import random
from lxml import html
import wbgapi as wb
import pandas as pd
import seaborn as sns
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.covariance import EllipticEnvelope


import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from tools.plot_tools import prep_plot
from tools.file_utils import create_dir, delete_previous_files

from parrot import Parrot
from paraphrase import paraphrase_text


CO2_DATA_URL ="https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_mlo.txt"
ECONOMIES_1 = ['GRC',  'CYP', 'FRA', 'WLD']
ECONOMIES_1 = ['CYP', 'WLD']
ECONOMIES_2 = ['CYP',  'WLD']
SERIES = ['NY.GDP.PCAP.CD', 'SP.POP.TOTL']
OUTPUT_DIR = 'output/cyprus_worldbank'
DEBUG=False
PARROT=False

HAND_SELECTED_INDICATORS = [
        {'ind':'ST.INT.ARVL', 'CYP_ONLY':True},
        {'ind':'ST.INT.XPND.CD', 'CYP_ONLY':True},
        {'ind':'EG.USE.PCAP.KG.OE', 'CYP_ONLY':False},
        {'ind':'NY.GDP.MKTP.CD', 'CYP_ONLY':True},
        {'ind':'EN.ATM.CO2E.PC', 'CYP_ONLY':False},
        {'ind':'EG.USE.COMM.FO.ZS', 'CYP_ONLY':False},
    ]


MAX_N = 3
MAX_IND_LENGTH = 63
MIN_NB_DATA=15
MAX_NB_OUTLIERS=3
MIN_SLOPE=.1
MIN_MAXMIN=.1


def get_co2_data():
    df=pd.read_csv(CO2_DATA_URL, delim_whitespace=True,  comment='#', header=None)
    df.columns=['year', 'mean', 'unc']
    return df

def get_wb_topics():
    topics=list(wb.topic.list())
    return topics

def get_ecolomic_data(series=SERIES, economies=ECONOMIES_1):
    df = wb.data.DataFrame(series, economies)
    return df

def get_random_topic():
    topics=get_wb_topics()
    topic=random.choice(topics)
    return topic

def get_economie_name(id):
    l=list(wb.economy.list(id))
    if not len(l): return ""
    return l[0]['value']

def get_indicators(topic_nb):
    inds = list(wb.topic.members(topic_nb))
    random.shuffle(inds)
    return inds

def get_title(ind):
    info=wb.series.list(ind)
    title='None'
    for i in info:
        title=str(i['value'])
    return title

def count_outliers(df):
    d = df.to_numpy()
    x=np.arange(d.shape[0])
    d=np.insert(d, 0, x, axis=1)
    d=d[~np.isnan(d).any(axis=1)]

    coeffs=[]
    for i in range(d.shape[1]-1):
        x = np.copy(d[::,0]).reshape(-1, 1)
        y = np.copy(d[::,i+1]).reshape(-1, 1)
        reg = LinearRegression().fit(x, y)
        coeffs.append([reg.coef_[0][0],  reg.intercept_[0]])

    # print('coeffs', coeffs)
    try:
        outliers = EllipticEnvelope(random_state = 0).fit_predict(coeffs)
    except Exception as e:
        return True

    nb_outliers = 0
    for o in outliers:
        if o==-1: nb_outliers=nb_outliers+1

    return nb_outliers


def filter_inds_nb_outliers(df, inds, min_nb_data, max_nb_outliers):
    #print(df)
    indsf=[]
    for ind in inds:
        d=df[df.index.map(lambda x: x[1]==ind)]
        tmp=1e6
        for index, row in d.iterrows():
            val_count = row.count()
            #print(val_count, row)
            tmp=min(tmp, val_count)

        if tmp < min_nb_data:
            continue

        nb_outliers  = count_outliers(d.transpose())

        skip=False
        if nb_outliers > max_nb_outliers:
            skip = True
        print(f'>>> nb_outliers:{nb_outliers}, max_nb_outliers:{max_nb_outliers}, skip:{skip}')

        if skip:
            continue

        indsf.append(ind)

    return indsf

def get_min_maxmin(df):
    min_mixmax = -1
    d = df.to_numpy()

    tmp=np.nanmax(d)-np.nanmin(d)
    d = (d - np.nanmin(d))/tmp
    d=d[~np.isnan(d).any(axis=1)]

    for i in range(d.shape[1]):
        y = np.copy(d[::,i]).reshape(-1, 1)
        try:
            mm = np.nanmax(y)-np.nanmin(y)
        except Exception as e:
            print(str(e))
            return -1

        assert mm >= 0
        if min_mixmax < 0:
            min_mixmax=mm
        else:
            min_mixmax=min(min_mixmax, mm)

    return min_mixmax

def get_slope(df, c):

    avg_slope = 0
    n=0

    cols = df.columns

    d = df.to_numpy()
    nb_dim = d.ndim
    if nb_dim == 1:
        d = np.reshape(d, (d.shape[0], -1))

    tmp=np.nanmax(d)-np.nanmin(d)
    d = (d - np.nanmin(d))/tmp

    x=np.arange(d.shape[0])
    tmp=np.nanmax(x)-np.nanmin(x)
    x = (x - np.nanmin(x))/tmp

    d=np.insert(d, 0, x, axis=1)
    d=d[~np.isnan(d).any(axis=1)]

    for i in range(d.shape[1]-1):
        if cols[i] != c:
            continue
        x = np.copy(d[::,0]).reshape(-1, 1)
        y = np.copy(d[::,i+1]).reshape(-1, 1)
        try:
            reg = LinearRegression().fit(x, y)
        except Exception as e:
            print(str(e))
            return -1
        avg_slope = avg_slope + reg.coef_[0][0]
        n=n+1

    return avg_slope/n



def get_min_slope(df):

    min_slope = -1
    d = df.to_numpy()

    tmp=np.nanmax(d)-np.nanmin(d)
    d = (d - np.nanmin(d))/tmp

    x=np.arange(d.shape[0])
    tmp=np.nanmax(x)-np.nanmin(x)
    x = (x - np.nanmin(x))/tmp

    d=np.insert(d, 0, x, axis=1)
    d=d[~np.isnan(d).any(axis=1)]

    for i in range(d.shape[1]-1):
        x = np.copy(d[::,0]).reshape(-1, 1)
        y = np.copy(d[::,i+1]).reshape(-1, 1)
        try:
            reg = LinearRegression().fit(x, y)
        except Exception as e:
            print(str(e))
            return -1
        if min_slope < 0:
            min_slope=abs(reg.coef_[0][0])
        else:
            min_slope=min(abs(reg.coef_[0][0]), min_slope)

    return min_slope


def filter_inds_on_slope(df, inds, min_slope):

    indsf=[]
    for ind in inds:
        d=df[df.index.map(lambda x: x[1]==ind)]
        slope = get_min_slope(d.transpose())
        skip=False
        if slope < min_slope:
            skip=True
        print(f'>>> slope:{slope}, min_slope:{min_slope}, skip:{skip}')
        if skip:
            continue
        indsf.append(ind)

    return indsf


def filter_inds_on_maxmin(df, inds, min_maxmin):

    indsf=[]
    for ind in inds:
        d=df[df.index.map(lambda x: x[1]==ind)]
        maxmin = get_min_maxmin(d.transpose())
        skip=False
        if maxmin < min_maxmin:
            skip=True
        print(f'>>> min_maxmin:{min_maxmin}, maxmin:{maxmin}, skip:{skip}')
        if skip:
            continue
        indsf.append(ind)

    return indsf


def filter_inds_on_length(inds, max_ind, max_ind_length):
    indsf=[]
    random.shuffle(inds)
    for ind in inds:
        title = get_title(ind)
        if len(title)<=max_ind_length:
            indsf.append(ind)
        if len(indsf) == max_ind:
            break
    return indsf

def get_random_data(economies,
                    max_ind=MAX_N,
                    max_ind_length=MAX_IND_LENGTH,
                    min_nb_data=MIN_NB_DATA,
                    min_slope=MIN_SLOPE,
                    min_maxmin=MIN_MAXMIN,
                    max_nb_outliers=MAX_NB_OUTLIERS):

    topic=get_random_topic()
    print('>>> topic:',topic)


    if DEBUG:
        print(topic)
    inds = get_indicators(topic['id'])
    if DEBUG:
        print(inds)

    print('0 >>> inds:', len(inds))

    inds=filter_inds_on_length(inds, max_ind=10*max_ind, max_ind_length=max_ind_length)
    print('1 >>> inds:', len(inds))

    df = wb.data.DataFrame(inds, economies)

    inds=filter_inds_on_maxmin(df, inds, min_maxmin=min_maxmin)
    print('2 >>> inds:', len(inds))

    inds=filter_inds_on_slope(df, inds, min_slope=min_slope)
    print('3 >>> inds:', len(inds))

    inds=filter_inds_nb_outliers(df, inds, min_nb_data=min_nb_data, max_nb_outliers=max_nb_outliers)
    print('4 >>> inds:', len(inds))

    inds=filter_inds_on_length(inds, max_ind=2*max_ind, max_ind_length=max_ind_length)
    print('5 >>> inds:', len(inds))

    # Add hand selected indicators:
    hand_selected = HAND_SELECTED_INDICATORS 

    # inds_dict
    if True:
        inds_dicts = hand_selected
        for ind in inds:
            found=False
            for hs in inds_dicts:
                if hs['ind']==ind:
                    found=True
                    break
            if not found:
                inds_dicts.append({'ind':ind, 'CYP_ONLY':False})
    # DEBUG:
    if False:
        inds_dicts=[{'ind':'EG.USE.COMM.FO.ZS', 'CYP_ONLY':False}]


    # random selection of indicators
    max_ind=min(max_ind, len(inds_dicts))
    inds_dicts = random.sample(inds_dicts, k=max_ind)
    inds=[]
    for ind_dict in inds_dicts:
        print(ind_dict)
        print(type(ind_dict))
        inds.append(ind_dict['ind'])

    df = wb.data.DataFrame(inds, economies)

    data = {'df':df, 'inds_dicts': inds_dicts, 'topic':topic}
    return data


def pref_df(df, economies):
    df.columns = df.columns.str.replace("YR", "")
    df=df.T

    #print(">>>>>>>> plot_df")
    #print(df)

    countries_nocyp=[]
    countries_cyp=[]

    for c in economies:
        name=get_economie_name(c)
        df.columns = df.columns.str.replace(c, name)
        if c == 'CYP':
            countries_cyp.append(name)
        else:
            countries_nocyp.append(name)

    #print(f'>>> countries_nocyp: {countries_nocyp}')
    #print(f'>>> countries_cyp: {countries_cyp}')

    return df, countries_nocyp, countries_cyp


def plot_df(df, title, economies, index, output_dir):

    df, countries_nocyp, countries_cyp=pref_df(df, economies)

    linewidth=5
    font_scale=3

    prep_plot(font_scale=font_scale)
    plt.rcParams["figure.figsize"] = [16, 9]


    #print(f"countries_nocyp: {countries_nocyp}")
    #print(f"df[countries_nocyp]: {df[countries_nocyp]}")

    box=None
    if len(countries_nocyp) > 0:
        g1=sns.lineplot(data=df[countries_nocyp], legend=True,  sizes=(10, 600),linewidth=linewidth, dashes=False)
        box = g1.get_position()
        g1.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    g2=sns.lineplot(data=df[countries_cyp],  legend=False,   sizes=(10, 600),  palette=['orange'], linewidth=linewidth, dashes=False)
    if not box:
        box = g2.get_position()
        g2.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    handles, _ = g2.get_legend_handles_labels()
    line = mlines.Line2D([], [], color='orange', label='Cyprus', linewidth=linewidth)
    handles.insert(0, line)

    for h in handles:
        h.set_linewidth(linewidth)

    plt.legend(handles=handles, loc='center right', bbox_to_anchor=(1.35, 0.5), ncol=1)


    ax=g2

    plt.rcParams['axes.titley'] = 1.0    # y is in axes-relative coordinates.
    plt.rcParams['axes.titlepad'] = 30
    ax.set_title(title)

    nbticks=6
    ntx=len(ax.xaxis.get_ticklabels())
    if ntx>nbticks:
        nbt = int(ntx/nbticks)+1
        for i, tick in enumerate(reversed(ax.xaxis.get_ticklabels())):
            if i % nbt != 0:
                tick.set_visible(False)

    nty=len(ax.xaxis.get_ticklabels())
    if nty>nbticks:
        nbt = int(nty/nbticks)+1
        for i, tick in enumerate(reversed(ax.yaxis.get_ticklabels())):
            if i % nbt != 0:
                tick.set_visible(False)

    # data source
    plt.text(0., -.12, 'data: https://data.worldbank.org/', ha='left', va='center', transform=ax.transAxes, fontsize=15)

    # save plot
    output_png=os.path.join(output_dir, f'data_plot_{index}.png')
    plt.savefig(output_png, format='png', dpi=600)

    # save data
    output_data=os.path.join(output_dir, f'data_{index}.npy')
    with open(output_data, 'wb') as f:
        np.save(f, df[countries_cyp].to_numpy())

    show=False
    if show:
        plt.show()
    plt.close('all')
    plt.clf()


def narrate_df(df, title, economies, output_txt_file):

    df, countries_nocyp, countries_cyp=pref_df(df, economies)

    df = df.interpolate(method='linear', axis=0, limit_direction='both', limit_area='inside')
    df_nonan = df[~np.isnan(df).any(axis=1)]
    df = df.astype(float)
    df_nonan = df_nonan.astype(float)

    topic =  re.sub("\(.*?\)","",title)
    topic = topic.split(',')[0]

    title_fix = str(title)
    title_fix = title_fix.replace("BoP", "Balance of Payments")
    title_fix = title_fix.replace("PPP", "Purchasing power parity")
    title_fix = title_fix.replace("sq. km", "square kilometers")


    def find_trend(df, c):
        trend = 'stayed more or less the same'
        slope = get_slope(df, c)
        if slope > .1:
            trend="increased slightly"
        if slope > .25:
            trend="increased"
        if slope > .5:
            trend="increased significantly"
        if slope < -.1:
            trend="decreased slightly"
        if slope < -.25:
            trend="decreased"
        if slope < -.5:
            trend="decreased significantly"
        return trend

    trend1=-1
    trend2=-1
    with open(output_txt_file, "a") as f:
        opening2=random.choice(["Let's", "Let's", "And now let's", "We will now", "We shall now"])
        opening1=random.choice(["look at", "review", "examine"])
        f.write(f"{opening2} {opening1} the {title_fix}.\n")
        for c in countries_cyp:
            trend1=find_trend(df_nonan, c)
            f.write(f"From {df_nonan.index[0]} to {df_nonan.index[-1]} in {c},\n")
            f.write(f"The {topic} {trend1}.\n")

        ok=True
        for c in countries_nocyp:
            trend2=find_trend(df, c)

            liaison=random.choice(["Whereas", "Instead", "Meanwhile", "In contrast", "However"])
            if "increase" in trend1 and "increase" in trend2:
                liaison=random.choice(["Likewise", "Similarly", "By the same token", "Moreover", "Furthermore"])
            if "decrease" in trend1 and "decrease" in trend2:
                liaison=random.choice(["Likewise", "Similarly", "By the same token", "Moreover", "Furthermore"])

            if ok:
                f.write(f"{liaison}, during that same period,\n")
                ok=False

            f.write(f"The {topic} {trend2} for the {c}.\n")


def create_media(data, economies, output_dir=OUTPUT_DIR, parrot=None):

    topic_name=data['topic']['value']
    topic_description=data['topic']['sourceNote']
    text_file = os.path.join(OUTPUT_DIR, 'notes.txt')

    '''with open(text_file, 'w') as f:
        f.write(topic_name)
        f.write('\n\n')
        f.write(topic_description)
        f.write('\n\n')'''

    topic_description = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', topic_description) # split in sentences

    for index,  inds_dict in enumerate(data['inds_dicts']):
        
        ind = inds_dict['ind']
        cyp_only = inds_dict['CYP_ONLY']

        title=get_title(ind)
        economies_used = economies
        if cyp_only:
            economies_used=['CYP']

        df=wb.data.DataFrame(ind, economies_used)  
        plot_df(df,title, economies_used, index, output_dir)

        output_txt_file=os.path.join(output_dir, f'data_text_{index}.txt')

        # narrate topic only for first ind
        if index == 0 and False:
            with open(output_txt_file, "w") as f:
                text=''
                for tdesc in topic_description:
                    if parrot:
                        tdesc=paraphrase_text(text=tdesc, parrot=parrot)
                    text += tdesc + '\n'
                    if len(text) > 300:
                        break
                f.write(text + '\n')

        # indicator defenition
        long_def = get_ind_long_def(ind)
        if long_def:
            long_def = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', long_def)
            long_def_text=''
            for ldf in long_def:
                long_def_text+= ldf + '\n'
                if len(long_def_text) > 250:
                    break
            with open(output_txt_file, "a") as f:
                f.write(long_def_text + '\n')
        
        # narrate df
        narrate_df(df,title, economies_used, output_txt_file)

    return


def get_ind_long_def(ind):
    try:
        url = f'https://databank.worldbank.org/metadataglossary/world-development-indicators/series/{ind}'
        page = requests.get(url)
        tree = html.fromstring(page.content)
        long_def = tree.xpath('//*[@id="DivSingleMeta"]/table/tbody/tr[3]/td[2]/text()')
        assert len(long_def) == 1
        return long_def[0]
    except Exception as e:
        print(str(e))
    return None

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


    if DEBUG:
        df = get_co2_data()
        print(df)
        print(f'type(df)={type(df)}')
        topics=get_wb_topics()
        print(topics)
        print(f'type(topics)={type(topics)}')
        df = get_ecolomic_data()
        print(df)
        print(f'type(df)={type(df)}')
        inds = get_indicators(topic_nb=19)
        print(inds)
        print(f'type(inds)={type(inds)}')

    parrot=None
    if PARROT:
        print("Loading parrot...")
        parrot = Parrot(model_tag="prithivida/parrot_paraphraser_on_T5")
        print("Parrot loaded...")

    for i in range(10):
        data=None
        try:
            create_dir(OUTPUT_DIR)
            delete_previous_files(OUTPUT_DIR)
            data = get_random_data(economies=ECONOMIES_1)
            print(data)
        except Exception as e:
            print(str(e))
            print(f"Try {i} failed")
            print(data)
            continue
        create_media(data=data, economies=ECONOMIES_2, output_dir=OUTPUT_DIR, parrot=parrot)
        break
