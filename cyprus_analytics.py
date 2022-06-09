import os
import random
from re import I
import wbgapi as wb
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.covariance import EllipticEnvelope

from tools.plot_tools import prep_plot

CO2_DATA_URL ="https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_mlo.txt"
ECONOMIES_1 = ['GRC',  'CYP', 'FRA', 'WLD']
ECONOMIES_1 = ['GRC', 'CYP', 'WLD']
ECONOMIES_2 = ['CYP', 'WLD']
SERIES = ['NY.GDP.PCAP.CD', 'SP.POP.TOTL']
OUTPUT_DIR = 'output/cyprus_analytics'
DEBUG=False


MAX_IND_LENGTH = 50
MAX_IND = 5
MIN_NB_DATA=15
MAX_NB_OUTLIERS=2
MIN_SLOPE=.2
MIN_MAXMIN=.2

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


        if skip:
            continue
        indsf.append(ind)



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
    if DEBUG:
        print(topic)
    inds = get_indicators(topic['id'])
    if DEBUG:
        print(inds)
    
    inds=filter_inds_on_length(inds, max_ind=10*max_ind, max_ind_length=max_ind_length)
    assert len(inds)>0
    print('1 >>> inds:', inds)

    df = wb.data.DataFrame(inds, economies)

    inds=filter_inds_on_maxmin(df, inds, min_maxmin=min_maxmin)
    print('2 >>> inds:', inds)

    inds=filter_inds_on_slope(df, inds, min_slope=min_slope)
    print('3 >>> inds:', inds)
    
    inds=filter_inds_nb_outliers(df, inds, min_nb_data=min_nb_data, max_nb_outliers=max_nb_outliers)
    print('4 >>> inds:', inds)

    inds=filter_inds_on_length(inds, max_ind=max_ind, max_ind_length=max_ind_length)
    print('5 >>> inds:', inds)
    df = wb.data.DataFrame(inds, economies)

    data = {'df':df, 'inds': inds, 'topic':topic}
    return data

def plot_df(df,title, economies, index, output_dir):
    df.columns = df.columns.str.replace("YR", "")
    df=df.T

    for c in economies:
        name=get_economie_name(c)
        df.columns = df.columns.str.replace(c, name)

    linewidth=10
    font_scale=4
    prep_plot(font_scale=font_scale)
    ax=sns.lineplot(data=df, linewidth=linewidth, dashes=False)

    #title = title.replace(', ', ',\n')
    ax.set_title(title)

    nbticks=6
    nbt = int(len(ax.xaxis.get_ticklabels())/nbticks)+1
    for i, tick in enumerate(reversed(ax.xaxis.get_ticklabels())):
        if i % nbt != 0:
            tick.set_visible(False) 
    '''nbt = int(len(ax.yaxis.get_ticklabels())/nbticks)+1     
    for i, tick in enumerate(reversed(ax.yaxis.get_ticklabels())):
        if i % nbt != 0:
            tick.set_visible(False)         
    '''

    leg = ax.legend()
    for line in leg.get_lines():
        line.set_linewidth(linewidth)

    ax.figure.savefig(os.path.join(output_dir, f'image{index}.png'))
    plt.close(ax.figure)

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
            data = get_random_data(economies=ECONOMIES_1)
            print(data)
            create_media(data=data, economies=ECONOMIES_2, output_dir=OUTPUT_DIR)
        except Exception as e:
            print(str(e))
            print(f"Try {i} failed")
            print(data)
            continue
        break




