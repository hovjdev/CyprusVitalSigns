import os
import re
import tempfile
from pydub import AudioSegment
from gtts import gTTS


def textfile_to_mp3(text_file, output_mp3_file):

    with open(text_file, 'r') as f:
        text = f.read()
        text_to_speach(text, output_mp3_file)
        
    return

def text_to_speach(text, output_mp3_file):

    with tempfile.TemporaryDirectory() as tmpdirname:
        text = text.replace(". ", ".. ")
        text = text.replace(", ", ",, ")
        text_list= re.split(r', |\. |\n', text)

        mp3_files = []
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
            mp3_files.append(tmp)


        combine_mp3_files(mp3_files, output_mp3_file)


def combine_mp3_files(mp3_files, output_mp3_file, silence_duration_ms=300):
        combined_audio=None
        silence=None
        if silence_duration_ms>0:
            silence = AudioSegment.silent(duration=silence_duration_ms) 

        for m in mp3_files:
            m = AudioSegment.from_file(m, "mp3")
            if combined_audio is None:
                combined_audio=m
            else:
                combined_audio = combined_audio+m
                
            if silence:
                combined_audio=combined_audio+silence

        combined_audio.export(output_mp3_file, format="mp3")
        return

