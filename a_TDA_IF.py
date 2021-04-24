### working this on 4/18 as class and functions 
import requests
import numpy as np
import pandas as pd 
import a_utils
import datetime 
from logging import debug as lgd
from logging import info as lgi
from logging import error as lge


class StockInfoBroker: 
     def __init__(self, broker_nm):
        self.brokernm = broker_nm
        self.usernm = None
        self.userpwd = None
        self.apiURL=None
        self.accesskey=None



def TDA_Price_Hist ( APIK='', PlayLoad='', APIURL='', Symbol='', StartDTStamp=0, EndDTStamp=0 ): 
# epoch time in ms, typically requires *1000 

     if StartDTStamp==0:
          StartDTStamp=1577865600  #2020/1/1


     if EndDTStamp==0:
          EndDTStamp=datetime.datetime.today().timestamp()

     StartDTStamp =StartDTStamp*1000
     EndDTStamp =EndDTStamp*1000
     
     if APIK=='' : 
          APIK='K4OAZ0RGJBLI4VEBPOXZFUNFACKWPNNF'
        #  yAPIk='K4OAZ0RGJBLI4VEBPOXZFUNFACKWPNNF'
     if PlayLoad=='' : 
          PlayLoad={'apikey': APIK,
               'periodType':'month',
               'period':'1',
               "frequencyType":'daily',
               'frequency':'1',
               'endDate':EndDTStamp,
               'startDate':StartDTStamp,
               'needExtendedHoursDat':'false'
               }

     if Symbol=='':
          Symbol='AMD'

     #print( 'Symbol=',Symbol,'APIURL=', APIURL)
     if APIURL=='':
          APIURL="https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format(Symbol)


     #print( 'Symbol=',Symbol,'APIURL=', APIURL, 'pl=', PlayLoad)
     content=requests.get(url=APIURL,params=PlayLoad)
     hist_data=content.json()
     
     hist_df=pd.json_normalize(hist_data, record_path= ['candles'], meta=["symbol", 'empty'])

     #shuffle dataframe a bit
     df_cols=hist_df.columns.tolist() 
     df_cols=df_cols[-2:-1]+df_cols[:-2]  # omitting "empty column"

     hist_df=hist_df[df_cols]
     lgd("TDA_Price_Hist ")
     return hist_df

