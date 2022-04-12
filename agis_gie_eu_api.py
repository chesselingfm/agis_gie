#%%

import pandas as pd
import datetime
import requests
import matplotlib.pyplot as plt
from google.oauth2 import service_account
from google.cloud import storage
import json
import requests
import numpy as np
from datawrapper import Datawrapper
import time
from datetime import datetime
import datetime

#%%
headers = {
    'x-key': 'MY_API_KEY',
}



#%% Determine how many pages for the query?
def anzahlderseiten2(date_from, date_to, size):
    date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d')
    date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d')
    lastpage = int(((date_to - date_from).days / size) +1)
    return lastpage


#%% Get Data from a single page (e.g. 30 days)
def einzelseite_abfragen(facility, country, company, date_from, date_to, page):
    url = 'https://agsi.gie.eu/api?facility={}&country={}&company={}&from={}&to={}&page={}&size=30'.format(facility, country, company, date_from, date_to, page)
    print (url)
    r = requests.get(url, headers=headers)
    data = r.json()
    df = pd.DataFrame.from_records(data['data'])
    return df

#%% This is the main function that gets the data from the API
def gie_api_abfragen(name, facility, country, company, date_from, date_to):
    # How many pages?
    lastpage = anzahlderseiten2(date_from, date_to, 30)    
    
    print ('Requesting', name , ' - consisting of ', str(lastpage) , ' page(s)')
    
     
    df_liste = []
    
    # Loop gets all pages
    for i in range(1, lastpage + 1):
        print("Seite:", i)
        
        # Single page
        df = einzelseite_abfragen(facility, country, company, date_from, date_to, i)
        print ('Length of response:',  len(df))
        df_liste.append(df)
        time.sleep(1)

    # List of DFs is concatenated
    dfs = pd.concat(df_liste) 
    
    del dfs['info']
    
    # Correcting dtypes
    dfs['gasInStorage'] = pd.to_numeric(dfs['gasInStorage'])
    dfs['full'] = pd.to_numeric(dfs['full'])
    
    dfs['gasDayStart'] = pd.to_datetime(dfs['gasDayStart'])
    dfs['month_day'] = dfs['gasDayStart'].dt.strftime('%m.%d.')
    dfs['year'] = dfs['gasDayStart'].dt.strftime('%Y')
    return dfs


#######################

#%% If I get the data for a county like Germany, this works:
df_germany = gie_api_abfragen('', '', 'DE', '', '2022-04-01', '2022-04-12')
df_germany

#%% But if I want the data for 1 SSO or a facility, the json response is almost empty:
df_astora = gie_api_abfragen('astora', '', 'DE', '21X000000001160J', '2022-04-01', '2022-04-12')
df_astora

#%% OR Rehden
df_rehden = gie_api_abfragen('astora', '21Z000000000271O', 'DE', '21X000000001160J', '2022-04-01', '2022-04-12')

# This is the URL https://agsi.gie.eu/api?facility=21Z000000000271O&country=DE&company=21X000000001160J&from=2022-04-04&to=2022-04-12&page=1&size=30

# and this is the respsone:
# {"last_page":0,"total":0,"dataset":"","gas_day":"2022-04-10","data":[]}