# -*- coding: utf-8 -*-
"""Amazon Fine Food Reviews.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13siVmP2dKGiXz_1CQF0dKA_iXy8P6AeA
"""

import requests
import re
import string
from textblob import TextBlob
import nltk
# nltk.download('all')
from nltk.corpus import stopwords
import spacy
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
import shutil
import os, sys
import numpy as np
import pandas as pd
import zipfile
# !pip install contractions
import contractions
from bs4 import BeautifulSoup
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, LSTM,Dropout
from tensorflow.keras.optimizers import SGD
import sqlite3
from tensorflow.keras.callbacks import EarlyStopping

# Source path: kaggle.json file in Google Drive
source_path = '/content/drive/MyDrive/kaggle token/kaggle.json'

# Destination path: Colab environment
destination_path = '/content/kaggle.json'

# Copy the file from Google Drive to Colab
shutil.copyfile(source_path, destination_path)

# List files in the current directory
print(os.listdir('/content'))

!mkdir -p ~/.kaggle
!mv kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

!kaggle datasets download -d snap/amazon-fine-food-reviews

with zipfile.ZipFile('/content/amazon-fine-food-reviews.zip', 'r') as zip_ref:
    zip_ref.extractall('/content')

connection = sqlite3.connect("/content/database.sqlite")

filtered_data = pd.read_sql_query("""select * from reviews""", connection)
filtered_data.shape

df=filtered_data.copy()
df

df.drop(['Id', 'ProductId', 'UserId', 'ProfileName', 'Time', 'Summary'], axis=1, inplace=True)

df.drop(df[df.HelpfulnessNumerator > df.HelpfulnessDenominator].index,axis=0,inplace=True)

df.reset_index(drop=True,inplace=True)

df.drop(['HelpfulnessNumerator', 'HelpfulnessDenominator'],inplace=True,axis=1)

df=df.reindex(columns=['Text', 'Score'])

df

df.drop(df[df.duplicated()].index,axis=0,inplace=True)

df.reset_index(drop=True,inplace=True)
df

df.drop(df[df['Score'] == 3].index,axis=0,inplace=True)

df.reset_index(drop=True,inplace=True)
df

df.Score.value_counts()

def mylabel(x):
    if x<3:
        return 0
    return 1

ActaulScore = df.Score
df.Score = df.Score.apply(lambda x: mylabel(x))
df['ActaulScore'] = ActaulScore

df.head()

df.Score.value_counts()

# 1. Lowercasing:
def lowercasing(text):

    return text.lower()

# 2. Remove HTML TAGS:
def remove_htlm_tags(text):
    p_text = BeautifulSoup(text, 'html.parser',).get_text()
    pattern_html = re.compile('<.*?>')
    return pattern_html.sub(r'', p_text)

# 3. Remove URLs
def remove_urls(text):

    pattern_url = re.compile(r'https?://\S+|www\.\S+')
    return pattern_url.sub(r'', text)

# 4. Remove Punctuation:
def remove_punctuation(text):

    exclude = string.punctuation
    return text.translate(str.maketrans('', '', exclude))

