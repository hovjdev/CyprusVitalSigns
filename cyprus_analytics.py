import os
import re
import copy
import random
import shutil
from re import I
import wbgapi as wb
import pandas as pd
import seaborn as sns
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.covariance import EllipticEnvelope


import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from tools.plot_tools import prep_plot

CO2_DATA_URL ="https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_mlo.txt"
ECONOMIES_1 = ['GRC',  'CYP', 'FRA', 'WLD']
ECONOMIES_1 = ['GRC', 'CYP', 'WLD']
ECONOMIES_2 = ['CYP',  'WLD']
SERIES = ['NY.GDP.PCAP.CD', 'SP.POP.TOTL']
OUTPUT_DIR = 'output/cyprus_analytics'
DEBUG=False


MAX_IND_LENGTH = 60
MAX_IND = 5
MIN_NB_DATA=20
MAX_NB_OUTLIERS=3
MIN_SLOPE=.15
MIN_MAXMIN=.15


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
                    max_ind=MAX_IND, 
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
    
    inds=filter_inds_on_length(inds, max_ind=20*max_ind, max_ind_length=max_ind_length)
    print('1 >>> inds:', len(inds))

    df = wb.data.DataFrame(inds, economies)

    inds=filter_inds_on_maxmin(df, inds, min_maxmin=min_maxmin)
    print('2 >>> inds:', len(inds))

    inds=filter_inds_on_slope(df, inds, min_slope=min_slope)
    print('3 >>> inds:', len(inds))

    inds=filter_inds_nb_outliers(df, inds, min_nb_data=min_nb_data, max_nb_outliers=max_nb_outliers)
    print('4 >>> inds:', len(inds))

    inds=filter_inds_on_length(inds, max_ind=max_ind, max_ind_length=max_ind_length)
    print('5 >>> inds:', len(inds))
    df = wb.data.DataFrame(inds, economies)

    data = {'df':df, 'inds': inds, 'topic':topic}
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

    print(f'>>> countries_nocyp: {countries_nocyp}')
    print(f'>>> countries_cyp: {countries_cyp}')

    return df, countries_nocyp, countries_cyp


def plot_df(df,title, economies, index, output_dir):

    df, countries_nocyp, countries_cyp=pref_df(df, economies)

    linewidth=5
    font_scale=3

    prep_plot(font_scale=font_scale)
    plt.rcParams["figure.figsize"] = [16, 9]

    g1=sns.lineplot(data=df[countries_nocyp], legend=True,  sizes=(10, 400),linewidth=linewidth, dashes=False)
    box = g1.get_position()
    g1.set_position([box.x0, box.y0, box.width * 0.9, box.height])

    g2=sns.lineplot(data=df[countries_cyp],  legend=False,   sizes=(10, 400),  palette=['orange'], linewidth=linewidth, dashes=False)
    box = g2.get_position()
    g2.set_position([box.x0, box.y0, box.width * 0.9, box.height])

    handles, _ = g2.get_legend_handles_labels()
    line = mlines.Line2D([], [], color='orange', label='Cyprus', linewidth=linewidth)
    handles.insert(0, line)
   
    for h in handles:
        h.set_linewidth(linewidth)

    plt.legend(handles=handles, loc='center right', bbox_to_anchor=(1.35, 0.5), ncol=1)


    ax=g2

    #title = title.replace(', ', ',\n')
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

    # plot the legend
    output_png=os.path.join(output_dir, f'data_plot_{index}.png')

    plt.savefig(output_png, format='png', dpi=600)
    show=False
    if show:
        plt.show()
    plt.close('all')
    plt.clf()


def narrate_df(df, title, economies, index, output_dir):

    df, countries_nocyp, countries_cyp=pref_df(df, economies)
    output_txt=os.path.join(output_dir, f'data_text_{index}.txt')

    df_nonan=df[~np.isnan(df).any(axis=1)]
    df = df.interpolate(method='linear', axis=0, limit_direction='both')
    df = df.astype(float)

    topic = title.split(',')[0]

    trend = 'stayed the same'

    with open(output_txt, "w") as f:
        f.write(f"Let's look at the {topic}.\n")
        for c in countries_cyp:
            f.write(f"From {df_nonan.index[0]} to {df_nonan.index[-1]} {c}.\n")
            f.write(f"Has seen {topic} {trend}.\n")

        f.write(f"During that same period\n")
        for c in countries_nocyp:
            f.write(f"The {topic} {trend} for the {c}\n")      




def create_media(data, economies, output_dir=OUTPUT_DIR):

    topic_name=data['topic']['value']
    topic_description=data['topic']['sourceNote']
    text_file = os.path.join(OUTPUT_DIR, 'notes.txt')

    with open(text_file, 'w') as f:
        f.write(topic_name)
        f.write('\n\n')        
        f.write(topic_description) 
        f.write('\n\n')

        for index,  ind in enumerate(data['inds']):
            title=get_title(ind)
            f.write(title)  
            f.write('\n\n')
            f.write("Data is...")  
            f.write('\n\n')   

    for index,  ind in enumerate(data['inds']):
        title=get_title(ind)
        df=wb.data.DataFrame(ind, economies)
        plot_df(df,title, economies, index, output_dir)

        narrate_df(df,title, economies, index, output_dir)

    return

if __name__ == "__main__":

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
        create_media(data=data, economies=ECONOMIES_2, output_dir=OUTPUT_DIR)
        break
        





