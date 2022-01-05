import os
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from sklearn.decomposition import PCA
from sklearn.feature_selection import VarianceThreshold

from tools.nltk_tools import sentence_similarity
from tools.plot_tools import prep_plot

def drop_nan(df, cutoff_nan=0.1):
    df_ = df.copy()
    df_=df_.dropna(thresh=int(len(df_) - len(df_)*cutoff_nan), axis=1)
    return df_


def filter_by_rolling_std(df, rolling_window=5, drop_fraction=0.3):
    df_ = df.copy()
    cols_std_percentiles = []
    for c in df_.columns:
        s = df_[c].squeeze()
        sr = s.rolling(rolling_window).std()
        p10 = sr.quantile(0.1)
        p50 = sr.quantile(0.5)
        p90 = sr.quantile(0.9)
        mean= sr.mean()
        cols_std_percentiles.append({'column':c, 'p10':p10, 'p50':p50, 'p90':p90, 'mean':mean})

    to_drop=[]
    # drop very low std
    sorted_cols = sorted(cols_std_percentiles, key=lambda d: d['p10'])
    #print(sorted_cols)
    tmp = [i['column'] for i in sorted_cols]
    to_drop.extend(tmp[0:int(len(df_.columns)*drop_fraction*1./8.)])
    # drop very high std
    sorted_cols = sorted(cols_std_percentiles, key=lambda d: -1.*d['p90'])
    #print(sorted_cols)
    tmp = [i['column'] for i in sorted_cols]
    to_drop.extend(tmp[0:int(len(df_.columns)*drop_fraction*1./8.)])
    # drop very high
    sorted_cols = sorted(cols_std_percentiles, key=lambda d: -1.*d['mean'])
    #print(sorted_cols)
    tmp = [i['column'] for i in sorted_cols]
    to_drop.extend(tmp[0:int(len(df_.columns)*drop_fraction*6./8.)])

    df_ = df_.drop(to_drop, axis=1)
    print(f"Filter column names by rolling std, nb cols={len(df_.columns)}")
    print(f"Columns kept: {sorted(df_.columns)}");print()
    return df_


def filter_by_column_correlation(df, cutoff_corr=0.7):
    df_ = df.copy()
    corr = df_.corr().round(2).abs()
    upper_tri = corr.where(np.triu(np.ones(corr.shape),k=1).astype(np.bool))
    to_drop = [column for column in upper_tri.columns if any(upper_tri[column] > cutoff_corr)]
    df_ = df_.drop(to_drop, axis=1)
    #corr_filtered = df_.corr().round(2).abs()
    #sns.heatmap(corr_filtered, annot=True)
    #plt.show()
    print(f"Filter columns by feature correlation, nb cols={len(df_.columns)}")
    print(f"Columns kept: {sorted(df_.columns)}");print()
    return df_


def filter_by_column_name_similarity(df, cutoff_corr_name=.7):
    df_ = df.copy()
    cols = df_.columns
    corr = df_.corr().round(2).abs()
    for i, c1 in enumerate(cols):
        for j, c2 in enumerate(cols):
            s=sentence_similarity(c1, c2)
            corr[c1][c2]=s
    upper_tri = corr.where(np.triu(np.ones(corr.shape),k=1).astype(np.bool))
    to_drop = [column for column in upper_tri.columns if any(upper_tri[column] > cutoff_corr_name)]
    df_ = df_.drop(to_drop, axis=1)
    print(f"Filter columns by name similarity, nb cols={len(df_.columns)}")
    print(f"Columns kept: {sorted(df_.columns)}");print()
    return df_


def low_variance_threshold(df):
    df_ = df.copy()
    X = df_.to_numpy()
    selector = VarianceThreshold()
    selector.fit(X)
    kept = selector.get_feature_names_out(df_.columns)
    to_drop =  [c for c in df_.columns if c not in kept]
    df_ = df_.drop(to_drop, axis=1)
    print(f"Filter columns by low variance, nb cols={len(df_.columns)}")
    print(f"Columns kept: {sorted(df_.columns)}");print()
    return df_


