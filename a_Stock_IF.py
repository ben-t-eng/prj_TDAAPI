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

        self.TA_Indicators=None 
        self.CSV_Path=r'C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\historical_data\a_Debug'
        self.Plt_Path=r'C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\historical_data\a_Debug'

      
        lgi('Stock() done')

    def GetHist(self):
    # get market data
        lgd("get symbol market data, ok")

        #print ('end date', yEDate)
        #print ('start Date', ySDate)

        ###################self.HistDF=a_TDA_IF.TDA_Price_Hist (Symbol=self.Symbol, StartDTStamp=self.HistStartDate, EndDTStamp=self.HistEndDate )
        yDF2=pd.read_csv(r'C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\historical_data\a_Debug\GOOG_TDA_raw.csv')
        self.HistDF= yDF2.iloc[:, 1:] #takes out the firstcolumn of serial numbers, 

        
        lgd( "got quote update, " + str(type(self.HistDF)) + str(self.HistDF.shape)) 

        self.UpdateTA()

        self.SaveHist()

    def UpdateTA(self):
        lgd('UpdateTA()')
        
        #

        SMAPeriod=self.SMADays
        if SMAPeriod > 100 or SMAPeriod < 1 :
            SMAPeriod =10 
            lgi("SMADays is out of range of 1 to 100, reset to 10; ") 

        #https://www.geeksforgeeks.org/adding-new-column-to-existing-dataframe-in-pandas/
        ySMA=talib.SMA(self.HistDF['close'].values, timeperiod=SMAPeriod)

        # df1["SMA"]=ySMA ##works   
        self.HistDF.insert(5,"SMA",  ySMA, True) #works too 
        
        # other new value for OLI fields
        # find the lastest data

        self.Price=self.HistDF.iloc[-1, 4]
        self.Volume=self.HistDF.iloc[-1,6]
        self.PriceDate= a_utils.TDAepoch2DT(self.HistDF.iloc[-1,7] )
        self.SMA= self.HistDF.iloc[-1,5] 


        lgi("updated price=" + str(self.Price) +' volume=' +str(self.Volume) + ' date=' + str(self.PriceDate) + ' SMA=' + str(self.SMA))

        self.SMA=self.HistDF.iloc[-1,5]  # column 5 is sma 
        if  self.SMAState==1 and self.SMA >= self.Price:
            self.SMAAlert = -1
            self.SMAState =0  
            
            lgi( "SMA Alert: price dropped below SMA")

        elif self.SMAState==0 and self.SMA < self.Price:
            self.SMAAlert = 1
            self.SMAState =1 
            
            lgi("SMA Alert: price rose above SMA"+'; ')
        else:
            self.SMAAlert = 0 
            self.Comment=self.Comment + "SMA Alert reset since no change since last update" +'; ' 
            self.SMADate=self.PriceDate
            lgi("updated price=" + str(self.Price) +' volume=' +str(self.Volume) + 'SMAdate=' + str(self.SMADate) + ' SMA=' + str(self.SMA) )

    def SaveHist(self):
        #lgi('SaveHist()')

        cdir=self.Symbol
        pdir=r'C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\historical_data\a_Debug'
        path= a_utils.addDir(pdir, cdir)

        path=a_utils.DF2CSV(self.HistDF, path, self.Symbol, '')

        lgi("SaveHist() path:  " + str(path) )



    