# 5. Chat Word Treatment:
chat_words = {
    "$" : " dollar ",
    "€" : " euro ",
    "4ao" : "for adults only",
    "a.m" : "before midday",
    "a3" : "anytime anywhere anyplace",
    "aamof" : "as a matter of fact",
    "acct" : "account",
    "adih" : "another day in hell",
    "afaic" : "as far as i am concerned",
    "afaict" : "as far as i can tell",
    "afaik" : "as far as i know",
    "afair" : "as far as i remember",
    "afk" : "away from keyboard",
    "app" : "application",
    "approx" : "approximately",
    "apps" : "applications",
    "asap" : "as soon as possible",
    "asl" : "age, sex, location",
    "atk" : "at the keyboard",
    "ave." : "avenue",
    "aymm" : "are you my mother",
    "ayor" : "at your own risk",
    "b&b" : "bed and breakfast",
    "b+b" : "bed and breakfast",
    "b.c" : "before christ",
    "b2b" : "business to business",
    "b2c" : "business to customer",
    "b4" : "before",
    "b4n" : "bye for now",
    "b@u" : "back at you",
    "bae" : "before anyone else",
    "bak" : "back at keyboard",
    "bbbg" : "bye bye be good",
    "bbc" : "british broadcasting corporation",
    "bbias" : "be back in a second",
    "bbl" : "be back later",
    "bbs" : "be back soon",
    "be4" : "before",
    "bfn" : "bye for now",
    "blvd" : "boulevard",
    "bout" : "about",
    "brb" : "be right back",
    "bros" : "brothers",
    "brt" : "be right there",
    "bsaaw" : "big smile and a wink",
    "btw" : "by the way",
    "bwl" : "bursting with laughter",
    "c/o" : "care of",
    "cet" : "central european time",
    "cf" : "compare",
    "cia" : "central intelligence agency",
    "csl" : "can not stop laughing",
    "cu" : "see you",
    "cul8r" : "see you later",
    "cv" : "curriculum vitae",
    "cwot" : "complete waste of time",
    "cya" : "see you",
    "cyt" : "see you tomorrow",
    "dae" : "does anyone else",
    "dbmib" : "do not bother me i am busy",
    "diy" : "do it yourself",
    "dm" : "direct message",
    "dwh" : "during work hours",
    "e123" : "easy as one two three",
    "eet" : "eastern european time",
    "eg" : "example",
    "embm" : "early morning business meeting",
    "encl" : "enclosed",
    "encl." : "enclosed",
    "etc" : "and so on",
    "faq" : "frequently asked questions",
    "fawc" : "for anyone who cares",
    "fb" : "facebook",
    "fc" : "fingers crossed",
    "fig" : "figure",
    "fimh" : "forever in my heart",
    "ft." : "feet",
    "ft" : "featuring",
    "ftl" : "for the loss",
    "ftw" : "for the win",
    "fwiw" : "for what it is worth",
    "fyi" : "for your information",
    "g9" : "genius",
    "gahoy" : "get a hold of yourself",
    "gal" : "get a life",
    "gcse" : "general certificate of secondary education",
    "gfn" : "gone for now",
    "gg" : "good game",
    "gl" : "good luck",
    "glhf" : "good luck have fun",
    "gmt" : "greenwich mean time",
    "gmta" : "great minds think alike",
    "gn" : "good night",
    "g.o.a.t" : "greatest of all time",
    "goat" : "greatest of all time",
    "goi" : "get over it",
    "gps" : "global positioning system",
    "gr8" : "great",
    "gratz" : "congratulations",
    "gyal" : "girl",
    "h&c" : "hot and cold",
    "hp" : "horsepower",
    "hr" : "hour",
    "hrh" : "his royal highness",
    "ht" : "height",
    "ibrb" : "i will be right back",
    "ic" : "i see",
    "icq" : "i seek you",
    "icymi" : "in case you missed it",
    "idc" : "i do not care",
    "idgadf" : "i do not give a damn fuck",
    "idgaf" : "i do not give a fuck",
    "idk" : "i do not know",
    "ie" : "that is",
    "i.e" : "that is",
    "ifyp" : "i feel your pain",
    "IG" : "instagram",
    "iirc" : "if i remember correctly",
    "ilu" : "i love you",
    "ily" : "i love you",
    "imho" : "in my humble opinion",
    "imo" : "in my opinion",
    "imu" : "i miss you",
    "iow" : "in other words",
    "irl" : "in real life",
    "j4f" : "just for fun",
    "jic" : "just in case",
    "jk" : "just kidding",
    "jsyk" : "just so you know",
    "l8r" : "later",
    "lb" : "pound",
    "lbs" : "pounds",
    "ldr" : "long distance relationship",
    "lmao" : "laugh my ass off",
    "lmfao" : "laugh my fucking ass off",
    "lol" : "laughing out loud",
    "ltd" : "limited",
    "ltns" : "long time no see",
    "m8" : "mate",
    "mf" : "motherfucker",
    "mfs" : "motherfuckers",
    "mfw" : "my face when",
    "mofo" : "motherfucker",
    "mph" : "miles per hour",
    "mr" : "mister",
    "mrw" : "my reaction when",
    "ms" : "miss",
    "mte" : "my thoughts exactly",
    "nagi" : "not a good idea",
    "nbc" : "national broadcasting company",
    "nbd" : "not big deal",
    "nfs" : "not for sale",
    "ngl" : "not going to lie",
    "nhs" : "national health service",
    "nrn" : "no reply necessary",
    "nsfl" : "not safe for life",
    "nsfw" : "not safe for work",
    "nth" : "nice to have",
    "nvr" : "never",
    "nyc" : "new york city",
    "oc" : "original content",
    "og" : "original",
    "ohp" : "overhead projector",
    "oic" : "oh i see",
    "omdb" : "over my dead body",
    "omg" : "oh my god",
    "omw" : "on my way",
    "p.a" : "per annum",
    "p.m" : "after midday",
    "pm" : "prime minister",
    "poc" : "people of color",
    "pov" : "point of view",
    "pp" : "pages",
    "ppl" : "people",
    "prw" : "parents are watching",
    "ps" : "postscript",
    "pt" : "point",
    "ptb" : "please text back",
    "pto" : "please turn over",
    "qpsa" : "what happens", #"que pasa",
    "ratchet" : "rude",
    "rbtl" : "read between the lines",
    "rlrt" : "real life retweet",
    "rofl" : "rolling on the floor laughing",
    "roflol" : "rolling on the floor laughing out loud",
    "rotflmao" : "rolling on the floor laughing my ass off",
    "rt" : "retweet",
    "ruok" : "are you ok",
    "sfw" : "safe for work",
    "sk8" : "skate",
    "smh" : "shake my head",
    "sq" : "square",
    "srsly" : "seriously",
    "ssdd" : "same stuff different day",
    "tbh" : "to be honest",
    "tbs" : "tablespooful",
    "tbsp" : "tablespooful",
    "tfw" : "that feeling when",
    "thks" : "thank you",
    "tho" : "though",
    "thx" : "thank you",
    "tia" : "thanks in advance",
    "til" : "today i learned",
    "tl;dr" : "too long i did not read",
    "tldr" : "too long i did not read",
    "tmb" : "tweet me back",
    "tntl" : "trying not to laugh",
    "ttyl" : "talk to you later",
    "u" : "you",
    "u2" : "you too",
    "u4e" : "yours for ever",
    "utc" : "coordinated universal time",
    "w/" : "with",
    "w/o" : "without",
    "w8" : "wait",
    "wassup" : "what is up",
    "wb" : "welcome back",
    "wtf" : "what the fuck",
    "wtg" : "way to go",
    "wtpa" : "where the party at",
    "wuf" : "where are you from",
    "wuzup" : "what is up",
    "wywh" : "wish you were here",
    "yd" : "yard",
    "ygtr" : "you got that right",
    "ynk" : "you never know",
    "zzz" : "sleeping bored and tired"
}