def read_data(data_file):
    df = pd.read_excel(data_file, skiprows=3, header=0)
    df =df.drop(columns=['Country Name', 'Country Code', 'Indicator Code'])
    df=df.set_index('Indicator Name')
    df.index.name='year'
    df = df.T
    print(df.columns)
    print(df.describe(include='all'))
    return df

def normalize(df):
        df_ = df.copy()
        for column in df_.columns:
            df_[column] = (df_[column] - df_[column].mean()) / df_[column].std()
        return df_

def get_data(data_file, drop_fraction=0.2, cutoff_corr=0.8, cutoff_corr_name=0.7):

    # load data
    df= read_data(data_file=data_file)
    df_original = df.copy()

    # drop nan
    df=drop_nan(df=df, cutoff_nan=0.1)

    # step1: low variance threshold
    df=low_variance_threshold(df=df)

    # step2: normalize
    df=normalize(df=df)

    # step3: filter high rolling std
    df=filter_by_rolling_std(df=df, rolling_window=10, drop_fraction=drop_fraction)

    # step4: filter columns by corellation
    df=filter_by_column_correlation(df=df, cutoff_corr=cutoff_corr)

    # step5: filter column names by similarity
    df = filter_by_column_name_similarity(df=df, cutoff_corr_name=cutoff_corr_name)
    return df





DATA_FILE = "input/worldbank/API_CYP_DS2_en_excel_v2_3472605.xls"
OUTPUT_DIR = "output/worldbank"
os.system(f'mkdir -p {OUTPUT_DIR}')

n_components=3
df = get_data(data_file=DATA_FILE, drop_fraction=0.2, cutoff_corr=0.8, cutoff_corr_name=0.7)


if True:
    # plot selected features
    drop_fraction=0.2
    cutoff_corr=0.8
    cutoff_corr_name=0.
    df = get_data(data_file=DATA_FILE, drop_fraction=0.2, cutoff_corr=0.8, cutoff_corr_name=0.6)
    labels = list(df.index)
    labels = [l if i % 5==0 else " " for i, l in enumerate(labels)  ]
    prep_plot()

    # plot selected features
    fig, ax =plt.subplots(1,1)
    g = sns.lineplot(data=df,  markers=False, dashes=False, linewidth = 3, palette="bright")
    g.set(yticklabels=[], xticklabels=labels)
    g.set(ylabel = None)
    legend_height=0.8
    plt.tight_layout(rect=[0,.05,1,legend_height])
    leg = ax.legend(loc='lower left', bbox_to_anchor=(0,legend_height,1,legend_height), mode="expand", frameon=False)
    for line in leg.get_lines():
        line.set_linewidth(5)
    legend_labels = []
    for t  in leg.get_texts():
        tt = str(t._text)
        t.set_text(re.sub(r"(\s*,.+|\s*\(.+)","", tt))
    plt.xticks(rotation=25)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['left'].set_visible(False)
    plt.savefig(os.path.join(OUTPUT_DIR, 'worldbank_selected.png'), format='png', dpi=600)
    plt.close('all')

    # plot std accross features
    std = df.std(axis=1)
    df_std = std.to_frame(name='Standard deviation')
    g = sns.lineplot(data=df_std,  markers=False, dashes=False, linewidth = 4)
    g.set(xticklabels=labels)
    plt.xticks(rotation=25)
    plt.savefig(os.path.join(OUTPUT_DIR, 'worldbank_stdv.png'), format='png', dpi=600)
    plt.close('all')


df.to_csv(os.path.join(OUTPUT_DIR, "worldbank.csv"))



df = df.interpolate(method='linear',  axis=0, limit_direction='both')
X=df.to_numpy()
pca = PCA(n_components=3, svd_solver='full')
X=pca.fit_transform(X)
X= np.swapaxes(X,0,1)

for i in range(n_components):
    X[i,:] = (X[i] - X[i].min()) / (X[i].max()-X[i].min())

df = df.drop(df.columns, axis=1)
for i in range(n_components):
    df[f'X{i+1}']=X[i]

sns.lineplot(data=df)
plt.xticks(rotation=75)
plt.show()

with open(os.path.join(OUTPUT_DIR, "API_CYP_DS2_en_excel_v2_3472605_n{n_components}.npy"), 'wb') as f:
    np.save(f, df.to_numpy())
