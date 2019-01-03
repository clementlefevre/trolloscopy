
# coding: utf-8


import requests
import time
import json
import pandas as pd
from dateutil.relativedelta import relativedelta

from config import FT_API_KEY

# Third trial with FT comments section scraping
# - retrieve the article ID of the ft via http://api.ft.com/content/search/v1 (with headers X-Api-Key:k_E_Y)
# - retrieve corresponding livefyre comments ID via https://session-user-data.webservices.ft.com/v1/livefyre/get_lf_bootstrap?uuid=ARTICLE_ID
# - retrieve comments via https://bootstrap.ft.fyre.co/bs3/ft.fyre.co/378157/LIVEFYRE_ID/init

# In[ ]:


FT_API_KEY = '59cbaf20e3e06d3565778e7b8833135b219f49c7b6e4965e5c22cae5'

## THE FT HEADLINE API DOES NOT ALLOW MUCH combined topics search, thus split them :
#TOPICS = ['Russia', 'Syria','Trump', 'Crimea', 'Ukraine','Oil']
#TOPICS = ['Afd', 'Assad', 'Brexit', 'Doping', 'Gazprom']
#TOPICS = [ 'Georgia', 'IOC', 'Le+Pen', 'Merkel']
TOPICS = ['MH17', 'NATO', 'Obama', 'Putin', 'Refugees']
TOPICS = ['Mueller', 'Flynn', 'Manafort', 'Cohen']


# In[ ]:


TOPICS_string = ' OR '.join(TOPICS)
TOPICS_string


# In[ ]:


dates= pd.date_range('2014-01-01','2019-01-01' , freq='1M')-pd.offsets.MonthBegin(1)
dates


# In[ ]:


def set_date_range(start_date):
    start_date = start_date
    start_date_string = "lastPublishDateTime:>{0}T00:00:00Z".format(start_date.strftime("%Y-%m-%d"))
    end_date = start_date + relativedelta(months=+1,days=+1)
    end_date_string = "lastPublishDateTime:<{0}T00:00:00Z".format(end_date.strftime("%Y-%m-%d"))
    string_date_range = " AND "+ start_date_string + " AND " +end_date_string
    return string_date_range


# In[ ]:


def get_FT_ID(query_string,offset=0):
    print('offset :',str(offset))
    FT_ID =[]
    number_results = 0
    url = 'http://api.ft.com/content/search/v1'
    headers = {'X-Api-Key': FT_API_KEY }
    body={"queryString": query_string,"queryContext" : {"curations" : ["ARTICLES"]}, "resultContext": {"offset": offset}}
    try:
        time.sleep(.5)
        response = requests.post(url,data=json.dumps(body),headers=headers, timeout=5)
        print(response.status_code)
        data = json.loads(response.content)
        #import ipdb;ipdb.set_trace()
        
        FT_ID = [(query_string,resp['id']) for resp in data['results'][0]['results']]
        number_results = data['results'][0]['indexCount']
        print ("number_results : ",str(number_results))
    except Exception as e:
        print(e)
        print('---'*20)
        print('ERROR')
        print (e)
        
    return FT_ID, number_results


# In[ ]:


def get_monthly_result(start_date):
    results = []
    date_range_month = set_date_range(start_date)
    
    query_string = TOPICS_string + date_range_month
    print(date_range_month)
    result_0, number_results= get_FT_ID(query_string,offset=0)
    results +=result_0
    
    for i in range(100,number_results,100):
        
        result,_ = get_FT_ID(query_string,offset=i)
        results +=result
    return results


# In[ ]:


all_months_results = []

for date_month in dates:
    all_months_results += get_monthly_result(date_month)


# In[ ]:


df = pd.DataFrame(all_months_results)
df.info()


# In[ ]:


df.to_csv('FT_ID_{0}.csv'.format('_'.join(TOPICS)))

