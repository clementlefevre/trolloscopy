
# coding: utf-8


import requests
import time
import datetime
import json
import pandas as pd
from dateutil.relativedelta import relativedelta

from  config import FT_API_KEY, TOPICS, FT_ID_RAW_FILES_FOLDER

# Third trial with FT comments section scraping
# - retrieve the article ID of the ft via http://api.ft.com/content/search/v1 (with headers X-Api-Key:k_E_Y)
# - retrieve corresponding livefyre comments ID via https://session-user-data.webservices.ft.com/v1/livefyre/get_lf_bootstrap?uuid=ARTICLE_ID
# - retrieve comments via https://bootstrap.ft.fyre.co/bs3/ft.fyre.co/378157/LIVEFYRE_ID/init


## THE FT HEADLINE API DOES NOT ALLOW MUCH combined topics search, thus split them :



def get_topics_search_string(key):

    TOPICS_string = ' OR '.join(TOPICS[key])
    return TOPICS_string


def get_dates_range(start_date_string, end_date_string = datetime.datetime.today().strftime("%Y-%m-%d")):
    
    dates= pd.date_range(start_date_string,'2019-01-01' , freq='1M')-pd.offsets.MonthBegin(1)
    return dates



def get_date_range_search_string(start_date):
    start_date = start_date
    start_date_string = "lastPublishDateTime:>{0}T00:00:00Z".format(start_date.strftime("%Y-%m-%d"))
    end_date = start_date + relativedelta(months=+1,days=+1)
    end_date_string = "lastPublishDateTime:<{0}T00:00:00Z".format(end_date.strftime("%Y-%m-%d"))
    string_date_range = " AND "+ start_date_string + " AND " +end_date_string
    return string_date_range




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



def get_monthly_result(start_date, topics_string):
    results = []
    date_range_month = get_date_range_search_string(start_date)
    
    query_string = topics_string + date_range_month
    print(date_range_month)
    result_0, number_results= get_FT_ID(query_string,offset=0)
    results +=result_0
    
    for i in range(100,number_results,100):
        
        result,_ = get_FT_ID(query_string,offset=i)
        results +=result
    return results



def get_ft_articles_ids_from_date(start_date_string):

    df_all_ft_id = pd.DataFrame()
    dates = get_dates_range(start_date_string)
    
    for topic in TOPICS:
        print('topic : {0}'.format(topic))
        
        all_months_results = []
        
        for date_month in dates: 
            all_months_results += get_monthly_result(date_month,topic )

        df = pd.DataFrame(all_months_results)
        print(df.info())
        df_all_ft_id = pd.concat([df,df_all_ft_id],axis=0)
     
    df_all_ft_id.columns = ['search_query','ft_id']
    df_all_ft_id = df_all_ft_id.drop_duplicates('ft_id')    
    df_all_ft_id.to_csv(FT_ID_RAW_FILES_FOLDER+ '/'+'FT_ID_all.csv')
    
    
# %% test
get_ft_articles_ids_from_date('2018-12-01')

