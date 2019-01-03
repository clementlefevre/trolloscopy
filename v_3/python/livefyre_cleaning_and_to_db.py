
# coding: utf-8

# In[1]:


import pandas as pd
import re
from pandas.io.json import json_normalize
from sqlalchemy import create_engine
import sqlite3

ENGINE = 'sqlite:///db/livefyre.db'


# the database consiste in tables :

# - likes
# - authors
# - titles
# - comments metadata
# - comments text

def create_likes_df(df_raw):
    df_raw_no_na= df_raw[~df_raw.likedBy.isnull()][['id','likedBy']]
    df_raw_no_na.likedBy =  df_raw_no_na.likedBy.apply(lambda x: x[1:-1].split(','))
    df_likes = pd.DataFrame({'comment_id':df_raw_no_na.id.repeat(df_raw_no_na.likedBy.str.len()),'likedBy':df_raw_no_na.likedBy.sum()})
    df_likes.likedBy = df_likes.likedBy.str.replace('\'','')
    df_likes.likedBy = df_likes.likedBy.str.replace(' ','')
    df_likes.comment_id = df_likes.comment_id.astype(int)
    return df_likes
    

def create_title_df(df_raw):
    df_raw = df_raw[['ft_id', 'title']]
    df_raw= df_raw[~df_raw.title.isnull()]
    df_raw = df_raw.drop_duplicates('ft_id')
    return df_raw

cleanr =re.compile('<.*?>')

def cleanhtml(raw_html):
    if isinstance(raw_html, float):
        raw_html = str(raw_html)
    cleantext = re.sub(cleanr,'', raw_html)
    return cleantext

def create_comments_df(df_raw):
    df_raw = df_raw[['ancestorId', 'authorId', 'bodyHtml', 'createdAt', 'ft_id', 'id',
        'parentId']]
    df_raw[['ancestorId','id','parentId']] =df_raw[['ancestorId','id','parentId']].fillna(-1).astype(int)
    df_raw= df_raw[~df_raw.authorId.isnull()]
    
    return df_raw


def create_text_df(df_raw):
    df_raw = df_raw[['id','bodyHtml']]
   
    df_raw= df_raw[~df_raw.bodyHtml.isnull()]
    
    df_raw['bodyHtml'] = df_raw['bodyHtml'].apply(cleanhtml)
    return df_raw
    


# Store data to database

# ## Store Authors id and Authors Name

def store_authors_to_db(df_authors_raw_filepath):
    disk_engine = create_engine(ENGINE)
    chunksize = 2000
    reader = pd.read_csv(df_authors_raw_filepath,sep=';',encoding='utf-8', chunksize=chunksize)
    
    for chunk in reader:
        
        try:
            existing_authors_id = pd.read_sql_query('SELECT author_id FROM authors',disk_engine)
            df_to_store = chunk[~chunk.author_id.isin(existing_authors_id.author_id)]
            df_to_store[['author_id','displayName']].to_sql('authors', disk_engine, if_exists='append')
        except :
            chunk[['author_id','displayName']].to_sql('authors', disk_engine, if_exists='append')


    disk_engine.dispose()

# ## Store titles in database
            
def store_titles_to_db(df_comments_filepath):
    disk_engine = create_engine(ENGINE)
    chunksize = 20000
    reader = pd.read_csv(df_comments_filepath,sep=';',encoding='utf-8', chunksize=chunksize)
    
    for chunk in reader:
        df = create_title_df(chunk)
        
        try:
            
            existing_titles_id = pd.read_sql_query('SELECT ft_id FROM titles',disk_engine)
            df_to_store = df[~df.id.isin(existing_titles_id.ft_id)]
            df_to_store.to_sql('titles', disk_engine, if_exists='append')
        except :
            df.to_sql('titles', disk_engine, if_exists='append')
            
    disk_engine.dispose()
# ## Store titles in database
            
