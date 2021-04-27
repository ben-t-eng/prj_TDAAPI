############MM
## imports
##############
import sys
sys.path.append ('..\TDAAPI')
import a_TDA_IF 
import a_utils
import talib
import pandas as pd
import numpy as np
import datetime
import a_Stock_IF
import logging
from logging import debug as lgd
from logging import info as lgi
from logging import error as lge

###################################
class Stock:
#######################
# it is required to populate self.HistDF with DataFrame
# with column name  'symbol' 'open', 'high', 'low', 'close', 'volume', 'date' ( in epoch timestamp minisecond)
# later processes can add more columns , such as TAs 

    def __init__(self, Symbol, Company=''):
    

        self.CompanyNm = Company
        self.Status= 0
        self.Symbol= Symbol
        self.Sector=''
        self.Industry=''

        self.StockBeta=1

        self.SMADays=10
        self.SMAAlert=0
        self.SMAState=0 # above or below
        self.SMA=0
        self.SMADate=None  #datetime obj
        self.SMA_D={'Period': 10, 'Alert':1, 'State':0, 'Value':0, 'Date':None}
        
        self.MACD={'Slow_Window':26, 'Fast_Window':12, 'Signal':9}
        self.RSI={'High':70 , 'Low':40 }
        self.BB={'Window':20}  #Bollinger Bands

        self.Broker=''
        self.Shares=0
        
        self.HistDF=None   #dataframe

        self.HistStartDate=0 # Epoc second
        self.Price=0
        self.Volume=0
        self.HistEndDate=0 # Epoc second
        self.PriceDate=None  # datetime obj

        self.Comment='' # for collecting all changes, warnings

        tPlt_Path=r'C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\historical_data\a_Debug'
        self.TA1={ 'plt_path':tPlt_Path, 
                    'Strategies': {
                                'SMA':{ 'plt_loc':[]  ,'SMAPeriod':10   },
                                'RSI': { 'plt_loc':[]  ,'SMAPeriod':10   }, 
                                'MACD':{ 'plt_loc':[]  ,'SMAPeriod':10   }, 
                                'BB':  { 'plt_loc':[]  ,'SMAPeriod':10   }   
                                }
                }
        self.CSV_Path=r'C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\historical_data\a_Debug'
        

        lgi('Stock initialized')

    def GetHist(self, Test=0):
    # get market data
        lgd("get symbol market data, ok")

     
        ySDate=a_utils.epoch_from_today( Yr=1, Mo=0, Day=0) 

        ###################self.HistDF=a_TDA_IF.TDA_Price_Hist (Symbol=self.Symbol, StartDTStamp=self.HistStartDate, EndDTStamp=self.HistEndDate )
        #
        if Test==1 :
            yDF2=pd.read_csv(r'C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\historical_data\a_Debug\GOOG_TDA_raw.csv')
        else:
            yDF2=a_TDA_IF.TDA_Price_Hist ( Symbol=self.Symbol, StartDTStamp=ySDate, EndDTStamp=0 )
        
        yDF2['Date']= pd.to_datetime(yDF2['datetime'], unit='ms') 
        yDF2.set_index(keys='Date', inplace=True)
        self.HistDF=yDF2
        #no need and not safe, self.HistDF= yDF2.iloc[:, 1:] #takes out the firstcolumn of serial numbers, 

        ##############################################
        # Date (DT index)  symbol     open       high       low    close      SMA1  \

        ##############################################

        lgd( "got quote update, " + str(type(self.HistDF)) + str(self.HistDF.shape)) 

        #print (yDF2) 

        self.UpdateTA()

        self.SaveHist()

    def UpdateTA(self):
        lgd('UpdateTA()')
        
        SMAPeriod=self.SMADays
        if SMAPeriod > 100 or SMAPeriod < 1 :
            SMAPeriod =10 
            lgi("SMADays is out of range of 1 to 100, reset to 10; ") 

        #https://www.geeksforgeeks.org/adding-new-column-to-existing-dataframe-in-pandas/
        ySMA=talib.SMA(self.HistDF['close'].values, timeperiod=SMAPeriod)

        # df1["SMA"]=ySMA ##works   
        self.HistDF.insert(5,"SMA1",  ySMA, True) #works too 
        
        # other new value for OLI fields
        # find the lastest data

        self.Price=self.HistDF['close'][-1]
        self.Volume=self.HistDF['volume'][-1]
        a=int(self.HistDF['datetime'][-1])
        self.PriceDate=a_utils.TDAepoch2DT(a)
        self.SMADate=self.PriceDate

        #lgi(" ppp updated price=" + str(self.Price) +' volume=' +str(self.Volume) + 
        #    ' date=' + str(self.PriceDate) + ' SMA=' + str(self.SMA))
    
        self.SMA=self.HistDF['SMA1'][-1]  # column 5 is sma 
        if  round(self.SMAState)==1 and float(self.SMA) >= float(self.Price):
            self.SMAAlert = -1
            self.SMAState =0  
            
            lgi( "SMA Alert: price dropped below SMA")

        elif round(self.SMAState)==0 and float(self.SMA) < float(self.Price):
            self.SMAAlert = 1
            self.SMAState =1 
            
            lgi("SMA Alert: price rose above SMA"+'; ')
        else:
            self.SMAAlert = 0
            self.Comment=self.Comment + "SMA Alert reset since no change since last update" +'; ' 
            
            lgi("updated price=" + str(self.Price) +' volume=' +str(self.Volume) + 
                'SMAdate=' + str(self.SMADate) + ' SMA=' + str(self.SMA) )

    def SaveHist(self):
        #lgi('SaveHist()')

        cdir=self.Symbol
        pdir=r'C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\historical_data\a_Debug'
        path= a_utils.addDir(pdir, cdir)

        path=a_utils.DF2CSV(self.HistDF, path, self.Symbol, '')

        lgi("SaveHist() path:  " + str(path) )

    def GetHist_TDA(self):

        ySDate=a_utils.epoch_from_today( Yr=1, Mo=0, Day=0) 
        df=a_TDA_IF.TDA_Price_Hist ( Symbol=self.Symbol, StartDTStamp=ySDate, EndDTStamp=0 )

        return df