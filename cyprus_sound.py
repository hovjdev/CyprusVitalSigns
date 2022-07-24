
import os
import argparse
import random
import shutil



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



def create_wave_file(nyp_files, output_wav):
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

    output_midi = output_wav[:-4] + ".midi"
    sonify.create_midi_from_data(multitrack_data_with_instruments, 
                        outputfile=output_midi,
                        track_type='multiple', key='c_sharp_major')

    if os.path.exists(output_midi):
        fs = FluidSynth()
        fs.midi_to_audio(output_midi, output_wav)
        audio = AudioSegment.from_wav(output_wav)
        audio=audio.normalize()
        audio=audio-1
        fade_time=300
        audio = audio.fade_in(fade_time).fade_out(fade_time)
        audio.export(output_wav, "wav")
        if os.path.exists(output_wav):
            return output_wav
    
    return None



def create_sound(nyp_files, output_dir):

    random.shuffle(nyp_files)
    nyp_files=nyp_files[:MAXFILES]

    nb_nyp_files=len(nyp_files)
    nyp_files_left = nyp_files[:int(nb_nyp_files/2)]
    nyp_files_right = nyp_files[int(nb_nyp_files/2):]

    try:
        assert len(nyp_files_left) > 0 and len(nyp_files_right) > 0
    except Exception as e:
        nyp_files_left=nb_nyp_files
        nyp_files_right=nb_nyp_files
        print(str(e))
    
    tmp_path=os.path.join(OUTPUT_DIR, "TMP")
    create_dir(tmp_path)
    output_wav_left = os.path.join(tmp_path, "1_sound_left.wav")
    output_wav_right = os.path.join(tmp_path, "1_sound_right.wav")

    output_wav_left=create_wave_file(nyp_files_left, output_wav_left)
    output_wav_right=create_wave_file(nyp_files_right, output_wav_right)

    print(output_wav_left)
    print(type(output_wav_left))
    print(output_wav_right)
    print(type(output_wav_right))


    left_channel_as = AudioSegment.from_wav(output_wav_left)
    right_channel_as = AudioSegment.from_wav(output_wav_right)
    left_channel=np.array(left_channel_as.get_array_of_samples())
    right_channel=np.array(right_channel_as.get_array_of_samples())
    #print(left_channel.dtype, right_channel.dtype)
    
    def count_samples(left_channel, right_channel):
        lr=right_channel.shape[0]
        ll=left_channel.shape[0] 
        #print(ll, lr)
        return ll, lr
    
    ll, lr = count_samples(left_channel, right_channel)
    l=max(ll, lr)
    channels=np.zeros((2,l), dtype='int16')
    channels[0,:ll]=left_channel
    channels[1,:lr]=right_channel
    left_channel_tmp=channels[0,:]
    right_channel_tmp=channels[1,:]

    a=np.sin(np.arange(0,l)*2*np.pi/l)**2
    b=np.cos(np.arange(0,l)*2*np.pi/l)**2
    left_channel=a*left_channel_tmp + b*right_channel_tmp
    left_channel=left_channel.astype('int16')
    right_channel=a*right_channel_tmp + b*left_channel_tmp
    right_channel=right_channel.astype('int16')



    left_sound = AudioSegment(
        left_channel.tobytes(), 
        frame_rate=left_channel_as.frame_rate,
        sample_width=left_channel.dtype.itemsize, 
        channels=1
    )
    right_sound = AudioSegment(
        right_channel.tobytes(), 
        frame_rate=right_channel_as.frame_rate,
        sample_width=right_channel.dtype.itemsize, 
        channels=1
    )    

    stereo_sound=AudioSegment.from_mono_audiosegments(left_sound, right_sound)
    output_wav = os.path.join(OUTPUT_DIR, "1_sound.wav")
    stereo_sound.export(output_wav)

    try:
        shutil.rmtree(tmp_path)
        pass
    except Exception as e:
        print(print(str(e)))

    prep_plot(font_scale=1)
    plt.rcParams["figure.figsize"] = [16, 9]

    #PLOT
    if True:
        fig, ax = plt.subplots(nb_nyp_files)
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
        "And now, let's transform today's data into an audio representation.",
        "Let's now listen to an audio representation of today's data.",
        "We shall now experience a sonified version of today's data.",
        "To continue, let's percieve today's data as an audio experience."
    ]
    with open(output_txt, 'w') as f:
        f.write(random.choice(txts))



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