def store_comment_text_to_db(df_comments_filepath):
    disk_engine = create_engine(ENGINE)
    chunksize = 2000
    reader = pd.read_csv(df_comments_filepath,sep=';',encoding='utf-8', chunksize=chunksize)
    
    for chunk in reader:
        df = create_text_df(chunk)
        
        try:
            
            existing_text_id = pd.read_sql_query('SELECT id FROM text',disk_engine)
            df_to_store = df[~df.id.isin(existing_text_id.id)]
            df_to_store.to_sql('text', disk_engine, if_exists='append')
        except :
            df.to_sql('text', disk_engine, if_exists='append')
    disk_engine.dispose()
# ## Store Comments in database
            
def store_comments_to_db(df_comments_filepath):
    disk_engine = create_engine(ENGINE)
    chunksize = 20000
    
    cols_to_store = ['ancestorId', 'authorId','createdAt', 'ft_id','id','parentId']
    reader = pd.read_csv(df_comments_filepath,sep=';',encoding='utf-8', chunksize=chunksize)
    
    for chunk in reader:
        df = create_comments_df(chunk)
        
        try:
            
            existing_comments_id = pd.read_sql_query('SELECT id FROM comments',disk_engine)
            df_to_store = df[~df.id.isin(existing_comments_id.id)]
            df_to_store[cols_to_store].to_sql('comments', disk_engine, if_exists='append')
        except :
            df[cols_to_store].to_sql('comments', disk_engine, if_exists='append')
    disk_engine.dispose()
# ## Store Likes in database
            
def store_likes_to_db(df_comments_filepath):
    disk_engine = create_engine(ENGINE)
    chunksize = 20000
    reader = pd.read_csv(df_comments_filepath,sep=';',encoding='utf-8', chunksize=chunksize)
    
    for chunk in reader:
        df = create_likes_df(chunk)
        
        try:
            
            existing_likes = pd.read_sql_query('SELECT *  FROM likes',disk_engine)
            existing_likes['comment_liked'] =existing_likes.comment_id.map(str) + existing_likes.likedBy.map(str)
            df['comment_liked'] =df.comment_id.map(str) + df.likedBy.map(str)
            df_to_store = df[~df.comment_liked.isin(existing_likes.comment_liked)]
            df_to_store[['comment_id','likedBy']].to_sql('likes', disk_engine, if_exists='append')
        except :
            df[['comment_id','likedBy']].to_sql('likes', disk_engine, if_exists='append')
    
    disk_engine.dispose()


#%%
# drop a table

# import the sqlite3 module

def drop_table(table_name):
     
    connection  = sqlite3.connect(ENGINE.replace('sqlite:///',''))
    cursor      = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())
    
    dropTableStatement = "DROP TABLE \"{0}\"".format(table_name)
    print(dropTableStatement)
    cursor.execute(dropTableStatement)
    cursor.execute("vacuum")
    connection.close()    
    
#%%
# test authors :
   
#store_authors_to_db('livefyre_raw/df_authors_all.csv')
df_authors_db = pd.read_sql_query('SELECT * FROM authors',create_engine(ENGINE))
df_authors_db.author_id.value_counts().sort_values(ascending=False)
print(df_authors_db.shape)


#%%
# Test likes
#drop_table('likes')
#store_likes_to_db('livefyre_raw/df_comments_all_with_title.csv')

df_likes_db = pd.read_sql_query('SELECT * FROM likes',create_engine(ENGINE))

print(df_authors_db.shape)

#%% test comment metadata
#drop_table('comments')
#store_comments_to_db('livefyre_raw/df_comments_all_with_title.csv')
df_comments_db = pd.read_sql_query('SELECT * FROM comments',create_engine(ENGINE))
print(df_comments_db.shape)

#%% test comments text
store_comment_text_to_db('livefyre_raw/df_comments_all_with_title.csv')
df_comments_text_db = pd.read_sql_query('SELECT * FROM text',create_engine(ENGINE))
print(df_comments_text_db.shape)

#%% 
# Test titles
store_titles_to_db('livefyre_raw/df_comments_all_with_title.csv')
df_title_db = pd.read_sql_query('SELECT * FROM titles',create_engine(ENGINE))
print(df_title_db.shape)


#%% merge
df_merged = pd.merge(df_comments_db,df_title_db.drop_duplicates('ft_id'),on='ft_id',how='left')
df_merged[df_merged.title.isnull()]