def remove_chat_words(text):

    new_text = []
    for w in text.split():
        if w.lower() in chat_words:
            new_text.append(chat_words[w.lower()])
        else:
            new_text.append(w)
    return " ".join(new_text)

# 6 Handling Emojis
def remove_emojis(text):

    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

# 7. Removing Stopwords
def remove_stopwords(text):

    new_text = []

    for word in text.split():
        if word in stopwords.words('english'):
            new_text.append('')
        else:
            new_text.append(word)
    x = new_text[:]
    new_text.clear()
    return  " ".join(x)

# 8. Spelling Correction:
def spell_check(text):

    my_list = []

    for word in text.split():
        textBlb = TextBlob(word)
        my_list.append(textBlb.correct().string)

    return " ".join(my_list)

# 9. Lemmatization
def Lemmatize_text(text):

    wordnet_lemmatizer = WordNetLemmatizer()

    lemm_text = " ".join([wordnet_lemmatizer.lemmatize(word) for word in text.split()])
    return lemm_text

# 10 Tokenization
def tokenize_text(text):

    return word_tokenize(text)

# 11. Contractions
def decontract_word(text):
    return contractions.fix(text)

df.Text[57046]

ActualText = df.Text

df.Text = df.Text.apply(lambda x: lowercasing(x))
df.Text = df.Text.apply(lambda x: remove_htlm_tags(x))
df.Text = df.Text.apply(lambda x: remove_urls(x))
df.Text = df.Text.apply(lambda x: remove_punctuation(x))
df.Text = df.Text.apply(lambda x: decontract_word(x))
df.Text = df.Text.apply(lambda x: remove_chat_words(x))
df.Text = df.Text.apply(lambda x: remove_emojis(x))

df.Text = df.Text.apply(lambda x: remove_stopwords(x))

df.to_csv('data_after_stopwords.csv', index=False)

df.Text[57046]

# Source path: kaggle.json file in Google Drive
source_path = '/content/drive/MyDrive/kaggle token/Amazon Fine Food Reviews/data_after_stopwords.csv'

# Destination path: Colab environment
destination_path = '/content/data_after_stopwords.csv'

# Copy the file from Google Drive to Colab
shutil.copyfile(source_path, destination_path)

# List files in the current directory
print(os.listdir('/content'))

df=pd.read_csv('/content/data_after_stopwords.csv')

df.Text[57046]

df.Text = df.Text.apply(lambda x: Lemmatize_text(x))

import gensim
from nltk import sent_tokenize
from gensim.utils import simple_preprocess

story = []
for doc in df['Text']:
    raw_sent = sent_tokenize(doc)
    for sent in raw_sent:
        story.append(simple_preprocess(sent))

len(story)

model = gensim.models.Word2Vec(
    window=10,
    min_count=2
)

model.build_vocab(story)

