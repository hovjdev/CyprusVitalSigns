import wbgapi as wb
import pandas as pd

CO2_DATA_URL ="https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_mlo.txt"

ECONOMIES = ['CYP', 'FRA']
SERIES = ['NY.GDP.PCAP.CD', 'SP.POP.TOTL']

def get_co2_data():
    df=pd.read_csv(CO2_DATA_URL, delim_whitespace=True,  comment='#', header=None)
    df.columns=['year', 'mean', 'unc']
    return df

def get_wb_topics():
    topics=list(wb.topic.list())
    return topics

def get_ecolomic_data(series=SERIES, economies=ECONOMIES):
    df = wb.data.DataFrame(series, economies) # most recent 5 years
    return df

def get_indicators(topic_nb):
    inds = wb.series.info(wb.topic.members(topic_nb))
    return inds

if __name__ == "__main__":
    df = get_co2_data()
    print(df)
    topics=get_wb_topics()
    print(topics)
    df = get_ecolomic_data()
    print(df)
    inds = get_indicators(topic_nb=19)
    print(inds)
