# To add a new cell, type '# %%'

# %%
##### for logging 
import logging
from logging import debug as lgd
from logging import info as lgi
from logging import error as lge
from logging import warning as lgw
from logging import critical as lgc
from io import StringIO
#############
import sys 
import datetime
import a_utils
import weakref
###############
from ta.momentum import RSIIndicator
from ta.trend import MACD
import numpy as np
import pandas as pd
from ta.volatility import BollingerBands
import talib

#############
import os
from matplotlib import pyplot as plt
import numpy as np

# %%
# logging for debugging 
#

#yfilter=a_utils.LevelFilter((logging.CRITICAL,logging.INFO, logging.WARNING, logging.DEBUG))
#yfilter=(a_utils.LevelFilter((logging.INFO, logging.CRITICAL, logging.DEBUG)), None) , a_utils.FileFilter())
yfilter=(a_utils.LevelFilter((logging.INFO, logging.CRITICAL, logging.DEBUG)) , a_utils.LevelFilter((logging.INFO, logging.CRITICAL, logging.DEBUG)))
yfilter2=(a_utils.LevelFilter((logging.INFO, logging.CRITICAL, logging.DEBUG)) , a_utils.FileFilter())

yfilter1=(a_utils.LevelFilter((logging.WARNING, logging.INFO, logging.DEBUG)),)  # have to have two items , even if the same
yfilter3=[a_utils.LevelFilter([logging.WARNING])]

#global lg

lg=a_utils.BTLogger( stdout_filter=yfilter3)


# %%
# "C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\Automating Stock Investing Technical Analysis With Python _ by Farhad Malik _ FinTechExplained _ Medium_btc.pdf"
# for TA in python https://technical-analysis-library-in-python.readthedocs.io/en/latest/


