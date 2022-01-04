import os
import numpy as np
import pandas as pd
from scipy.io.wavfile import write
from scipy import signal

import seaborn as sns
import matplotlib.pyplot as plt

from tools.plot_tools import prep_plot
from tools.tune_audio import tune_audio_data

DATA_FILE_MONTHLY = "input/rainfall/monthly-climatology-of-min-temperature,-mean-temperature,-max-temperature-&-precipitation-1991-2020_br__cyprus.xlsx"
DATA_FILE_ANNUAL = "input/rainfall/pr_timeseries_annual_cru_1901-2020_CYP.xlsx"
OUTPUT_DIR = "output/rainfall"

os.system(f'mkdir -p {OUTPUT_DIR}')

def read_data(data_file):
    df = pd.read_excel(data_file, skiprows=0, header=0, index_col=0)
    #df.index.name='month'
    #df=df.drop(['TOTAL'], axis=0)
    print(df)
    print(df.columns)
    return df

def nan_helper(y):
    return np.isnan(y), lambda z: z.nonzero()[0]

def smooth(y, box_pts):
    box = np.ones(box_pts)
    y_smooth = np.convolve(y, box, mode='same')/box_pts
    return y_smooth

def process_data(precipitation, fs):
    n1 = 40
    data = []

    precipitation = (precipitation.max() - precipitation) / (precipitation.max() - precipitation.min())
    for p in precipitation:

        n=int(1000 * (p+.5))
        print(f"n:{n}")
        f=10 + 10000*np.power(0.5*precipitation,4)
        print(f)
        x = np.fft.ifft(f, n=n)
        xr = x.real + x.imag
        xr=xr.flatten()

        p1 = np.percentile(xr, 5)
        p99 = np.percentile(xr, 95)

        xr[xr<p1]=p1
        xr[xr>p99]=p99

        a = np.full( ( int(len(xr)*1.02)), np.nan)
        a[int(len(xr)*0.01):int(len(xr)*0.01)+len(xr)]=xr
        a[0]=0
        a[-1]=0
        nans, x = nan_helper(a)
        a[nans]= np.interp(x(nans), x(~nans), a[~nans])

        for _ in range(50):
            a=smooth(a, 20)

        xr = tune_audio_data(a)

        for _ in range(n1):
            data.extend(xr.tolist())

    xr = np.array(data)
    xr= xr.flatten()


    sos = signal.butter(10, 60, 'hp', fs=fs, output='sos')
    xr = signal.sosfilt(sos, xr)
    sos = signal.butter(10, 15000, 'lp', fs=fs, output='sos')
    xr = signal.sosfilt(sos, xr)
    return xr




dfa = read_data(DATA_FILE_ANNUAL)
dfm = read_data(DATA_FILE_MONTHLY)
dfm['Month']=dfm.index
dfa['Year']=dfa.index


prep_plot()



precipitation = dfa['Cyprus precipitation (mm)'].to_numpy()
precipitation_smooth = precipitation.copy()

for _ in range(1):
        precipitation_smooth=smooth(precipitation_smooth, 10)

dfa['Cyprus precipitation smooth (mm)'] = precipitation_smooth


plt.rcParams["figure.figsize"] = [16, 9]
g=sns.lineplot( x='Year', y='Cyprus precipitation (mm)', data=dfa, color='aquamarine')
g=sns.regplot( x='Year', y='Cyprus precipitation (mm)', data=dfa, color='steelblue')
plt.savefig(os.path.join(OUTPUT_DIR, 'Cyprus_precipitation_annually.png'), format='png', dpi=600)
plt.close('all')

dfm['Month'] = dfm.index
ax = sns.barplot( x='Month', y='Precipitation (mm)', data=dfm, color='aquamarine')
plt.savefig(os.path.join(OUTPUT_DIR, 'Cyprus_precipitation_monthly.png'), format='png', dpi=600)
plt.close('all')


fs=400000
xr = process_data(precipitation, fs)
t = np.arange(len(xr))



g = sns.lineplot(x=t[0:20000], y=xr[0:20000] , label='waveform')
plt.show()


data=xr*3
scaled = np.int16(data/np.max(np.abs(data)) * 32767)
write(os.path.join(OUTPUT_DIR, 'rainfall.wav'), int(fs*1.0), scaled)


with open(os.path.join(OUTPUT_DIR, 'rainfall.npy'), 'wb') as f:
    np.save(f, xr[0:20000])
