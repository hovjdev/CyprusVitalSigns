import os
import numpy as np
import pandas as pd
from scipy.io.wavfile import write
import seaborn as sns
import matplotlib.pyplot as plt

from tools.plot_tools import prep_plot

DATA_FILE = "input/tourist_arrivals/Cyprus-tourist-arrivals.xls"
OUTPUT_DIR = "output/tourist_arrivals"

os.system(f'mkdir -p {OUTPUT_DIR}')


def read_data(data_file):
    df = pd.read_excel(data_file, skiprows=0, header=0, index_col=0)
    df.index.name='month'
    df=df.drop(['TOTAL'], axis=0)
    print(df)
    print(df.columns)
    return df

def nan_helper(y):
    return np.isnan(y), lambda z: z.nonzero()[0]


df = read_data(DATA_FILE)
df_original = df.copy()
df = df.melt(ignore_index=False)
df.columns = ['year', 'arrivals']
df.reset_index(inplace=True)
print(df)

prep_plot()


g=sns.factorplot(x = 'month', y='arrivals',hue = 'year',data=df, kind='bar',
    legend=False, palette="Blues", linewidth=0,
    height=9,
    aspect=16/9)
plt.subplots_adjust(right=0.85)
plt.legend(loc='center right', bbox_to_anchor=(1, .05, 1.05,.9), mode="expand", frameon=False)
plt.savefig(os.path.join(OUTPUT_DIR, 'tourist_arrivals.png'), format='png', dpi=600)
plt.close('all')


df = df_original.copy()
d = []
n=2000
n1=3
n2=5
n3=5
for _ in range(n2):
    for c in df.columns:
        for _ in range(n1):
            s = df[c].to_numpy()
            s=(s- s.min()) / (s.max() - s.min())
            s=s*1000. + 200.
            x = np.fft.ifft(s, n=n)
            xr = x.real - x.imag
            xr=xr.flatten()

            a = np.full( ( int(len(xr)*1.2)), np.nan)
            a[int(len(xr)*0.1):int(len(xr)*0.1)+len(xr)]=xr
            a[0]=0
            a[-1]=0

            nans, x = nan_helper(a)
            a[nans]= np.interp(x(nans), x(~nans), a[~nans])

            xr=np.sin(a*10.)

            d.append(xr)



xr = np.array(d)
xr= xr.flatten()
#xr = np.arctan(xr/10.)
xr=(xr-xr.min()) / (xr.max()-xr.min())


d=[]
for _ in range(n3):
    d.append(xr)

xr = np.array(d)
xr= xr.flatten()
t = np.arange(len(xr))


xr = xr * 2. - 1.


g = sns.lineplot(x=t[0:2000], y=xr[0:2000] , label='waveform')
plt.show()


data=xr
scaled = np.int16(data/np.max(np.abs(data)) * 32767)
write(os.path.join(OUTPUT_DIR, 'tourist_arrivals.wav'), 5000, scaled)

with open(os.path.join(OUTPUT_DIR, 'tourist_arrivals.npy'), 'wb') as f:
    np.save(f, xr[0:2000])