class TA1:
    def __init__(self, container):
        
        self.container=container
        self.symbol= container.Symbol

        ### expects pd dataframe in Stock format:symbol' 'open', 'high', 'low', 'close', 'volume', 'date' 
        self.TAs = container.HistDF      
        self.prices=None #expects pd ds of prices with datetimeindexed  
    

    def createPriceDS(self): 
        try:
            #w self.TAs['Date']= pd.to_datetime(self.TAs['datetime'], unit='ms')  # datetime is timestamp /Epoch, Date is py datetime obj   
            #w self.prices= pd.Series(DF2['close'].values , index=DF2['Date']) #price is PD series, with datetimeindex obj 
            #w self.TAs.set_index(keys='Date', inplace=True) # must be after the self.price is set 
          
            self.TAs['Date']= pd.to_datetime(self.TAs['datetime'], unit='ms')  # datetime is timestamp /Epoch, Date is py datetime obj  
            self.TAs.set_index(keys='Date', inplace=True) # must be after the self.price is set 

            self.prices= pd.Series(DF2['close']) #w without pd.Series(DF2['close'].values  , index=DF2['Date'] ) #price is PD series, with datetimeindex obj 
            
            #print('TAS=', self.TAs)
            #print( 'Prices=', self.prices)
            lgw("Created price DS= "+ str(self.prices.shape))
        except:
            lge('unable to create price data series form HistDF')
            lgd('unable to create price data series form HistDF')
            #print('unable to create datetime index')
        

    # you don;t need the "y" if this function is declared outside of the Company class
    # this is an instance method, requires "self" as the first arugment in a instance method
    def generate_buy_sell_signals(self, condition_buy, condition_sell, dataframe, strategy):
        last_signal = None  # np series -> np array -> pd df 
        indicators = []  # np series -> np array -> pd df 
        buy = [] # np series -> np array -> pd df 
        sell = [] # np series -> np array -> pd df 

        
        #print(" Buy sell signal() condition_buy type=", type(condition_sell))
        #print(" Buy sell signal() dataframe type=", type(dataframe))
        #print(" Buy sell signal() buy type=", type(buy))
        #print("genbuysellsignal():company.ti ?DF shape", dataframe.shape)

        for i in range(0, len(dataframe)):
            # if buy condition is true and last signal was not Buy
            if condition_buy(i, dataframe) and last_signal != 'Buy':
                last_signal = 'Buy'
                indicators.append(last_signal)
                buy.append(dataframe['close'].iloc[i])
                sell.append(np.nan)
            # if sell condition is true and last signal was Buy
            elif condition_sell(i, dataframe)  and last_signal == 'Buy':
                last_signal = 'Sell'
                indicators.append(last_signal)
                buy.append(np.nan)
                sell.append(dataframe['close'].iloc[i])
            else:
                indicators.append(last_signal)
                buy.append(np.nan)
                sell.append(np.nan)

        dataframe[f'{strategy}_Last_Signal'] = np.array(last_signal)
        dataframe[f'{strategy}_Indicator'] = np.array(indicators)
        dataframe[f'{strategy}_Buy'] = np.array(buy)
        dataframe[f'{strategy}_Sell'] = np.array(sell)
        # print("genbuysellsignal():company.ti shape", company.technical_indicators.shape)
        # print("genbuysellsignal():company.ti ?DF shape", dataframe.shape

    
    def set_TAs(self):
        # company.technical_indicators = pandas.DataFrame()
        # company.technical_indicators['Close'] = company.prices  # tech_indicator is now fully stacked with on column , with index

        #print ("new", company.technical_indicators)
        
        self.get_sma()
        #print ("After sma", yTA.TAs)

        #print ("before MACD",yGoog.technical_indicators)
        self.get_macd()
        #print ("After macd", yTA.TAs)
        
        #print ("before RSI",yGoog.technical_indicators)
        self.get_rsi()
        #print ("After rsi", yTA.TAs)

        #print ("After RSI", company.technical_indicators)
        self.get_bollinger_bands()
        #print ("After bb", yTA.TAs)

    def get_sma(self):
        close_prices = self.prices
    
        DF2=self.TAs

        lgd("get_sma():df2 shape :"+ str(DF2.shape))
        
        SMAPeriod=self.container.SMADays 
        #print(" ------------self.container SMMADays= ", SMAPeriod )
        ySMA=talib.SMA(close_prices, timeperiod=SMAPeriod)
        DF2['SMA']=ySMA     #add new column to 
        #print (ySMA)
        lgd("get_sma():df2 shape"+ str( DF2.shape))
        lgd("get_sma():df2 type"+ str(type(DF2)))
        
        self.generate_buy_sell_signals(lambda x, dataframe: DF2['SMA'].values[x] < DF2['close'].iloc[x] , 
                                          lambda x, dataframe: DF2['SMA'].values[x] > DF2['close'].iloc[x], DF2, 'SMA')
        
        #print("genbuysellsignal():company.ti shape after gen_signal", company.technical_indicators.shape)
        lgd("get_sma():company.ti shape, after gen_signal"+ str(self.TAs.shape))
        return DF2         

    def get_macd(self):
            close_prices = self.prices
            dataframe1 = self.TAs

            # to be changes later from company obj
            window_slow = 26
            signal = 9
            window_fast = 12

            macd = MACD(self.prices, window_slow, window_fast, signal)
            
            dataframe1['MACD'] = macd.macd()
            dataframe1['MACD_Histogram'] = macd.macd_diff()
            dataframe1['MACD_Signal'] = macd.macd_signal()

            #print("df len", len(dataframe1))
        
            self.generate_buy_sell_signals(lambda x, dataframe: dataframe['MACD'].values[x] < dataframe['MACD_Signal'].iloc[x] , 
                                            lambda x, dataframe: dataframe['MACD'].values[x] > dataframe['MACD_Signal'].iloc[x], 
                                            dataframe1, 'MACD')
                                            
            return dataframe1

    def get_rsi(self):
        close_prices = self.prices
        dataframe = self.TAs

        rsi_time_period = 20
        rsi_indicator = RSIIndicator(close_prices, rsi_time_period)
        
        dataframe['RSI'] = rsi_indicator.rsi()
        
        low_rsi = 40
        high_rsi = 70
        
        self.generate_buy_sell_signals(
            lambda x, dataframe: dataframe['RSI'].values[x] < low_rsi,
            lambda x, dataframe: dataframe['RSI'].values[x] > high_rsi, dataframe, 'RSI')
        return dataframe


    def get_bollinger_bands(self):
        close_prices = self.prices
        dataframe = self.TAs

        window = 20
        
        indicator_bb = BollingerBands(close=close_prices, window=window,window_dev=2)
        # Add Bollinger Bands features
        dataframe['Bollinger_Bands_Middle'] =indicator_bb.bollinger_mavg()
        dataframe['Bollinger_Bands_Upper'] =indicator_bb.bollinger_hband()
        dataframe['Bollinger_Bands_Lower'] =indicator_bb.bollinger_lband()
        
        self.generate_buy_sell_signals(
            lambda x, signal: signal['close'].values[x] < signal['Bollinger_Bands_Lower'].values[x], 
            lambda x, signal: signal['close'].values[x] >
            signal['Bollinger_Bands_Upper'].values[x],
            dataframe, 'Bollinger_Bands')
        return dataframe


