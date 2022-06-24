import os
import re
import argparse
import eurostat
import datetime

import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from tools.plot_tools import prep_plot
from tools.file_utils import create_dir, delete_previous_files



DEBUG=True
OUTPUT_DIR = 'output/cyprus_eurostat'


def db_print(s, debug=DEBUG):
    if debug:
        print(s)


def get_codes(keyword = 'tourist'):
    avail_sdmx_df = eurostat.get_avail_sdmx_df()
    subset = eurostat.subset_avail_sdmx_df(avail_sdmx_df, keyword)
    db_print(subset.to_string())


    codes = subset.index.values.tolist()
    db_print(codes)
    return codes



def get_data(code, filters):

    avail_sdmx_df = eurostat.get_avail_sdmx_df()


    db_print(f">>>Getting data for code: {code}")
    dims = eurostat.get_sdmx_dims(code)
    has_cy = False
    dim_cy=None
    for dim in dims:
        dic = eurostat.get_sdmx_dic(code, dim)
        db_print(dic)
        if not dic:
            continue
        if 'CY' in dic:
            dim_cy=dim
            break
    if not dim_cy:
        db_print("CY not found")
        return None
    

    for dim in dims:
        db_print(dim)
        dic = eurostat.get_sdmx_dic(code, dim)
        db_print(dic)


    db_print(code)
    title=avail_sdmx_df.loc[[code]].to_string()
    db_print(f'title: {title}')
    db_print(dim_cy)
    dic = eurostat.get_sdmx_dic(code, dim_cy)
    db_print(dic)

    flags = eurostat.get_sdmx_dic(code, 'OBS_STATUS')
    db_print(flags)
    

    StartPeriod = 2000
    currentDateTime = datetime.datetime.now()
    date = currentDateTime.date()
    year = date.strftime("%Y")
    EndPeriod = int(year)
    filter_pars = filters
    
    df=eurostat.get_sdmx_data_df(code, StartPeriod, EndPeriod, filter_pars, flags = False, verbose=True)
    db_print(df)
    db_print(df.columns.to_list())

    return df, title
        


def prep_df(df):

    df=df.T
    
    assert len(df.columns.to_list())==1
    df.columns = ['Cyprus']
    
    indices = list(df.index.values)
    drop_indices = []
    pattern = re.compile("^(\d\d\d\d-\d\d|\d\d\d\d)$")
    for index in indices:
        if not pattern.match(str(index)):
            drop_indices.append(index)

    print(f"drop_indices: {drop_indices}")
    df = df.drop(index=drop_indices)
    
    indices = list(df.index.values)
    has_months=False
    pattern = re.compile("^(\d\d\d\d-\d\d)$")
    for index in indices:
        if  pattern.match(str(index)):
            has_months=True

    if has_months:
        df.index = pd.MultiIndex.from_tuples([((idx[:4],idx[-2:])) for idx in df.index], names=["Year", "Month"])
    else:
        df.index.name='Year'

    df=df.sort_index()
    df=df.dropna()
    df["Cyprus"] = pd.to_numeric(df["Cyprus"], errors='coerce')
    
    df.reset_index(inplace=True)


    if has_months:
        df['Month'] = df['Month'].map({'01':'January',
                                       '02':'February',
                                       '03':'March',
                                       '04':'April',
                                       '05':'May',
                                       '06':'June',
                                       '07':'July',                                                                                                                                                            
                                       '08':'August',
                                       '09':'September',                                                                                                                                                            
                                       '10':'October',      
                                       '11':'November',                                                                                                            
                                       '12':'December',})

    print(df)
    return df


def plot_df(df, title,  index, output_dir):

    font_scale=2.5
    df.rename(columns={'Cyprus': ''}, inplace=True)

    prep_plot(font_scale=font_scale)
    plt.rcParams["figure.figsize"] = [16, 9]

    ax=None
    if 'Month' in list(df.columns):
        linewidth=1
        if len(df.index) > 60: linewidth=0
        ax = sns.barplot( x='Year', y='', data=df, hue='Month', color='orange', linewidth=linewidth)
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.75, box.height])
        handles, _ = ax.get_legend_handles_labels()
        plt.legend(handles=handles, loc='center right', bbox_to_anchor=(1.45, 0.5), ncol=1)
    else:
        ax = sns.barplot( x='Year', y='', data=df, color='orange')      

    plt.title(title)


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

    # save plot
    output_png=os.path.join(output_dir, f'data_plot_{index}.png')
    plt.savefig(output_png, format='png', dpi=600)

    # save data
    output_data=os.path.join(output_dir, f'data_{index}.npy')
    with open(output_data, 'wb') as f:
        np.save(f, df[''].to_numpy())

    show=False
    if show:
        plt.show()
    plt.close('all')
    plt.clf()

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

    

    codes = get_codes(keyword = 'goals')

    code_selection=['avia_tf_cm',
                    'tour_occ_arm',
                    't2020_rd300',

    ]

    metadata = {
        'avia_tf_cm': {
                'filters':{'GEO': ['CY'], 'UNIT':['NR']}, 
                'title':"Number of commercial flights reported monthly"},
        'tour_occ_arm': {
                'filters': {'GEO': ['CY'], 'UNIT':['NR'], 'NACE_R2':['I551'], 'C_RESID':['FOR']}, 
                'title':"Arrivals at tourist accommodation establishments"},
        't2020_rd300' : {
                'filters': {'GEO': ['CY']}, 
                'title':"Greenhouse gas emissions per capita (tonnes)"},
    }


    create_dir(OUTPUT_DIR)
    delete_previous_files(OUTPUT_DIR)

    for index, code in enumerate(code_selection):


        df, title = get_data(code, metadata[code]['filters'])
        df = prep_df(df)

        plot_df(df, title=metadata[code]['title'],  index=index, output_dir=OUTPUT_DIR)


