
import os
import argparse
import random

import numpy as np
import matplotlib.pyplot as plt


import tools.sonify as sonify
from midi2audio import FluidSynth
from pydub import AudioSegment

from sklearn.linear_model import Ridge
from sklearn.preprocessing import SplineTransformer
from sklearn.pipeline import make_pipeline
from tools.file_utils import create_dir, delete_previous_files
from tools.plot_tools import prep_plot






DEBUG=False
OUTPUT_DIR = 'output/cyprus_sound'

MAXFILES=6
NB1=80

DEBUG=False

def nan_helper(y):
    return np.isnan(y), lambda z: z.nonzero()[0]

def smooth(y, box_pts):
    box = np.ones(box_pts)
    y_smooth = np.convolve(y, box, mode='same')/box_pts
    return y_smooth



def get_npy_files(filepath=os.path.join(OUTPUT_DIR, '..)')):
    nyp_files=[]
    for root, dirs, files in os.walk(filepath):
        for f in files:
            if f.endswith('.npy'):
                nyp_files.append(os.path.join(root, f))

    return nyp_files

def interpolate(y):
    def nan_helper(y):
        return np.isnan(y), lambda z: z.nonzero()[0]
    nans, x= nan_helper(y)
    y[nans]= np.interp(x(nans), x(~nans), y[~nans])
    return y



def create_sound(nyp_files, output_dir):

    random.shuffle(nyp_files)
    nyp_files=nyp_files[:MAXFILES]

    YYs=[]
    for f in nyp_files:
        print(f)
        Y=np.load(f)
        Y=interpolate(Y)
        n = len(Y)
        if n < 5:
            continue
        print(f'n:{n}')

        X=np.linspace(0,1,n)
        XX=np.linspace(0,1,NB1)
        degree=min(50, int(n-3))
        
        model = make_pipeline(SplineTransformer(n_knots=degree+1, degree=degree), Ridge(alpha=1e-3))
        model.fit(X[:, np.newaxis], Y)
        YY = model.predict(XX[:, np.newaxis])

        if DEBUG:
            fig, ax = plt.subplots()
            ax.scatter(X[:, np.newaxis], Y, label="training points")
            ax.scatter(XX[:, np.newaxis], YY, label="pred")
            plt.show()

        YY = (YY-YY.min())/(YY.max()-YY.min())
        YYs.append(YY)


    # create MIDI
    assert len(YYs) == len(nyp_files)
    instuments = list(sonify.INSTRUMENTS.keys())
    #instuments = ['rock organ', 'oboe', 'flute', 'trombone', 'tuba']

    instruments_to_add=[]
    for _ in range(len(YYs)):
        instruments_to_add.append(random.choice(instuments))
    print(f'instuments: {instruments_to_add}')

    multitrack_data =[]
    for YY in YYs:
        assert len(YY) == NB1
        multitrack_data.append([])
        for i in range(NB1):
                multitrack_data[-1].append(
                        (i,  
                        YY[i],
                        .000005))
    

    multitrack_data_with_instruments = []
    for index, track in enumerate(multitrack_data):
        multitrack_data_with_instruments.append([instruments_to_add[index]] + track)
        
        
    max_number_of_beats = multitrack_data_with_instruments[0][-1][0]

    bass_drum = []
    for beat in range(0, int(max_number_of_beats + 1)):
        bass_drum.append((beat, 1)) 

    beat_track = ['bass drum 1'] + bass_drum
    #multitrack_data_with_instruments.append(beat_track)

    output_midi = os.path.join(OUTPUT_DIR, "sound.midi")
    sonify.create_midi_from_data(multitrack_data_with_instruments, 
                        outputfile=output_midi,
                        track_type='multiple', key='c_sharp_major')

    if os.path.exists(output_midi):
        output_wav = os.path.join(OUTPUT_DIR, "1_sound.wav")
        fs = FluidSynth()
        fs.midi_to_audio(output_midi, output_wav)
        audio = AudioSegment.from_wav(output_wav)
        audio=audio.normalize()
        audio=audio-10
        fade_time=300
        audio = audio.fade_in(fade_time).fade_out(fade_time)
        audio.export(output_wav)



    prep_plot(font_scale=1)
    plt.rcParams["figure.figsize"] = [16, 9]



    #PLOT
    if True:
        fig, ax = plt.subplots(len(nyp_files))
        for i, f in enumerate(nyp_files):
            print(f)
            Y=np.load(f)
            Y=interpolate(Y)
            Y = (Y-Y.min())/(Y.max()-Y.min())
            ax[i].plot(Y, color='orange', linewidth=5)

        plt.suptitle("Data sonification",  fontsize=20)    
        #plt.show()

        output_png = os.path.join(OUTPUT_DIR, "sound.png")
        plt.savefig(output_png, format='png', dpi=600)
        plt.close('all')
        

    output_txt = os.path.join(OUTPUT_DIR, "0_intro.txt")
    txts = [
        "And now let's transform today's data into a sound representation.",
        "Let's now listen to an audio representation of today's data.",
        "We shall now experience a sonified version of today's data.",
        "And now, let's percieve data as a sound experience."
    ]
    with open(output_txt, 'w') as f:
        f.write(random.choice(txts))


    if DEBUG:
        fig, ax = plt.subplots(len(YYs))
        for i, Y in enumerate(YYs):
            Y = (Y-Y.min())/(Y.max()-Y.min())
            ax[i].plot(Y, color='magenta', linewidth=5)

        plt.suptitle("Data to sound",  fontsize=30)    
        plt.show()



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


    create_dir(OUTPUT_DIR)
    delete_previous_files(OUTPUT_DIR)

    nyp_files = get_npy_files(filepath=os.path.join(OUTPUT_DIR, '..'))
    print(f'nyp_files: {nyp_files}')

    if len(nyp_files) < 1:
        exit(1)

    create_sound(nyp_files=nyp_files, output_dir=OUTPUT_DIR)

