import random
from termios import PARODD
from parrot import Parrot



def paraphrase_text(text, parrot, do_diverse=True, use_gpu=False, 
            adequacy_threshold = 0.90, fluency_threshold = 0.90) :

    if not parrot:
        print("Warning: parrot not provided")
        return text

    texts = text.split('\n')
    ptexts = []
    for text in texts:
        if not text: continue
        para_phrases = parrot.augment(
            input_phrase=text, 
            use_gpu=use_gpu, 
            do_diverse=do_diverse, 
            adequacy_threshold=adequacy_threshold,
            fluency_threshold=fluency_threshold)

        print(f">>This is the original text:{text}")
        if para_phrases is None: continue
        if len(para_phrases) < 1: para_phrases=[""]
        text=random.choice(para_phrases)[0]
        print(f">> And the paraphrased text:{text}")
        ptexts.append(text)
    text='\n'.join(ptexts)

    return text



if __name__ == "__main__":

    parrot = Parrot(model_tag="prithivida/parrot_paraphraser_on_T5")
    text = "I've always loved to take long walks in the woods."

    for i in range(100):   
        text = paraphrase_text(text, parrot, 
                adequacy_threshold=0.3,
                fluency_threshold=0.3)