model.train(story, total_examples=model.corpus_count, epochs=model.epochs)

len(model.wv.index_to_key)

import pickle

with open("embedding.pkl", 'wb') as f:
    pickle.dump(model, f)

# Source path: kaggle.json file in Google Drive
destination_path = '/content/drive/MyDrive/kaggle token/Amazon Fine Food Reviews/embedding.pkl'

# Destination path: Colab environment
source_path = '/content/embedding.pkl'

# Copy the file from Google Drive to Colab
shutil.copyfile(source_path, destination_path)

model.wv.index_to_key

embedding_dim = model.vector_size
embedding_dim

vocab_size = len(model.wv.index_to_key)
vocab_size

word2vec_embeddings = model.wv.vectors
word2vec_embeddings

def document_vector(doc):
    # remove out-of-vocabulary words
    doc = [word for word in doc.split() if word in model.wv.index_to_key]
    # return np.mean(model.wv[doc], axis=0)
    if len(doc) == 0:
        return np.zeros(model.vector_size)
    else:
        return np.mean(model.wv[doc], axis=0)

from tqdm import tqdm

X = []
for doc in tqdm(df['Text'].values):
    X.append(document_vector(doc))

# Source path: kaggle.json file in Google Drive
source_path = '/content/drive/MyDrive/kaggle token/Amazon Fine Food Reviews/X_array.npy'

# Destination path: Colab environment
destination_path = '/content/X_array.npy'

# Copy the file from Google Drive to Colab
shutil.copyfile(source_path, destination_path)

# List files in the current directory
print(os.listdir('/content'))

# Load array from file
X = np.load('/content/X_array.npy')

X_array = np.array(X)

# np.save("X_array.npy", X_array)

# # Destination path: Colab environment
# destination_path = '/content/drive/MyDrive/kaggle token/Amazon Fine Food Reviews/X_array.npy'

# # Source path: kaggle.json file in Google Drive
# source_path = '/content/X_array.npy'

# # Copy the file from Google Drive to Colab
# shutil.copyfile(source_path, destination_path)

len(X_array)

y = df.Score

len(y)

y.value_counts(normalize=True)

from imblearn.over_sampling import SMOTE
smote = SMOTE(random_state=42)

X_resampled, y_resampled = smote.fit_resample(X_array, y)

X_resampled.shape

y_resampled.value_counts()

y_resampled.value_counts(normalize=True)

from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test = train_test_split(X_resampled, y_resampled, test_size=0.2,random_state=100)

print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)

y_train.value_counts()

y_test.value_counts()

X_train.shape

pd.DataFrame(X_train)

"""#**Deep learning Model**"""

# Define DNN model
DNN = Sequential([
    Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    Dropout(0.5),  # Optional dropout layer for regularization
    Dense(64, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')
])

# Compile model
DNN.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Define early stopping callback
early_stopping = EarlyStopping(monitor='val_loss', patience=3, verbose=1, restore_best_weights=True)

# Train model
DNN.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_test,y_test), callbacks=[early_stopping])

# Evaluate model
loss, accuracy = DNN.evaluate(X_test, y_test)
print(f'Test Loss: {loss}, Test Accuracy: {accuracy}')

with open("DNN.pkl", 'wb') as f:
    pickle.dump(DNN, f)

# Destination path: Colab environment
destination_path = '/content/drive/MyDrive/kaggle token/Amazon Fine Food Reviews/DNN.pkl'

# Source path: kaggle.json file in Google Drive
source_path = '/content/DNN.pkl'

# Copy the file from Google Drive to Colab
shutil.copyfile(source_path, destination_path)

mytxt = """
Its seriously a waste of money. I have tried all most all variants of Yummiez Chicken sausages, but found their combinations are very bad. Taste, Smell and even its quality of chicken is not good. " A Sausage manufacturer who don't know what is sausage". Picture on the packet is yummy, But not the product inside.
Don't buy and get disappoint with this product.
"""

mytxt = lowercasing(mytxt)
mytxt = remove_chat_words(mytxt)
mytxt = remove_htlm_tags(mytxt)
mytxt = remove_urls(mytxt)
mytxt = remove_punctuation(mytxt)
mytxt = decontract_word(mytxt)
mytxt = remove_emojis(mytxt)
mytxt = remove_stopwords(mytxt)
mytxt = Lemmatize_text(mytxt)

mytxt

mytxt1 = document_vector(mytxt)

mytxt1 = mytxt1.reshape(1, -1)

mytxt1.shape

predictions = DNN.predict(mytxt1)

binary_predictions = (predictions > 0.5).astype(int)
if binary_predictions ==1:
    print("Positive Sentiment")
else:
    print("Negative Sentiment")