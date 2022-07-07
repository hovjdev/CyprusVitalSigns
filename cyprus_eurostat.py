import os
import re
import random
import argparse
import eurostat
import datetime

import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression

from tools.plot_tools import prep_plot
from tools.file_utils import create_dir, delete_previous_files


from parrot import Parrot
from paraphrase import paraphrase_text


DEBUG=False
OUTPUT_DIR = 'output/cyprus_eurostat'
MAX_N=3

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

    db_print(f">>>Getting data for code: {code}")
    df = eurostat.get_data_df(code)
    dim_cy=None
    for col in df.columns:
        col_values = df[col].values.tolist()
        if 'CY' in col_values:
            dim_cy=col
            break
    if not dim_cy:
        db_print("CY not found")
        return None
    
    toc_df = eurostat.get_toc_df()
    toc_df = toc_df[toc_df['code']==code] 

    db_print(code)
    db_print(toc_df)    
    title=toc_df['title'].tolist()
    assert len(title)==1
    title=title[0]
    db_print(f'title: {title}')
    db_print(dim_cy)
    db_print(df)    

    db_print(df.columns)
    for filter in filters:
        for f in filters[filter]:
            df=df[df[filter]==f]



    db_print(df)
    db_print(df.columns.to_list())

    return df, title
        



def get_sdmx_data(code, filters):

    avail_sdmx_df = eurostat.get_avail_sdmx_df()


    db_print(f">>>Getting SDMX data for code: {code}")
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

    
    try:
        assert len(df.columns.to_list())==1
    except Exception as e:
        print(str(e))
        print(df)
        print(f"len(df.columns.to_list()): {len(df.columns.to_list())}")
        raise(e)
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
    #df=df.dropna()
    df["Cyprus"] = pd.to_numeric(df["Cyprus"], errors='coerce')
    
    df = df.interpolate(method='linear', axis=0, limit_direction='both', limit_area='inside')
    df = df[~np.isnan(df).any(axis=1)]

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

    db_print(df)
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



