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

from sqlalchemy import null
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
import a_Stock_IF


# %%
# "C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\Automating Stock Investing Technical Analysis With Python _ by Farhad Malik _ FinTechExplained _ Medium_btc.pdf"
# for TA in python https://technical-analysis-library-in-python.readthedocs.io/en/latest/


class TA1:
    def __init__(self, container):
        
        self.container=container #a_stock_if.py class stock 
        self.symbol= container.Symbol

        ### expects pd dataframe in Stock format:symbol' 'open', 'high', 'low', 'close', 'volume', 'date' 
        self.TAs = container.HistDF      
        self.prices=None #expects pd dataseries (DS) of prices with datetimeindexed  
    

    def createPriceDS(self): 
        try:
            #w self.TAs['Date']= pd.to_datetime(self.TAs['datetime'], unit='ms')  # datetime is timestamp /Epoch, Date is py datetime obj   
            #w self.prices= pd.Series(DF2['close'].values , index=DF2['Date']) #price is PD series, with datetimeindex obj 
            #w self.TAs.set_index(keys='Date', inplace=True) # must be after the self.price is set 
          
            #self.TAs['Date']= pd.to_datetime(self.TAs['datetime'], unit='ms')  # datetime is timestamp /Epoch, Date is py datetime obj  
            #self.TAs.set_index(keys='Date', inplace=True) # must be after the self.price is set 

            #
            # self.prices= pd.Series(self.TAs['close'].values, index=self.TAs['Date'].values) #w without pd.Series(DF2['close'].values  , index=DF2['Date'] ) #price is PD series, with datetimeindex obj 
            self.prices=self.TAs['close']  # self.prices is a DF not Data series

            #print('TAS=', self.TAs)
            #print( 'Prices=', self.prices)
            lgd("Created price DS= "+ str(self.prices.shape))
        except:
            lge('unable to create price data series form HistDF')
            lgd('unable to create price data series form HistDF')
            #print('unable to create datetime index')
        

    # you don;t need the "y" if this function is declared outside of the Company class
    # this is an instance method, requires "self" as the first arugment in a instance method
    def generate_buy_sell_signals(self, condition_buy, condition_sell, dataframe, strategy):
        last_signal = None  # text for indicators
        indicators = []  # list -> np array -> pd df 
        buy = [] # list -> np array -> pd df 
        sell = [] # list -> np array -> pd df 

        
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

        self.get_CompressedBS()

        self.get_ChgPert()

    # updating the histDF in stock obj
    def get_ChgPert(self):
        try:
            yDF=self.TAs
            lgd(f"yDF= {yDF.shape}  ")

            yNPA1=yDF['close'].to_numpy()
            yNPA2=np.insert(yNPA1,0, 0)
            yNPA3=np.delete(yNPA2, yNPA2.size-1   )
            yNPA4=(yNPA1-yNPA3)/yNPA1
            yDF['PriceChg']=yNPA4

            yNPA5=np.delete(yNPA4,0) # first row value artifial
            #yNPA6=(np.amax(yNPA5)-np.amin(yNPA5))/2
           
            # price change mean is assumed to be at 0%
            yDF['PChgAlm']=np.std(yNPA5)*2
            
            lgd(f"price std= {np.std(yNPA5)}  ")



            yNPA1=yDF['volume'].to_numpy()
            #shift one row donw by adding  at index 0 and delete at index yNPA2.size-1
            yNPA2=np.insert(yNPA1,0, 0)
            yNPA3=np.delete(yNPA2, yNPA2.size-1   )
            yNPA4=(yNPA1-yNPA3)/yNPA1
            yDF['VolChg']=yNPA4
            yNPA5=np.delete(yNPA4,0) # first row value artifial
            yDF['VChgAlm']=np.std(yNPA5)*2

            yDF['VolSTD']=np.std(yNPA1)
            yDF['VolMean']=np.mean(yNPA1)
            yDF['VLvlAlmH']=np.mean(yNPA1)+2*np.std(yNPA1)
            yDF['VLvlAlmL']=np.mean(yNPA1)-2*np.std(yNPA1)
            lgd(f"vol std= {np.std(yNPA1)}  ")

        except:
            lge("failed")    
                     





    def get_sma(self):
        close_prices = self.prices
    
        DF2=self.TAs

        lgd("get_sma():df2 shape :"+ str(DF2.shape))
        
        SMAPeriod=self.container.TA1['Strategies']['SMA']["Params"]["Period"]
        #print(" ------------self.container SMMADays= ", SMAPeriod )
        ySMA=talib.SMA(close_prices, timeperiod=SMAPeriod)
        DF2['SMA']=ySMA     #add new column to DF, which already has SMA1 from a_stock_IF, 
        #print (ySMA)
        lgd("get_sma():df2 shape"+ str( DF2.shape))
        lgd("get_sma():df2 type"+ str(type(DF2)))
        
        self.generate_buy_sell_signals(lambda x, DF2: DF2['SMA'].values[x] < DF2['close'].iloc[x] , 
                                          lambda x, DF2: DF2['SMA'].values[x] > DF2['close'].iloc[x], DF2, 'SMA')
        
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

    def get_CompressedBS(self):
            close_prices = self.prices
        
            DF2=self.TAs  #just use DF2 as alias of teh TAs Dataframe object

            lgd("df2 shape :"+ str(DF2.shape))
            
            #NW self.cal_CompressedBSC()  #replaced by   def load_CmprsdBS(self) in a_Stock_IF()
            #NW self.load_CmprsdBS(self.TAs) 

            lgd("df2 shape"+ str( DF2.shape))
            lgd("df2 type"+ str(type(DF2)))
            
            ###self.generate_buy_sell_signals(lambda x, DF2: DF2['CmprsdB'].values[x] < DF2['close'].iloc[x] , 
            ###                               lambda x, DF2: DF2['CmprsdS'].values[x] > DF2['close'].iloc[x], DF2, 'CmprsdBS')
            ##self.generate_buy_sell_signals(lambda x, DF2: DF2['CmprsdB'].values[x] > DF2['close'].values[x] , 
            ##                             lambda x, DF2: DF2['CmprsdS'].values[x] < DF2['close'].values[x], DF2, 'CmprsdBS')

            self.calCmprsdBSSignal("CmprsdBS", "Buy", DF2 ,lambda i, DF2: DF2['close'].values[i] > DF2['CmprsdB'].values[i] )    
            self.calCmprsdBSSignal("CmprsdBS", "Sell",DF2 ,lambda i, DF2: DF2['close'].values[i] < DF2['CmprsdS'].values[i] )
            #a must to be able to use plot_price_and_signals(self, fig, yTA1, yDF, strategy,axs)
            DF2['CmprsdBS_Last_Signal'] = "N/A"

            lgd("after gen_buy_sell_signal"+ str(self.TAs.shape))
            return DF2         

    #replaced by def load_CmprsdBS(self) in a_Stock_IF()
    def cal_CompressedBSC(self):
            #for testing, get the average from the DS or DF price 
            
            df1=self.TAs['close']
            print( "ds1 type is ",df1.dtypes, '', df1.info()  )


            self.TAs['CmprsdB']= df1.min() *1.08
            self.TAs['CmprsdS']= df1.max() *0.92
            self.TAs['Cost']=df1.min() *1.18

    def calCmprsdBSSignal(self, sFieldNm,  yAction, yDF1, yLmdFunc):

       
        
        last_signal = "Ready"  # text for indicators
        indicators = []  # list -> np array -> pd df 
        action = [] # list -> np array -> pd df 
        value1=[]
        value2=[]
        value3=[]

        

        yDF=self.TAs  #just use DF2 as alias of teh TAs Dataframe object
        yFilter=f" yDF[\"{sFieldNm}\"].notnull() "
        lgd(f"filer = {yFilter}")
        ### dataframe=yDF[ yDF["CmprsdB"].notnull()]   
        dataframe=yDF1
        lgd(f"DF shape = {dataframe.shape}")

        #assuming DF is sorted ascending by Datetime Index  
        for i in range(0, len(dataframe)):
            if  yLmdFunc(i, dataframe) and last_signal !="Triggered": 
                last_signal = "Triggered"
                indicators.append("Activated")
                action.append(dataframe['close'].iloc[i])
            elif   yLmdFunc(i, dataframe) and last_signal =="Triggered":
                    indicators.append("Activated")
                    action.append(np.nan)

            else:
                last_signal="Ready"
                indicators.append("Deactivated")
                action.append(np.nan)

            value1.append(dataframe['close'].iloc[i])
        #    value2.append(dataframe[yColumn].values[i])
               

        yDF[f'{sFieldNm}_Last_Signal'] = last_signal
        yDF[f'{sFieldNm}_{yAction}_Indicator'] = np.array(indicators)
        yDF[f'{sFieldNm}_{yAction}'] = np.array(action)
        yDF[f'{sFieldNm}__{yAction}_close'] = np.array(value1)
        #yDF[f'{sFieldNm}_{yAction}_values'] = np.array(value2)
        

