import os
import re
import tempfile
import random
from pydub import AudioSegment
from gtts import gTTS


def paraphrase_text(text, parrot, do_diverse=True, use_gpu=False) :

    if not parrot:
        print("Warning: parrot not provided")
        return text

    texts = text.split('\n')
    ptexts = []
    for text in texts:
        if not text: continue
        para_phrases = parrot.augment(input_phrase=text, use_gpu=use_gpu, do_diverse=do_diverse)
        print(f">>This is the original text:{text}")
        if para_phrases is None: continue
        if len(para_phrases) < 1: para_phrases=[""]
        text=random.choice(para_phrases)[0]
        print(f">> And the paraphrased text:{text}")
        ptexts.append(text)
    text='\n'.join(ptexts)

    return text


def textfile_to_wav(text_file, output_wav_file, parrot=None):

    with open(text_file, 'r') as f:
        text = f.read()
        
        if parrot:
            text = paraphrase_text(text, parrot)
            
        text_to_speach(text, output_wav_file)
        
    return

def text_to_speach(text, output_wav_file):

    with tempfile.TemporaryDirectory() as tmpdirname:
        text = text.replace(". ", ".. ")
        text = text.replace(", ", ",, ")
        text_list= re.split(r', |\. |\n', text)

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


def combine_wav_files(wav_files, output_wav_file, silence_duration_ms=300):
       
        combined_audio=None 
        silence=None

        if silence_duration_ms>0:
            silence = AudioSegment.silent(duration=silence_duration_ms) 
            combined_audio = AudioSegment.silent(duration=silence_duration_ms) 

        for m in wav_files:
            m = AudioSegment.from_file(m)

            if combined_audio is None:
                combined_audio=m
            else:
                combined_audio = combined_audio+m

            if silence:
                combined_audio=combined_audio+silence

        if silence:
            for i in range(5):
                combined_audio=combined_audio+silence

        combined_audio.export(output_wav_file, format="wav")

        return

