# %%
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
          EndDTStamp=round(datetime.datetime.today().timestamp())

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
               'needExtendedHoursData':'false'
               }

     if Symbol=='':
          Symbol='AMD'

     #print( 'Symbol=',Symbol,'APIURL=', APIURL)
     #https://developer.tdameritrade.com/quotes/apis/get/marketdata/%7Bsymbol%7D/quotes
     #https://api.tdameritrade.com/v1/marketdata/GOOG/pricehistory?apikey=K4OAZ0RGJBLI4VEBPOXZFUNFACKWPNNF&periodType=month&period=1&frequencyType=daily&frequency=1&endDate=1652244122000&startDate=1620708122000&needExtendedHoursDat=false
     # gets GMT time 2021-05-10 22:00:00  from 
     # <candles>
     # <open>2291.86</open>
     # <high>2322.0</high>
     # <low>2283.0</low>
     # <close>2308.76</close>
     # <volume>1605548</volume>
     # <datetime>1620709200000</datetime>
     # </candles>
    
    
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

def TDA_Price_Hist_a ( APIK='',  APIURL='', Symbol='', yPeriodType='month', yPeriod ='1',
                     yFrequencyType='daily',yFrequency='1' , StartDTStamp=0, EndDTStamp=0 , yExtHour='false'): 
# epoch time in ms, typically requires *1000 

     if StartDTStamp==0:
          StartDTStamp=1577865600  #2020/1/1


     if EndDTStamp==0:
          EndDTStamp=round(datetime.datetime.today().timestamp())

     StartDTStamp =StartDTStamp*1000
     EndDTStamp =EndDTStamp*1000
     
     if APIK=='' : 
          APIK='K4OAZ0RGJBLI4VEBPOXZFUNFACKWPNNF'
        #  yAPIk='K4OAZ0RGJBLI4VEBPOXZFUNFACKWPNNF'
     
     PlayLoad={'apikey': APIK,
               'periodType':yPeriodType,
               'period':1, #  yPeriod,
               "frequencyType":yFrequencyType,
               'frequency':yFrequency,
     #          'endDate':EndDTStamp,
     #          'startDate':StartDTStamp,
               'needExtendedHoursData':yExtHour
               }

     if Symbol=='':
          Symbol='AMD'

     #print( 'Symbol=',Symbol,'APIURL=', APIURL)
     #https://developer.tdameritrade.com/quotes/apis/get/marketdata/%7Bsymbol%7D/quotes
     #https://api.tdameritrade.com/v1/marketdata/GOOG/pricehistory?apikey=K4OAZ0RGJBLI4VEBPOXZFUNFACKWPNNF&periodType=month&period=1&frequencyType=daily&frequency=1&endDate=1652244122000&startDate=1620708122000&needExtendedHoursDat=false
     # gets GMT time 2021-05-10 22:00:00  from 
     # <candles>
     # <open>2291.86</open>
     # <high>2322.0</high>
     # <low>2283.0</low>
     # <close>2308.76</close>
     # <volume>1605548</volume>
     # <datetime>1620709200000</datetime>
     # </candles>
    
    
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

def TDA_Get_Instr_Funda ( APIK='',  APIURL='', Symbol=''): 
#https://developer.tdameritrade.com/instruments/apis/get/instruments

     try: 
     
          if APIK=='' : 
               APIK='K4OAZ0RGJBLI4VEBPOXZFUNFACKWPNNF'
          #  yAPIk='K4OAZ0RGJBLI4VEBPOXZFUNFACKWPNNF'
          
          PlayLoad={'apikey': APIK,
                    'symbol':Symbol, 
                    'projection':'fundamental'
                    }

          if Symbol=='':
               Symbol='AMD'


     
          if APIURL=='':
               APIURL="https://api.tdameritrade.com/v1/instruments"


          #print( 'Symbol=',Symbol,'APIURL=', APIURL, 'pl=', PlayLoad)
          content=requests.get(url=APIURL,params=PlayLoad)
          hist_data=content.json()
          
          hist_df=pd.json_normalize(hist_data)

          lgd("TDA_Symbol_Fund ")
     except:
          lge("failed")
     return hist_df

# %% 
# testing module codes 
################################################
def Test1():
    #yDF1= TDA_Price_Hist_a ( Symbol='QQQ', yPeriodType='day', yPeriod ='1', yFrequencyType='minute',yFrequency='15' , \
     #StartDTStamp=a_utils.epoch_from_today( Yr=0, Mo=0, Day=5), EndDTStamp= a_utils.epoch_from_today( Yr=0, Mo=0, Day=0) , yExtHour='false') 
    #print (f" \
    # date time is {yDF1['datetime'].to_numpy()[0]} ={ a_utils.TDAepoch2DT(yDF1['datetime'].to_numpy()[0])}, \
    #{yDF1['datetime'].to_numpy()[-2]} =  { a_utils.TDAepoch2DT(yDF1['datetime'].to_numpy()[-2])}, \
    # {yDF1['datetime'].to_numpy()[-1]} =  { a_utils.TDAepoch2DT(yDF1['datetime'].to_numpy()[-1])} \
    # ")
     ySec="XLV"
     yDF1=TDA_Get_Instr_Funda (Symbol=ySec)
     print (yDF1 ) 
     yColNm=f"{ySec}.description"
     ySecNM=yDF1[yColNm].to_numpy()[-1]
     print ( f"name = {ySecNM}")
   


# %%
if __name__ == '__main__':
     yDF1= Test1()


# %%