# %%
# plotting 
# from "C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\Automating Stock Investing Technical Analysis With Python _ by Farhad Malik _ FinTechExplained _ Medium_btc.pdf"
# started wit matplotlib tutorial:
# https://matplotlib.org/stable/tutorials/index.html


import os
from matplotlib import pyplot as plt
import matplotlib.patches as patches
import numpy as np
class TA1_Plt:
    def plot_price_and_signals(self, fig, yTA1, yDF, strategy,axs):
            
            last_signal_val = yDF[f'{strategy}_Last_Signal'].values[-1]
            lgd(f"last BS signal is {last_signal_val}")
            last_signal = 'Unknown' if not last_signal_val else last_signal_val
            lgd(f"last signal is {last_signal}")
        
            yParam=str(yTA1.container.TA1['Strategies'][strategy]['Params'])
            title = f' {strategy} {yParam} ; Last Signal: {last_signal}'
            fig.suptitle(f'Top: {yTA1.symbol} Stock Price. Bottom:{strategy}')

            yDFSS=not yDF[f'{strategy}_Buy'].isnull().all()
            yDFa=yDF[yDF[f'{strategy}_Buy'].notnull() ]
            if yDFSS:
                axs[0].scatter(yDF.index, yDF[f'{strategy}_Buy'], color='green', label='Buy Signal', marker='^', alpha=1)
                for i in range(0, len(yDFa)):
                    yDTa=yDFa.index.array[i].strftime("%m%d")
                    axs[0].text(yDFa.index.array[i], yDFa[f'{strategy}_Buy'].values[i],  s=f"{yDTa}", rotation=45, color='green')
            ##if not yDF[f'{strategy}_Sell'].isnull().all():
            ##    axs[0].scatter(yDF.index, yDF[f'{strategy}_Sell'], color='red', label='Sell Signal', marker='v', alpha=1)
                #axs[0].text(yDF.index, yDF[f'{strategy}_Sell'],  s=f" 123 ", color='green' , rotation=45)
            yDFSS=not yDF[f'{strategy}_Sell'].isnull().all()
            yDFa=yDF[yDF[f'{strategy}_Sell'].notnull() ]
            if yDFSS:
                axs[0].scatter(yDF.index, yDF[f'{strategy}_Sell'], color='red', label='Sell Signal', marker='v', alpha=1)
                for i in range(0, len(yDFa)):
                    yDTa=yDFa.index.array[i].strftime("%m%d")
                    axs[0].text(yDFa.index.array[i], yDFa[f'{strategy}_Sell'].values[i],  s=f"{yDTa}", rotation=45, color='red')
          

            axs[0].plot(yDF.index, yTA1.prices, label='Close Price',color='blue', alpha=0.35)

            # 20220603 have to be after the plot, so to have the x,y axes setup 
            self.drawEvents(axs, yDF)
            
            #nw if not yDF[f'EventLink'].isnull().all():
            #nw     axs[0].axvline(x=yDF.index, color='green', label='Event', linestyle='--', alpha=1)
          
            plt.xticks(rotation=45)
            axs[0].set_title(title)
            #axs[0].set_xlabel(f'Top: {yTA1.symbol} Stock Price. Bottom:{strategy}', fontsize=12)
            axs[0].set_ylabel('Close Price', fontsize=12)
            axs[0].legend(loc='upper left')
            axs[0].grid()

    def drawEvents(self, axs, yDF):
            yDF1= yDF[yDF[f'EventLink'].notnull()]

            lgd(f"DF1 = {yDF1.shape} " )
            for i in range(0, len(yDF1)):

                yDT=yDF1["EventDate"].values[i].strftime("%m%d")
                lgd(f" event date= {yDT} ")
                
                
                axs[0].axvline(x=yDF1["EventDate"].values[i], url= f"{i}",  color='brown', linestyle='--', alpha=1)
               
                lgd(f" step 1")
                #https://matplotlib.org/stable/tutorials/text/text_props.html#sphx-glr-tutorials-text-text-props-py
                yYlow,yYheight=axs[0].set_ylim(auto=True)
                yYlow,yYheight=axs[0].get_ybound()
                lgd(f" step 2")
                axs[0].text(x=yDF1["EventDate"].values[i], y=yYlow-10,  s=f"<{i+1}>{yDT}", color='brown',  verticalalignment='bottom', horizontalalignment='left' , rotation=45) # transform=axs[0].transAxes)            
                lgd(f" step 3")
               # axs[0].text(x=yDF1["EventDate"].values[i], y=yYlow,  s=f"<{i+1}>", color='green', rotation=45)




    def plot_macd(self, yTA1):
            image = f'images/{yTA1.symbol}_macd.png'
            macd =  yTA1.TAs
            # Create and plot the graph
            fig, axs = plt.subplots(2, sharex=True, figsize=(12,9))
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
            
            self.save_plot(yTA1,'MACD', plt)
            plt.close(fig)
            #plt.show()

    def plot_rsi(self, yTA1):
            image = f'images/{yTA1.symbol}_rsi.png'
            rsi = yTA1.TAs
            low_rsi = 40
            high_rsi = 70
        #plt.style.use('default')
            fig, axs = plt.subplots(2, sharex=True, figsize=(12, 9))
            self.plot_price_and_signals(fig, yTA1, rsi, 'RSI', axs)
            axs[1].fill_between(rsi.index, y1=low_rsi, y2=high_rsi, color='#adccff', alpha=0.3)
            axs[1].plot(rsi['RSI'], label='RSI', color='blue',alpha=0.35)
            axs[1].legend(loc='upper left')
            axs[1].grid()
           
            self.save_plot(yTA1,'RSI', plt)  
            plt.close(fig)
            #plt.show()

    def plot_bollinger_bands(self, yTA1):
            image = f'images/{yTA1.symbol}_bb.png'
            bollinger_bands = yTA1.TAs

            
            fig, axs = plt.subplots(2, sharex=True, figsize=(12, 9))

            self.plot_price_and_signals(fig, yTA1, bollinger_bands, 'Bollinger_Bands', axs)

            axs[1].plot(bollinger_bands['Bollinger_Bands_Middle'], label='Middle', color='blue', alpha=0.35)
            axs[1].plot(bollinger_bands['Bollinger_Bands_Upper'], label='Upper', color='green', alpha=0.35)
            axs[1].plot(bollinger_bands['Bollinger_Bands_Lower'], label='Lower', color='red', alpha=0.35)
            axs[1].fill_between(bollinger_bands.index, bollinger_bands['Bollinger_Bands_Lower'], bollinger_bands['Bollinger_Bands_Upper'], alpha=0.1)
            axs[1].legend(loc='upper left')

            axs[1].grid()
            
            #self.save_plot(yTA1,'BB', plt)  
            self.save_plot(yTA1,'Bollinger_Bands', plt) 

            plt.close(fig)
            #plt.show()
            
    def plot_sma(self, yTA1):
            
            sma = yTA1.TAs
            # Create and plot the graph
            fig, axs = plt.subplots(2, sharex=True, figsize=(12,9))
            self.plot_price_and_signals(fig, yTA1, sma, 'SMA', axs)
            axs[1].plot(sma['SMA'],  label=yTA1.symbol+' SMA', color= 'green')
            axs[1].plot(sma['close'], label='Signal Line',color='orange')
            
    
            axs[1].legend(loc='upper left')
            axs[1].grid()
           
                 
            # save image before the show
            self.save_plot(yTA1, 'SMA', plt )


            # don't show
            plt.close(fig)
            # plt.show()

    def plot_CmprsdBS(self, yTA1):
            
            
            # Create and plot the graph
            fig, axs = plt.subplots(2, sharex=True, figsize=(12,9))
            yBSH=yTA1.TAs
            self.plot_price_and_signals(fig, yTA1, yBSH, 'CmprsdBS', axs)


            axs[1].plot(yTA1.TAs['CmprsdB'],  label=' ComprsdB', color= 'green', linestyle='--', alpha=1)
            axs[1].plot(yTA1.TAs['CmprsdS'],  label=' ComprsdS', color= 'red', linestyle='--', alpha=1)
            axs[1].plot(yTA1.TAs['Cost'],  label=' Cost', color= 'black')
            axs[1].plot(yTA1.TAs['close'],  label=' price', color= 'blue', alpha=0.75)

            
           
            # 2nd y axis
            y2ndY=axs[1].twinx()
            y2ndY.plot(yTA1.TAs.index, yTA1.TAs['Shares'],  label=yTA1.symbol+' Shares', color= 'brown')
            y2ndY.set_ylabel("Shares", color="brown")

            axs[1].legend(loc='upper left')
            axs[1].grid()
                 
            # save image before the show
            self.save_plot(yTA1, 'CmprsdBS', plt )


            # don't show
            plt.close(fig)
            # plt.show()


    def save_plot(self, yTA1, strategy, plot):
            try:
                filenm = f'{yTA1.symbol}_{strategy}'    
                yPath= a_utils.addDir(yTA1.container.TA1['plt_path'], yTA1.symbol)
                yPath= a_utils.FilePath(Path=yPath, FileNm=filenm, TimeString='', Suffix='')
                plot.savefig(yPath)
                yPathSaved=yPath+'.png'
                lgd("plt saved at: " + str(yPathSaved) ) 
                ### dictionary  yTA1.container.TA1 from a_stock_IF---------- 
                # save to TA1 dictionary so that it can be recalled to put on OLI
                yTA1.container.TA1['Strategies'][strategy]['plt_loc'].append(yPathSaved)
                lgd("plt added to dictionary: " + str(yPathSaved) ) 
            except:
                lge('plt not saved to ' + str(yPathSaved))

    def plt_all(self, yTA5):
        ##### turn off interactive mode 
        
        
        self.plot_macd(yTA5)
        self.plot_rsi(yTA5)
        self.plot_bollinger_bands(yTA5)
        self.plot_sma(yTA5) 
        self.plot_CmprsdBS(yTA5)

#%%
#############################################################
#def testrun():
import a_Stock_IF
import pandas as pd
import numpy as np

def test1(): 
    #yYahooDS=  yf.Ticker(yGoog.symbol).history(period='1y')['Close']
    ###############################################################
    DF2=pd.read_csv(r".\HistoricalData\Debug\GOOG_2022_02_20-21_03.csv")



    yStock=a_Stock_IF.Stock('CompanyA')
    yStock.HistDF= DF2
    yTA=TA1(yStock)  
    yTA.createPriceDS()  # needed to populate the price DS first 
    
    yTA.set_TAs()

    print ("_________________________________")
    print('ta.prices=', yTA.prices)
  
    print ("_________________________________")
    print(' TA string=' , str(yTA.TAs))
 
    print ("_________________________________")
    print (' yTA =',yTA.TAs)

    print ( id(yTA.TAs), " ids ", id(yTA.prices), " ", id(yTA.TAs["close"]))

 

    ## yPlt=TA1_Plt()

    ## yPlt.plt_all(yTA)



# %%
if __name__ == "__main__" :
    test1()


# %%