def narrate_df(df, title,  title_short, unit, index, output_dir=OUTPUT_DIR, parrot=None):

    df = df.copy()
    output_txt_file=os.path.join(output_dir, f'data_plot_{index}.txt')

    has_year = 'Year' in df.columns.to_list()

    assert has_year
    df = df.groupby(['Year']).mean()


    def get_min_year_min(df):
        min_year = df[['']].idxmin(skipna=True)
        return min_year[0], df.loc[min_year[0]]['']

    def get_max_year_max(df):
        max_year = df[['']].idxmax(skipna=True)
        return max_year[0], df.loc[max_year[0]]['']

    def get_mean(df):
        return df[''].mean()

    def get_slope_pct(df):

        d = df[''].to_numpy()
        slope = 0
        d = np.reshape(d, (d.shape[0], -1))

        d_mean=np.nanmean(d)
        x=np.arange(d.shape[0])
        x = (x - np.nanmin(x))

        d=np.insert(d, 0, x, axis=1)
        d=d[~np.isnan(d).any(axis=1)]

        x = np.copy(d[::,0]).reshape(-1, 1)
        y = np.copy(d[::,1]).reshape(-1, 1)
        try:
            reg = LinearRegression().fit(x, y)
        except Exception as e:
            print(str(e))
            return -1
        slope = + reg.coef_[0][0]

        slope_pct = (slope / d_mean)*100
        return slope_pct

    slope_pct = get_slope_pct(df)
    min_year, min = get_min_year_min(df)
    max_year, max = get_max_year_max(df)
    mean = get_mean(df)

    print(f'slope_pct: {slope_pct}')
    print(f'min_year: {min_year}')    
    print(f'max_year: {max_year}') 

    

    with open(output_txt_file, "w") as f:
        first=random.choice([
                    "We shall now examine",
                    "And now let's review",
                    "Let's examine",
                    "Let's take a look at",
                    "Let's review",])
        title_split = title.split('(')[0]
        third=random.choice([
                    "data", 
                    "time series",
                    "chart",])

        fourth=random.choice([
                    "with the highest", 
                    "with the biggest",
                    "with most",])

        fifth=random.choice([
                    "with the lowest", 
                    "with the smallest",
                    "with least",])

        max_val= random.choice([
            f"with {str(round(max))} {unit}",
            f"with {str(round(max))} {unit}",            
            "",
        ])

        min_val= random.choice([
            f"with {str(round(min))} {unit}",
            f"with {str(round(min))} {unit}",            
            "",
        ])

        sixth=random.choice([
            "Overall,", 
            "On average,", 
            "Overall,",
            "On average,",
            "In recent years,",
            "On the whole,",
            "Over this period,",
        ])
        
        seventh = " "
        if slope_pct > 0:
            seventh=random.choice([
                " increased by ",
                " rose by ",
            ])
        else:
            seventh=random.choice([
                " decreased by ",
                " fell by ",
            ])


        eight=random.choice([
            "percent each year.", 
        ])

        text = ''
        text += f'{first} the {third} of the {title_split}.\n'
        text += f'{str(max_year)} {max_val} was the  year {fourth} {title_short}.\n'
        text += f'{str(min_year)} {min_val} was the  year {fifth} {title_short}.\n'
        text += f'{sixth} the {title_split}{seventh}{round(slope_pct)} {eight}\n'

        if parrot: 
            text = paraphrase_text(text, parrot)

        print(">>>>text:")
        print(text)
        f.write(text)

        



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

    
    if False and DEBUG:
        codes = get_codes(keyword = 'tourism')
        exit(1)

    code_selection=['avia_tf_cm',
                    'tour_occ_arm',
                    't2020_rd300',
                    'tour_occ_mnor',
                    'env_wat_res',
                    'cli_act_noec',
                    'tin00196',
                    'tin00195',
                    'tin00191']
    
    #code_selection=['tin00195']

    # ramdom selection of indicators
    MAX_N=min(MAX_N, len(code_selection))
    code_selection=random.sample(code_selection, MAX_N)
    print(len(code_selection))

    metadata = {
        'avia_tf_cm': {
                'filters':{'GEO': ['CY'], 'UNIT':['NR']}, 
                'title':"Number of commercial flights reported monthly",
                'title_short':"Number of commercial flights",
                'unit': ""},
        'tour_occ_arm': {
                'filters': {'GEO': ['CY'], 'UNIT':['NR'], 'NACE_R2':['I551'], 'C_RESID':['FOR']}, 
                'title':"Arrivals at tourist accommodation establishments",
                'title_short':"arrivals",
                'unit': ""},
        't2020_rd300' : {
                'filters': {'GEO': ['CY']}, 
                'title':"Greenhouse gas emissions per capita (tonnes)",
                'title_short':"emissions",
                'unit': "tonnes"},     
        'tour_occ_mnor' : {
                'filters': {'GEO': ['CY'], 'ACCOMUNIT': ['BEDRM']}, 
                'title':"Net occupancy rate of bedrooms in hotels accommodations",
                'title_short':"Net occupancy rate",
                'unit': ""},
        'env_wat_res' : {
                'filters': {'geo\\time': ['CY'], 'wat_proc':['RFW_RES'], 'unit':['M3_HAB']}, 
                'title':"Renewable freshwater resources (Cubic metres per inhabitant)",
                'title_short':"Freshwater resources",
                'unit': "Cubic metres per inhabitant"},
        'cli_act_noec' : {
                'filters': {'geo\\time': ['CY'],  'unit':['PC']}, 
                'title':"Share of zero emission vehicles in newly registered passenger cars (%)",
                'title_short':"Share of zero emission vehicle",
                'unit': "Percent"},
        'tin00196' : {
                'filters': {'geo\\time': ['CY'],  'unit':['EUR']}, 
                'title':"Average tourist expenditure per night (Euros)",
                'title_short':"Average expenditure",
                'unit': "Euros"},
        'tin00191' : {
                'filters': {'geo\\time': ['CY'],  'purpose':['PERS_HOL']}, 
                'title':"Number of nights spent on holidays, leisure and recreation",
                'title_short':"Number of nights spent",
                'unit': ""},
        'tin00195' : {
                'filters': {'geo\\time': ['CY'],  'purpose':['TOTAL'], 'duration':['N_GE1']}, 
                'title':"Average expenditure per trip on holidays, leisure and recreation (Euros)",
                'title_short':"Average expenditure",
                'unit': "Euros"}   
    }


    create_dir(OUTPUT_DIR)
    delete_previous_files(OUTPUT_DIR)

    #parrot = Parrot(model_tag="prithivida/parrot_paraphraser_on_T5")
    parrot=None

    for index, code in enumerate(code_selection):

        df = None
        title = None

        if df is None or title is None:
            try:
                df, title = get_sdmx_data(code, metadata[code]['filters'])
            except Exception as e:
                print(str(e))

        if df is None or title is None:
            #try:
                df, title = get_data(code, metadata[code]['filters'])
            #except Exception as e:
            #    print(str(e))      


        if df is None or title is None:
            exit(1)      

        df = prep_df(df)

        plot_df(df, title=metadata[code]['title'],  index=index, output_dir=OUTPUT_DIR)
        narrate_df(df, title=metadata[code]['title'],
                    title_short=metadata[code]['title_short'],
                    unit=metadata[code]['unit'],  
                    index=index, output_dir=OUTPUT_DIR, parrot=parrot)


