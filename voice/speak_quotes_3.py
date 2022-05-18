import subprocess
from gtts import gTTS


quotes=[
"A historical document",
"",
"A 1988 Debate on Climate Change,",
"on ABC News Nightline.",
"",
"with host Ted Koppel",
"and special guest Doctor Kilaparti Ramakrishna"
]


TLD='ca'


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


short_silence=.3
long_silence=1

c=f"rm -rf *.mp3"
execute_unix(c)
c=f"ffmpeg -f lavfi -i anullsrc=r=24000:cl=mono -t {short_silence}  -q:a 9 -acodec libmp3lame hold/silence-short.mp3"
execute_unix(c)
c=f"ffmpeg -f lavfi -i anullsrc=r=24000:cl=mono -t {long_silence}  -q:a 9 -acodec libmp3lame hold/silence-long.mp3"
execute_unix(c)

for i, q in enumerate(quotes):

    index = '0'*(2-len(str(i)))+str(i)
    dotts(q, f"{index}_1_quote.mp3")


    c= f'ffmpeg -i "concat:{index}_1_quote.mp3|hold/silence-short.mp3" -acodec copy {index}.mp3'
    execute_unix(c)


    c=f'rm -rf {index}_1_quote.mp3'
    execute_unix(c)


    joined += f'{index}.mp3 '




c= f'sox {joined} output.mp3'
print(c)
execute_unix(c)
