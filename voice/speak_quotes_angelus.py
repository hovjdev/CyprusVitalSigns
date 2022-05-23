import subprocess

quotes=[
"Angelus Novus",
"A text by Walter Benjamin",
"",
"",
"Angelus Novus is looking as though he is about to move away from something,",
"He is fixedly contemplating.",
"His eyes are staring,",
"His mouth is open,",
"His wings are spread.",
"This is how one pictures the angel of history.",
"His face is turned toward the past.",
"Where we perceive a chain of events,",
"He sees one single catastrophe,",
"Which keeps piling wreckage upon wreckage,",
"And hurls it in front of his feet.",
"The angel would like to stay,",
"Awaken the dead,",
"And make whole what has been smashed.",
"But a storm is blowing from Paradise.",
"It has got caught in his wings,",
"With such violence,",
"That the angel can no longer close them.",
"The storm irresistibly propels him into the future,",
"To which his back is turned,",
"While the pile of debris before him grows skyward.",
"This storm is what we call progress.",
""]





def execute_unix(inputcommand):
   p = subprocess.Popen(inputcommand, stdout=subprocess.PIPE, shell=True)
   (output, err) = p.communicate()
   return output

joined = ' '


short_silence=5
long_silence=10

c=f"ffmpeg -f lavfi -i anullsrc=r=24000:cl=mono -t {short_silence}  -q:a 9 -acodec libmp3lame hold/silence-short.mp3"
execute_unix(c)
c=f"ffmpeg -f lavfi -i anullsrc=r=24000:cl=mono -t {long_silence}  -q:a 9 -acodec libmp3lame hold/silence-long.mp3"
execute_unix(c)

for i, q in enumerate(quotes):


    index = '0'*(2-len(str(i)))+str(i)

    if q is not "":
        f = open("quote.txt", "w")
        f.write(q)
        f.close()

        c =  f'gtts-cli -f quote.txt --output {index}_1_quote.mp3'
        execute_unix(c)
    else:
        c=f"cp hold/silence-short.mp3 {index}_1_quote.mp3"
        execute_unix(c)



    c= f'ffmpeg -i "concat:{index}_1_quote.mp3|hold/silence-short.mp3" -acodec copy {index}.mp3'
    execute_unix(c)


    c=f'rm -rf {index}_1_quote.mp3'
    execute_unix(c)


    joined += f'{index}.mp3 '




c= f'sox {joined} output.mp3'
print(c)
execute_unix(c)




#c=f'ffmpeg -i output.mp3 -filter:a "asetrate=r=30K" -vn test2.mp3'
#execute_unix(c)