# %%
# plotting 
# from "C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\Automating Stock Investing Technical Analysis With Python _ by Farhad Malik _ FinTechExplained _ Medium_btc.pdf"
# started wit matplotlib tutorial:
# https://matplotlib.org/stable/tutorials/index.html


import os
from matplotlib import pyplot as plt
import numpy as np
class TA1_Plt:
    def plot_price_and_signals(self, fig, yTA1, yDF, strategy,axs):
            last_signal_val = yDF[f'{strategy}_Last_Signal'].values[-1]
            last_signal = 'Unknown' if not last_signal_val else last_signal_val
        
            title = f'Close Price Buy/Sell Signals using {strategy}.Last Signal: {last_signal}'
            fig.suptitle(f'Top: {yTA1.symbol} Stock Price. Bottom:{strategy}')

            if not yDF[f'{strategy}_Buy'].isnull().all():
                axs[0].scatter(yDF.index, yDF[f'{strategy}_Buy'], color='green', label='Buy Signal', marker='^', alpha=1)

            if not yDF[f'{strategy}_Sell'].isnull().all():
                axs[0].scatter(yDF.index, yDF[f'{strategy}_Sell'], color='red', label='Sell Signal', marker='v', alpha=1)
                axs[0].plot(yTA1.prices, label='Close Price',color='blue', alpha=0.35)

            plt.xticks(rotation=45)
            axs[0].set_title(title)
            axs[0].set_xlabel('Date', fontsize=18)
            axs[0].set_ylabel('Close Price', fontsize=18)
            axs[0].legend(loc='upper left')
            axs[0].grid()

    def plot_macd(self, yTA1):
            image = f'images/{yTA1.symbol}_macd.png'
            macd =  yTA1.TAs
            # Create and plot the graph
            fig, axs = plt.subplots(2, sharex=True, figsize=(13,9))
            self.plot_price_and_signals(fig, yTA1, macd, 'MACD', axs)
            axs[1].plot(macd['MACD'], label=yTA1.symbol+' MACD', color= 'green')
            axs[1].plot(macd['MACD_Signal'], label='Signal Line',color='orange')
            positive = macd['MACD_Histogram'][(macd['MACD_Histogram'] >=0)]
            negative = macd['MACD_Histogram'][(macd['MACD_Histogram'] <0)]
            axs[1].bar(positive.index, positive, color='green')
            axs[1].bar(negative.index, negative, color='red')
            axs[1].legend(loc='upper left')
            axs[1].grid()
            #print(os.path.abspath(image))
            
            self.save_plot(yTA1,'macd', plt)
            plt.show()

    def plot_rsi(self, yTA1):
            image = f'images/{yTA1.symbol}_rsi.png'
            rsi = yTA1.TAs
            low_rsi = 40
            high_rsi = 70
        #plt.style.use('default')
            fig, axs = plt.subplots(2, sharex=True, figsize=(13, 9))
            self.plot_price_and_signals(fig, yTA1, rsi, 'RSI', axs)
            axs[1].fill_between(rsi.index, y1=low_rsi, y2=high_rsi, color='#adccff', alpha=0.3)
            axs[1].plot(rsi['RSI'], label='RSI', color='blue',alpha=0.35)
            axs[1].legend(loc='upper left')
            axs[1].grid()
           
            self.save_plot(yTA1,'rsi', plt)  
            plt.show()

    def plot_bollinger_bands(self, yTA1):
            image = f'images/{yTA1.symbol}_bb.png'
            bollinger_bands = yTA1.TAs

            
            fig, axs = plt.subplots(2, sharex=True, figsize=(13, 9))

            self.plot_price_and_signals(fig, yTA1, bollinger_bands, 'Bollinger_Bands', axs)

            axs[1].plot(bollinger_bands['Bollinger_Bands_Middle'], label='Middle', color='blue', alpha=0.35)
            axs[1].plot(bollinger_bands['Bollinger_Bands_Upper'], label='Upper', color='green', alpha=0.35)
            axs[1].plot(bollinger_bands['Bollinger_Bands_Lower'], label='Lower', color='red', alpha=0.35)
            axs[1].fill_between(bollinger_bands.index, bollinger_bands['Bollinger_Bands_Lower'], bollinger_bands['Bollinger_Bands_Upper'], alpha=0.1)
            axs[1].legend(loc='upper left')

            axs[1].grid()
            
            self.save_plot(yTA1,'BB', plt)  
            plt.show()
            
    def plot_sma(self, yTA1):
            
            sma = yTA1.TAs
            # Create and plot the graph
            fig, axs = plt.subplots(2, sharex=True, figsize=(13,9))
            self.plot_price_and_signals(fig, yTA, sma, 'SMA', axs)
            axs[1].plot(sma['SMA'],  label=yTA1.symbol+' SMA', color= 'green')
            axs[1].plot(sma['close'], label='Signal Line',color='orange')
            
    
            axs[1].legend(loc='upper left')
            axs[1].grid()
           
                 
            # save image before the show
            self.save_plot(yTA1, 'SMA', plt )
            plt.show()



    def save_plot(self, yTA1, strategy, plot):
            try:
                filenm = f'{yTA1.symbol}_{strategy}'    
                yPath= a_utils.addDir(yTA1.container.Plt_Path, yTA1.symbol)
                yPath= a_utils.FilePath(Path=yPath, FileNm=filenm, TimeString='', Suffix='')
                plot.savefig(yPath)
                lgi("plt saved at:" + str(yPath) ) 
            except:
                lge('plt not saved to' + str(yPath))

    def plt_all(self, yTA):
        self.plot_macd(yTA)
        self.plot_rsi(yTA)
        self.plot_bollinger_bands(yTA)
        self.plot_sma(yTA) 

#%%

import a_Stock_IF
import pandas as pd
import numpy as np


#%%

#yYahooDS=  yf.Ticker(yGoog.symbol).history(period='1y')['Close']
###############################################################
DF2=pd.read_csv(r'C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\historical_data\a_Debug\GOOG_TDA_raw.csv')


lgc("lgc")
lge("lge")
lgw("lgw")
lgi('lgi')
lgd('lgd')

yStock=a_Stock_IF.Stock('CompanyA')
yStock.HistDF= DF2

yTA=TA1(yStock)
yTA.createPriceDS()  # needed to populate the price DS first 
#print('ta.prices=', yTA.prices)
#print('TAs=', yTA.TAs)
#lgd(' yTA price ds =' + yTA.prices)
#lgd(' lgd: yTA TA ds =' + str(yTA.TAs))
#print(' yTA price ds =',yTA.prices)
#print (' yTA TA ds =',yTA.TAs)


yTA.set_TAs()

yPlt=TA1_Plt()

yPlt.plt_all(yTA)



# %%
