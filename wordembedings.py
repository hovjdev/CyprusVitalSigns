#!/usr/bin/python -tt
import json
import logging
import nltk
import re
import cleantext
import random

from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from gensim.models import fasttext
from gensim.models import KeyedVectors
from gensim.models import word2vec
from gensim.models import FastText
from gensim.utils import tokenize
from gensim.models import ldamodel
from gensim.models import Word2Vec
from gensim import corpora
from gensim.parsing.preprocessing import preprocess_string, strip_punctuation, strip_numeric


from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer

import pyLDAvis
import pyLDAvis.gensim_models as gensimvis
from wordcloud import WordCloud



DATA_FILES = []

MODEL_FILE = "../models/cc.en.300.bin"

nltk.download('stopwords')
nltk.download('wordnet')


STOP_WORDS = nltk.corpus.stopwords.words()



logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def clean_sentence(val):
    "remove chars that are not letters or numbers, downcase, then remove stop words"
    val = cleantext.clean(val, extra_spaces=True, lowercase=True, numbers=True, punct=True)
    regex = re.compile('([^\s\w]|_)+')
    sentence = regex.sub('', val).lower()
    sentence = sentence.split(" ")
    for word in list(sentence):
        if word in STOP_WORDS:
            sentence.remove(word)
    sentence = " ".join(sentence)
    return sentence


corpus = []
wholetext = ''
# Opening JSON file
for datafile in DATA_FILES:
    f = open(datafile)
    data = json.load(f)
    f.close()

    for i in data:
        s=i['content']
        s=clean_sentence(s)
        word_list = s.split(" ")
        corpus.append(word_list)
        wholetext += " " + " ".join(word_list)


print(f'len(corpus)={len(corpus)}')
if False:
    import yake
    kw_extractor = yake.KeywordExtractor()
    language = "en"
    max_ngram_size = 1
    deduplication_threshold = 0.9
    numOfKeywords = 2000
    custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, top=numOfKeywords, features=None)
    keywords = custom_kw_extractor.extract_keywords(wholetext)
    keywords_list = []
    for k in keywords:
        keywords_list.append(k[0])
    print(f"keywords_list: {keywords_list[:100]}")


print(corpus[:10])


print("Get topics")
def get_lemma(word):
    lemma = wn.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma

def get_lemma2(word):
    return WordNetLemmatizer().lemmatize(word)

def prepare_text_for_lda(text):
    tokens = tokenize(text)
    tokens = [token for token in tokens if len(token) > 4]
    tokens = [token for token in tokens if token not in STOP_WORDS]
    tokens = [get_lemma(token) for token in tokens]
    return tokens

text_data = []
for c in corpus:
    line = " ".join(c)
    tokens = prepare_text_for_lda(line)
    text_data.append(tokens)

dictionary = corpora.Dictionary(text_data)
corpus2 = [dictionary.doc2bow(text) for text in text_data]

NUM_TOPICS = 30
ldamodel = ldamodel.LdaModel(corpus2, num_topics = NUM_TOPICS, id2word=dictionary, passes=20)
topics = ldamodel.print_topics(num_words=5)
for topic in topics:
    print(topic)


lda_display = gensimvis.prepare(ldamodel, corpus2, dictionary, sort_topics=False)
pyLDAvis.save_html(lda_display, 'lda.html')


for t in range(ldamodel.num_topics):
    plt.figure()
    wc = WordCloud(width=1600, height=1600)
    wc.font_path = "imput/fonts/bauhaus/BauhausRegular.ttf"
    plt.imshow(wc.fit_words(dict(ldamodel.show_topic(t, 100))))
    plt.axis("off")
    plt.savefig(f'wordcloud_{t+1}.png', facecolor='k', bbox_inches='tight', dpi=600)

plt.close('all')

print("Build model")
model=None
if True:
    #model = FastText(vector_size=50) #ok
    model = Word2Vec(vector_size=10) # ok
    model.build_vocab(corpus_iterable=corpus)
    print(f"len(corpus): {len(corpus)}")
    model.train(corpus_iterable=corpus, total_examples=len(corpus), epochs=100)


if False:
    model = FastText.load_fasttext_format(MODEL_FILE)
    model.build_vocab(corpus_iterable=corpus, update=True)
    model.train(corpus_iterable=corpus, total_examples=len(corpus), epochs=100)


print("Plot model")
def tsne_plot(model, positive):
    "Creates and TSNE model and plots it"
    labels = []
    tokens = []
    words = model.wv.most_similar(positive=positive, topn=20)
    for word in words:
        tokens.append(model.wv.__getitem__(word[0]))
        labels.append(word)
    tsne_model = TSNE(perplexity=40, n_components=2, init='pca', n_iter=2500, random_state=23)
    new_values = tsne_model.fit_transform(tokens)
    x = []
    y = []
    for value in new_values:
        x.append(value[0])
        y.append(value[1])
    plt.figure(figsize=(16, 16))
    for i in range(len(x)):
        plt.scatter(x[i],y[i])
        plt.annotate(labels[i],
            xy=(x[i], y[i]),
            xytext=(5, 2),
            textcoords='offset points',
            ha='right',
            va='bottom')
    plt.title(" ".join(positive))
    plt.show()

tsne_plot(model, positive=["cyprus"])
tsne_plot(model, positive=["aphrodite"])
tsne_plot(model, positive=["food"])
tsne_plot(model, positive=['tourism'])
