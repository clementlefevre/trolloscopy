
# coding: utf-8


import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD,PCA,RandomizedPCA
from nltk.stem.porter import PorterStemmer
from collections import Counter
import re

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer,TfidfTransformer
from sklearn.pipeline import Pipeline
import nltk

from datetime import date, timedelta,datetime
from stop_words import get_stop_words

from sqlalchemy import create_engine

from config import LIVEFYRE_DB

print(LIVEFYRE_DB)

ENGINE = ''.join(['sqlite:///',LIVEFYRE_DB])


# Load data from DB
def filter_on_year(df_comments_db,year):
    return df_comments_db[df_comments_db['year']==year]

def load_comments_data_from_db(year):
    
    df_comments_db = pd.read_sql_query('SELECT * FROM comments',create_engine(ENGINE))
    df_comments_db['datetimeCreated'] = pd.to_datetime(df_comments_db.createdAt, unit='s')
    df_comments_db['year']= df_comments_db.datetimeCreated.dt.year
    
    return filter_on_year(df_comments_db,year)






# Filter on top authors with number of comments per year higher than agiven value for computation sake.

def filter_on_top_n_authors(df_comments_db,top_n):
    
    
    df_top_authors = df_comments_db.groupby('authorId')[['index']].count()
    
    df_top_authors = df_top_authors[df_top_authors['index']>top_n]
    
    top_authors_id = df_top_authors.index
    return df_comments_db[df_comments_db.authorId.isin(top_authors_id)]


def add_text_comments(df):
     df_comments_text_db = pd.read_sql_query('SELECT * FROM text',create_engine(ENGINE))
     df = pd.merge(df,df_comments_text_db,on='id',how='left')
     return df[['authorId','bodyHtml']]

def preprocessor(text):
    text = str(text)
    text = re.sub('<[^>]*>', '', text)
    emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)', text)
    text = re.sub('[\W]+', ' ', text.lower()) +        ' '.join(emoticons).replace('-', '')
    return text

def process_the_comments_text(df):
    df['preprocessed_content'] = df['bodyHtml'].apply(preprocessor)

    df_comments_agg = df.groupby(['authorId']).agg({'preprocessed_content':lambda x:x.str.cat()})
    df_comments_agg = df_comments_agg.reset_index()
    
    return df_comments_agg[['authorId','preprocessed_content']]




# ### Text preprocessing

# #### Remove html tags and others

# #### Create a Stemming tokenizer with Porter's algo.

porter = PorterStemmer()


def tokenizer_porter(text):
    return [porter.stem(word) for word in text.split()]


# #### Stopwords
nltk.download('stopwords')
from nltk.corpus import stopwords
stop = stopwords.words('english')

# #### Only preprocess text

# #### Prepare data
def prepare_data(year):
    
    df = load_comments_data_from_db(year)
    df = filter_on_top_n_authors(df,100)
    df = add_text_comments(df)
    df_processed = process_the_comments_text(df)
    
    return df_processed



def get_X_y_labels(df_comments):
    X = df_comments.preprocessed_content.values
    y = df_comments.index.values
    labels = df_comments.authorId.values
    return X,y,labels


# ### TFIDF



def get_vectorized_text(X,ngram_range=(1,1),max_features=None):
    pipeline = Pipeline([('vect', TfidfVectorizer(ngram_range=ngram_range,tokenizer=tokenizer_porter,stop_words=stop,max_features=max_features)),
                         ('tfidf', TfidfTransformer())]) 
    return pipeline.fit_transform(X).todense()


# #### Decomposition with PCA

def create_PCA_TFIDF(df_comments,year):
    X,y,labels = get_X_y_labels(df)
    X_vectorized = get_vectorized_text(X,ngram_range=(2,2))
    pca = PCA(n_components=2).fit(X_vectorized)
    
    print (pca.explained_variance_ratio_.sum())
    print (pca.explained_variance_ratio_*100)
    
    pca_1_2 = pca.transform(X_vectorized)
    df_pca = pd.DataFrame({'author_id':df.authorId.values,'PCA_1':pca_1_2[:,0],'PCA_2':pca_1_2[:,1],'year':year})
    return df_pca
    


#%%
for i in range(2014,2019):
    df = prepare_data(i)
    df_pca = create_PCA_TFIDF(df,i)
    df_pca.to_sql('pca', create_engine(ENGINE), if_exists='append')
    
#%% test
df = pd.read_sql_query('SELECT * FROM pca',create_engine(ENGINE))
    
