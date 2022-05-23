import subprocess
from gtts import gTTS


quotes=[
    'Where do we come from?',
    'Where are we going?',
    'What are we?',
    'What caused the instability?',
    'We came on a grand tour.',
    'We commissioned portraits, of ourselves',
    'We came on foot.',
    'We came on jetliners.',
    'We came.',
    'We left a place in disarray.',
    'We were gifted with fire.',
    'We ignited.',
    'We got carried away.',
    'We were blind-sighted.',
    'We didn’t panic.',
    'We dragged the living.',
    'They once lived.',
    'We were hard-pressed to join them.',
]

    

TLD='com'


def execute_unix(inputcommand):
   p = subprocess.Popen(inputcommand, stdout=subprocess.PIPE, shell=True)
   (output, err) = p.communicate()
   return output

def dotts(text, output):
    if text:
        tts = gTTS(text, lang='en', tld=TLD, slow=False)
        tts.save(output)
    else:
        inputcommand=f"cp hold/silence-short.mp3 " + output
        output=execute_unix(inputcommand)
        return output

joined = ' '


short_silence=.2
long_silence=1

c=f"rm -rf *.mp3"
execute_unix(c)
c=f"rm -rf hold/*.mp3"
execute_unix(c)

c=f"ffmpeg -f lavfi -i anullsrc=r=24000:cl=mono -t {short_silence}  -q:a 9 -acodec libmp3lame hold/silence-short.mp3"
execute_unix(c)
c=f"ffmpeg -f lavfi -i anullsrc=r=24000:cl=mono -t {long_silence}  -q:a 9 -acodec libmp3lame hold/silence-long.mp3"
execute_unix(c)

for i, q in enumerate(quotes):

    index = '0'*(2-len(str(i)))+str(i)
    dotts(q, f"{index}_1_quote.mp3")


    c= f'ffmpeg -i "concat:{index}_1_quote.mp3|hold/silence-short.mp3" -acodec copy {index}_2_quote.mp3'
    execute_unix(c)


    c=f'rm -rf {index}_1_quote.mp3'
    execute_unix(c)

    c= f'sox {index}_2_quote.mp3 {index}.mp3 pad 0 .5  pitch -75  speed 0.83 bass 3 treble -10  biquad .99 .9 .8 .99 .8 .3  reverb 2 echo 0.8 0.88 6 0.4 fir 0.0195 −0.082 0.234 0.891 −0.145 0.043  norm -0.1 '
    execute_unix(c)

    c=f'rm -rf {index}_2_quote.mp3'
    execute_unix(c)

    joined += f'{index}.mp3 '




c= f'sox {joined} output.mp3'
print(c)
execute_unix(c)




