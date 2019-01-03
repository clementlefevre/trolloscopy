
# coding: utf-8

# # LiveFyre Comments API

# Once we retrieve the ID of the FT Articles, we can call the LiveFyre API

# In[1]:


import logging
from os import listdir
from os.path import isfile, join
import requests
import time
import datetime
import json
import pandas as pd
import pickle
import sqlite3
from pandas.io.json import json_normalize

logging.basicConfig(filename='livefyre_API.log',level=logging.DEBUG,format='%(asctime)s:%(levelname)s:%(message)s' )


# ## Load FT IDs

# In[2]:


FT_ID_FILES_FOLDER = 'FT_ID'
onlyfiles = [f for f in listdir(FT_ID_FILES_FOLDER) if isfile(join(FT_ID_FILES_FOLDER, f))]


# In[3]:


def read_all_FT_IDS():
    df_FT_IDS = pd.DataFrame()

    for f in onlyfiles:
        df = pd.read_csv(FT_ID_FILES_FOLDER+"/"+f, index_col=0)
        df_FT_IDS = pd.concat([df_FT_IDS,df],axis=0)
    df_FT_IDS.columns=['topic','ft_id']
    df_FT_IDS = df_FT_IDS.drop_duplicates('ft_id')
    return df_FT_IDS


# In[4]:


def get_livefyre_URL(ft_id):
    comment_data =""
    url_FT_to_Livefyre = 'https://session-user-data.webservices.ft.com/v1/livefyre/get_lf_bootstrap?uuid='
    try:
        response_livefyreID = (requests.get(url_FT_to_Livefyre+str(ft_id),timeout=5)).content
        liverfyre_comments_url =   (json.loads(response_livefyreID))['url'].replace('bootstrap.html','init').replace('https','http')
  
        
    except Exception as e:
        logging.error(e)
    
    return (liverfyre_comments_url)
    


# In[5]:


def get_livefyre_metadata(livefyre_url):
    response_content = ''
    comment_data ={}
    try:
        response_livefyre_Metadata = (requests.get(livefyre_url,timeout=5))
        #print( print(response_livefyre_Metadata.status_code))
        response_content = json.loads(response_livefyre_Metadata.content)


    except Exception as e:
        logging.error(e)

    comment_data['ft_id']=response_content['collectionSettings']['url']
    comment_data['title']= response_content['collectionSettings']['title']
    comment_data['livefyreID'] = livefyre_url.split('/')[-2]
    comment_data['archives_data']= response_content['collectionSettings']['archiveInfo']

    return (comment_data)
    


# In[6]:


def get_livefyre_data_json(livefyre_metadata):
    comments = []
    BASE_LIVEFYRE_URL = 'http://bootstrap.ft.fyre.co/bs3'
    number_json_url = livefyre_metadata['archives_data']['nPages']
    
    for i in range(0,number_json_url):
        
    
        try:
            livefyre_url_json = BASE_LIVEFYRE_URL+livefyre_metadata['archives_data']['pageInfo'][str(i)]['url']
            # the structure of the json given by PageInfo is nested. Very bad for pandas, we change :
            livefyre_url_json = livefyre_url_json.replace('bootstrap.ft.fyre.co/bs3/ft.fyre.co/','data.livefyre.com/bs3/v3.1/ft.fyre.co/')
            logging.info(livefyre_url_json)                                           
            response_livefyreID = requests.get(livefyre_url_json,timeout=5)
            logging.info(str(response_livefyreID.status_code))
            response_content = response_livefyreID.json()
            comments.append(response_content)

        except Exception as e:
            logging.error(e)
    
   
    return (comments)
    


# ## Parse LiveFyre Response

# ### Authors

# In[7]:


def get_authors(data):
    df_all_authors=pd.DataFrame()
    for d in data :
        df = pd.DataFrame(d['authors']).T
        df = df[['displayName']].reset_index()
        df.columns = ['author_id','displayName']
        df_all_authors = pd.concat([df_all_authors,df],axis=0)
    df_all_authors = df_all_authors.drop_duplicates('author_id')
    return df


# ## Content

# In[8]:


def get_comments_and_likes(data):
    df_all_comments=pd.DataFrame()
    for d in data :
    
        df_comments = pd.DataFrame(d['content']).content.apply(pd.Series)
        #df_comments = df_comments[~df_comments.authorId.isnull()]
        df_liked_by = df_comments.annotations.apply(pd.Series)
        df_comments_and_liked_by = pd.concat([df_comments, df_liked_by],axis=1, sort=True)
        #df_comments_and_liked_by = df_comments_and_liked_by.drop(['annotations','generator'], 1)
        df_all_comments = pd.concat([df_all_comments,df_comments_and_liked_by],axis=0, sort=True)
   
        
    df_all_comments = df_all_comments.drop_duplicates('id')
    
    return df_all_comments


# ## Retrieve all livefyre comments using the FT articles IDs

# In[ ]:


def get_ALL_COMMENTS():
    
    df_FT_IDS = read_all_FT_IDS()
    ALL_FT_IDS= df_FT_IDS['ft_id'].sort_values().tolist()
    print(ALL_FT_IDS[:10])
    df_all_authors = pd.DataFrame()
    df_all_comments = pd.DataFrame()
    for i,ft_id in enumerate(ALL_FT_IDS[:11]):
        #if i>=16500:

            try:
                livefyre_url = get_livefyre_URL(ft_id)
                livefyre_metadata = get_livefyre_metadata(livefyre_url)
                livefyre_data = get_livefyre_data_json(livefyre_metadata)
                df_authors = get_authors(livefyre_data)
                df_comments = get_comments_and_likes(livefyre_data)
                df_comments['ft_id']= ft_id
                df_comments['ft_title'] = livefyre_metadata['title']
                

                df_all_authors = pd.concat([df_all_authors,df_authors],axis=0,sort=True)
                df_all_comments = pd.concat([df_all_comments,df_comments],axis=0,sort=True)

            except Exception as e:
                logging.error('error at i= %s for ft_url =  %s', str(i), str(ft_id))
                logging.error(e)


            if i%500==0:


                df_all_authors.to_csv('df_authors_'+str(i)+'.csv', encoding='utf-8',sep=';')
                df_all_comments.to_csv('df_comments_'+str(i)+'.csv', encoding='utf-8',sep=';')
                logging.info("Checkpoint at : {0:10.2f}% - i={1} of {2}".format(i*100.0/len(ALL_FT_IDS),i,len(ALL_FT_IDS)))
            
    df_all_authors.to_csv('df_authors_'+str(i)+'.csv', encoding='utf-8',sep=';')
    df_all_comments.to_csv('df_comments_'+str(i)+'.csv', encoding='utf-8',sep=';')


# In[ ]:


#get_ALL_COMMENTS()

