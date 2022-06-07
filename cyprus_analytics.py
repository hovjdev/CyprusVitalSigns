import os
import random
import wbgapi as wb
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from tools.plot_tools import prep_plot

CO2_DATA_URL ="https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_mlo.txt"
ECONOMIES = ['CYP', 'GRC']
SERIES = ['NY.GDP.PCAP.CD', 'SP.POP.TOTL']
OUTPUT_DIR = 'output/cyprus_analytics'
DEBUG=False


def get_co2_data():
    df=pd.read_csv(CO2_DATA_URL, delim_whitespace=True,  comment='#', header=None)
    df.columns=['year', 'mean', 'unc']
    return df

def get_wb_topics():
    topics=list(wb.topic.list())
    return topics

def get_ecolomic_data(series=SERIES, economies=ECONOMIES):
    df = wb.data.DataFrame(series, economies) 
    return df

def get_indicators(topic_nb):
    inds = wb.topic.members(topic_nb)
    return inds

def create_dir(path):
    try: 
        os.mkdir(path) 
    except OSError as error: 
        print(error)  

def get_random_topic():
    topics=get_wb_topics()
    topic=random.choice(topics)
    return topic

def get_economie_name(id):
    l=list(wb.economy.list(id))
    if not len(l): return ""
    return l[0]['value']

def get_random_indicators(topic_nb, nb_inds):
    inds = list(get_indicators(topic_nb=topic_nb))
    random.shuffle(inds)
    nb_inds = min(len(inds), nb_inds)
    return inds[:nb_inds]

def get_random_data(economies, nb=5):
    topic=get_random_topic()
    if DEBUG:
        print(topic)
    inds = get_random_indicators(topic['id'], nb_inds=nb)
    if DEBUG:
        print(inds)
    df = wb.data.DataFrame(inds, economies)
    data = {'df':df, 'inds': inds, 'topic':topic}
    return data

def create_media(data, economies=ECONOMIES, output_dir=OUTPUT_DIR):

    topic_name=data['topic']['value']
    topic_description=data['topic']['sourceNote']
    text_file = os.path.join(OUTPUT_DIR, 'notes.txt')
    
    with open(text_file, 'w') as f:
        f.write(topic_name)
        f.write('\n\n')        
        f.write(topic_description) 
        f.write('\n\n')                

        for index,  ind in enumerate(data['inds']):
            info=wb.series.list(ind)
            title='None'
            for i in info:
                title=str(i['value'])
                f.write(str(i['value']))  
                f.write('\n\n')
            f.write("Data is...")  
            f.write('\n\n')   

            df=wb.data.DataFrame(ind, economies)
            df.columns = df.columns.str.replace("YR", "")
            df=df.T

            for c in economies:
                name=get_economie_name(c)
                df.columns = df.columns.str.replace(c, name)

            linewidth=10
            font_scale=3
            prep_plot(font_scale=font_scale)
            ax=sns.lineplot(data=df, linewidth=linewidth, dashes=False)

            title = title.replace(', ', ',\n')
            ax.set_title(title)

            nbticks=5
            nbt = int(len(ax.xaxis.get_ticklabels())/nbticks)+1
            for i, tick in enumerate(reversed(ax.xaxis.get_ticklabels())):
                if i % nbt != 0:
                    tick.set_visible(False) 
            nbt = int(len(ax.yaxis.get_ticklabels())/nbticks)+1     
            for i, tick in enumerate(reversed(ax.yaxis.get_ticklabels())):
                if i % nbt != 0:
                    tick.set_visible(False)         

            leg = ax.legend()
            for line in leg.get_lines():
                line.set_linewidth(linewidth)

            ax.figure.savefig(os.path.join(output_dir, f'image{index}.png'))
            plt.close(ax.figure)

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


    create_dir(OUTPUT_DIR)
    data = get_random_data(economies=ECONOMIES, nb=10)
    print(data)
    create_media(data=data, economies=ECONOMIES, output_dir=OUTPUT_DIR)


