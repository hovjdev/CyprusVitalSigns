import subprocess
from gtts import gTTS


quotes=[
"Most certainly.",
"They have begun a process of industrialization which is very much like the process",
"that the industrialized nations have adopted not long ago.",
"And they have adopted it,",
"because they feel that it is the only way to achieve the economic development levels,"
"that theindustrialized nations have reached now.",
"So they are pretty much going to go along those lines.",
"And, as you said, if that were to continue in 20 or 30 years,",
"you would see the problem are a lot more aggravated than it already is now.",
"",
"",
"Oh that would be preposterous.",
"That would never be accepted.",
"It would never be accepted because you go through your levels of development,",
"and then turn around and tell the developing countries",
"that you cannot develop to the same levels as we have.",
"What I would suggest is",
"that they should in turn talk about providing for the same kind of economic development,",
"but in a different path."
"A path that does not rely",
"upon the burning of fossil fuels,"
"that does not rely on the same development techniques that thedeveloped nations have adopted."
]

TLD='co.in'


def execute_unix(inputcommand):
   p = subprocess.Popen(inputcommand, stdout=subprocess.PIPE, shell=True)
   (output, err) = p.communicate()
   return output

def dotts(text, output):
    if text:
        tts = gTTS(text, lang='en', tld=TLD)
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
