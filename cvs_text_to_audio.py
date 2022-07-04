import os
import re
import tempfile
import random
from pathlib import Path
from pydub import AudioSegment
from gtts import gTTS

from paraphrase import paraphrase_text


def textfile_to_wav(text_file, output_wav_file, parrot=None):
    
    #print(f">>>textfile_to_wav: {text_file}")

    with open(text_file, 'r') as f:
        text = f.read()
        #print(f">>>text: {text}")
        
        if parrot:
            text = paraphrase_text(text, parrot)
            
        text_to_speach(text, output_wav_file)
        
    return

def text_to_speach(text, output_wav_file):

    with tempfile.TemporaryDirectory() as tmpdirname:
        text = text.replace(". ", ".\n")
        text = text.replace(", ", ",\n")
        text = text.replace(" and ", " and\n")
        text_list= re.split(r'\n', text)

        wav_files = []
        for i, t in enumerate(text_list):
            print(f'>>> gTTS({t})')
            tts=None
            try:
                tts = gTTS(t)
            except Exception as e:
                print(e)
                continue
            if tts is None:
                continue
            tmp = '0'*(4-len(str(i)))+str(i)+'.mp3'
            tmp = os.path.join(tmpdirname, tmp)
            tts.save(tmp)

            audio = AudioSegment.from_mp3(tmp)
            tmp = '0'*(4-len(str(i)))+str(i)+'.wav'
            tmp = os.path.join(tmpdirname, tmp)
            audio.export(tmp, format="wav")

            wav_files.append(tmp)          

        combine_wav_files(wav_files, output_wav_file)


def combine_wav_files(wav_files, output_wav_file, silence_duration_ms=200):
       
        combined_audio=None 
        silence=None

        if silence_duration_ms>0:
            silence = AudioSegment.silent(duration=silence_duration_ms)
            combined_audio = AudioSegment.silent(duration=silence_duration_ms)
            for i in range(20):
                combined_audio=combined_audio+silence

        for  m in wav_files:
            m = AudioSegment.from_file(m)

            if combined_audio is None:
                combined_audio=m
            else:
                combined_audio = combined_audio+m

            if silence:
                combined_audio=combined_audio+silence

        if silence:
            for i in range(20):
                combined_audio=combined_audio+silence

        combined_audio.export(output_wav_file, format="wav")

        return



if __name__ == "__main__":

    dir_path = "output/cvs_data_vids/6fac0e023c334c3fa6ed222cff58d654/weath"
    text_files = list(Path(dir_path).glob("*.txt"))
    text_files.sort()

    for t in text_files:
        t=str(t)
        assert t[-4:]=='.txt'
        wav_file = t[:-4]+'.wav'
        textfile_to_wav(text_file=t, output_wav_file=wav_file, parrot=None)
