############MM
## imports
##############
# %%
from msilib.schema import Property
from pickle import FALSE, TRUE
from re import M
import sys

from sqlalchemy import column
sys.path.append ('..\TDAAPI')
import a_TDA_IF 
import a_utils
import talib
import pandas as pd
import numpy as np
import datetime
#import a_Stock_IF
#import a_OL_IF


from logging import debug    as lgd   #10
from logging import info     as lgi   #20
from logging import warning  as lgw   #30
from logging import error    as lge   #40
from logging import critical as lgc   #50 


import a_Settings

import win32com.client as win32 
from win32com.client import constants as C

###################################
class Stock:
#######################
# it is required to populate self.HistDF with DataFrame
# with column name  'symbol' 'open', 'high', 'low', 'close', 'volume', 'date' ( in epoch timestamp minisecond)
# later processes can add more columns , such as TAs 

    def __init__(self, Symbol, Company=''):
    

        self.CompanyNm = Company
        self.Status= 0
        self.Symbol= Symbol.upper() #.capitalize()
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

        #tPlt_Path=r'C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\historical_data\a_Debug'
        #tPlt_Path=r'C:\BTFiles\btgithub1b\TDAAPI\HistoricalData'
        # no use for ,'SMAPeriod':8   after 'plt_loc':[] ???
        self.TA1={ 'plt_path':a_Settings.URL_plt_path, 
                    'Strategies': {
                                'SMA':{ 'plt_loc':[]   ,'SMAPeriod':10   },
                                'RSI': { 'plt_loc':[]  ,'SMAPeriod':10   }, 
                                'MACD':{ 'plt_loc':[]  ,'SMAPeriod':10   }, 
                                'BB':  { 'plt_loc':[]  ,'SMAPeriod':10   },
                                'CmprsdBS':{ 'plt_loc':[],'SMAPeriod':10   },
                                'FinViz':{ 'plt_loc':[] }        
                                }
                }
        self.CSV_Path=a_Settings.URL_CVS_file
        

        lgi('Stock initialized')

    def GetHist(self, Test=0):
    # get market data
        #lgd("get symbol market data, ok")

        try: 
            ySDate=a_utils.epoch_from_today( Yr=1, Mo=0, Day=0) 

            ###################self.HistDF=a_TDA_IF.TDA_Price_Hist (Symbol=self.Symbol, StartDTStamp=self.HistStartDate, EndDTStamp=self.HistEndDate )
            #
            if Test==1 :
                ##yDF2=pd.read_csv(r"C:\BTFiles\btgithub1b\TDAAPI\HistoricalData\Debug\GOOG_2022_02_20-21_03.csv")
                yDF2=pd.read_csv(a_Settings.URL_debug_data_file)
                lgi("--> debug data file used <--" + a_Settings.URL_debug_data_file + "; instead of data from web e.g. TDA and etc." ) 
            else:
                yDF2=a_TDA_IF.TDA_Price_Hist ( Symbol=self.Symbol, StartDTStamp=ySDate, EndDTStamp=0 )
            

            #from TDA ms Timestamp to panda PST time +11 hours, purely for excel table 
            yTDA2PDBias= 28800000 #ms

            yDF2['Date']= pd.to_datetime(yDF2['datetime'] + yTDA2PDBias , unit='ms')
            yDF2.set_index(keys='Date', inplace=True)

            #https://www.statology.org/pandas-convert-column-to-int/#:~:text=You%20can%20use%20the%20following%20syntax%20to%20convert,Integer%20Suppose%20we%20have%20the%20following%20pandas%20DataFrame%3A
            yDF2['datetime'] = yDF2['datetime'].astype('int64')  # so you get complete resolution vs 1.649E+12

            self.HistDF=yDF2
            #no need and not safe, self.HistDF= yDF2.iloc[:, 1:] #takes out the firstcolumn of serial numbers, 

            ##############################################
            # Date (DT index)  symbol     open       high       low    close      SMA1  \

            ##############################################

            lgd( "got quote update, " + str(type(self.HistDF)) + str(self.HistDF.shape)) 

            #print (yDF2) 

            self.UpdateTA()

            self.SaveHist()

            return 1
        except:
            lge ("failed, check SEC symbol in captital or internet connection")
            return 0


    def UpdateTA(self):
        lgd('UpdateTA()')
        
        SMAPeriod=self.SMADays
        if SMAPeriod > 100 or SMAPeriod < 1 :
            SMAPeriod =10 
            lgi("SMADays is out of range of 1 to 100, reset to 10; ") 

        #https://www.geeksforgeeks.org/adding-new-column-to-existing-dataframe-in-pandas/
        ySMA=talib.SMA(self.HistDF['close'].values, timeperiod=SMAPeriod)

        # df1["SMA"]=ySMA ##works   
        # need to check if SMA1 already exists , if so can;t add column of same name 2022feb19
        for col in self.HistDF.columns:
            if col == "SMA1" :
                colnm ="SMA-" + datetime.datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
                self.HistDF.rename(columns={"SMA1": colnm }, inplace=True)

        #https://www.geeksforgeeks.org/adding-new-column-to-existing-dataframe-in-pandas/
        self.HistDF.insert(5,"SMA1",  ySMA ) #works too 
        
        #debugging 20220220
        #a_utils.DF2CSV(self.HistDF, r"C:\BTFiles\btgithub1b\TDAAPI\HistoricalData\Debug", self.Symbol, '')
        #lgd("debugging datafile same date issue ")

        # other new value for OLI fields
        # find the lastest data

        # get latest trade day price, volume and trade date / time
        self.Price=self.HistDF['close'][-1]
        self.Volume=self.HistDF['volume'][-1]
        # a=a_utils.TDAepoch2DT(int(self.HistDF['datetime'][-1]))

        a0=self.HistDF['datetime'][-1].astype('int64')
        a=a_utils.TDAepoch2DT(a0) 
        b=pd.to_datetime(a0, unit='ms')
        s1="--->SMADate=PriceDate=" + a.strftime("%Y_%m_%d-%H_%M") + "; PD=" + b.strftime("%Y_%m_%d-%H_%M") +"; a0="+ str(a0)
        lgc(s1 )
        
        self.PriceDate=a
        
        ## 4/7/22 self.PriceDate=self.HistDF['datetime'][-1]
        
        self.SMADate=self.PriceDate

        #lgi(" ppp updated price=" + str(self.Price) +' volume=' +str(self.Volume) + 
        #    ' date=' + str(self.PriceDate) + ' SMA=' + str(self.SMA))
        self.cal_SMA_Alert()

        self.load_CmprsdBS()


    # 
    def load_CmprsdBS(self):
        df1=self.HistDF['close']
            
        self.HistDF['CmprsdB']= df1.min()
        self.HistDF['CmprsdS']= df1.max()
        self.HistDF['Cost']=df1.min()

        lgd(f" set_comprsdX starts")
    
        ###self.get_OLICompsdBS(self.Symbol, self.HistDF)

        self.set_CmprsdData( "CmprsdS", self.Symbol)
        self.set_CmprsdData( "CmprsdB", self.Symbol)
        self.set_CmprsdData( "Cost", self.Symbol)

        lgd(" set_comprsdX done")

    # great for testing , not  for real usage 
    def get_OLICompsdBS(self, Sec, DF ):
        yOL = win32.dynamic.Dispatch("Outlook.Application")  #w, needed for importing constants:
        yNS = yOL.GetNamespace("MAPI")
        #yFolder = yNS.Folders['BXSelfCurrent'].Folders['BTHM'].Folders['0-outlook usage'].Folders['Test Run Outlook Usage'].Folders['Securities']
        yFolder1 =yNS.Folders['BXSelfCurrent'].Folders['BTHM'].Folders['0-outlook usage'].Folders['Test Run Outlook Usage'].Folders['Securities'].Folders['History']

        s1=yFolder1.Items
        #s1.Sort(Property="[EffDate]", Descending= False )  # 1 is descenting,
        
        sFilter=f"[SEC]='{Sec}'"
        #sFilter="[Subject]=""Test"""
        ### f1=yFolder1.Items.Restrict(sFilter) #works
        f1=s1.Restrict(sFilter) #worksunt

        # sort is only effective on preinstalled fields, not on user propterties field, but restrict() can accept user property
        # false, date sorted from earilest to latest to none; True, from none, Lastest to earlier 
        f1.Sort(Property="[EffDate]", Descending= True )  

        print ("step1")
        v1=1 #=f1.GetLast().UserProperties.Find("SEC").Value
        print ("step2")
        
        if (1==1): 
            z=v1
            
        else:
            z=f1.GetLast().UserProperties.Find("EffDate").Value

        print ("Items", f1.Count, " Sec ", Sec, "search =", {sFilter} , 'first item:', z )     

        ###for yOLI in yFolder1.Items:
        for yOLI in f1:
            c1= 1 #yOLI.UserProperties.Find("SEC").Value
            if (c1 > 0): 
                #print(f"Sec:{yOLI.UserProperties.Find("SEC").Value} Effect date: {yOLI.UserProperties.Find("EffDate").Value}, price {yOLI.UserProperties.Find("Price").Value}, CmprsdeB= {}   ") 
                a= yOLI.UserProperties.Find("SEC").Value   
                b=yOLI.UserProperties.Find("EffDate").Value
                c=yOLI.UserProperties.Find("Price").Value
                d=yOLI.UserProperties.Find("CmprsdS").Value
                e= yOLI.TaskDueDate #https://docs.microsoft.com/en-us/office/vba/api/outlook.mailitem.creationtime
                f=2 # yOLI.Modified
                str1=f"Sec1:{a} Effect date:  {b}, {e}, {f}, price123= {c}, CmprsdeB= {d} "

                print (str1)

        #yOL=None

    def set_CmprsdData(self, FieldNm, Sec):
       
        yOL = win32.dynamic.Dispatch("Outlook.Application")  #w, needed for importing constants:
        yNS = yOL.GetNamespace("MAPI")
        yFolder1 =yNS.Folders['BXSelfCurrent'].Folders['BTHM'].Folders['0-outlook usage'].Folders['Test Run Outlook Usage'].Folders['Securities'].Folders['History']
       
        I1=yFolder1.Items
        
        #https://docs.microsoft.com/en-us/office/vba/outlook/how-to/search-and-filter/filtering-items
        # https://docs.microsoft.com/en-us/office/vba/outlook/how-to/search-and-filter/filtering-items-using-a-boolean-comparison
         #nw:  And  [Due Date] > '" & Format("1/15/20 3:30pm", "ddddd h:nn AMPM") & "'" 
         # And "[Due Date] IS NULL" actually filter out entries that Due Date is None 
    
        # sFilter=  [SEC]='NVDA' And [CmprsdS] >0
        # result of Not (Not ( [Due Date] IS NULL)) is Due Date has to be not Null (bug on pywin32 ???)
        sFilter=f"[SEC]='{Sec}' And [{FieldNm}] >0  And Not (Not ( [Due Date] IS NULL)) "
        lgd (f"filter = {sFilter}")

        f1=I1.Restrict(sFilter) #work
        lgd(" step1 ")

        # sort is only effective on preinstalled fields, not on user propterties field, but restrict() can accept user property
        # false, date sorted from earilest to latest to none; True, from none, Lastest to earlier 
        f1.Sort(Property="[Due Date]", Descending= False )  

        print ("Items", f1.Count, " Sec ", Sec, "search =", {sFilter} )     

        for yOLI in f1:
            #print(f"Sec:{yOLI.UserProperties.Find("SEC").Value} Effect date: {yOLI.UserProperties.Find("EffDate").Value}, price {yOLI.UserProperties.Find("Price").Value}, CmprsdeB= {}   ") 
            a= yOLI.UserProperties.Find("SEC").Value
            b=yOLI.UserProperties.Find("EffDate").Value   
            c=yOLI.UserProperties.Find("Price").Value
            d=yOLI.UserProperties.Find(FieldNm).Value
            e= yOLI.TaskDueDate #https://docs.microsoft.com/en-us/office/vba/api/outlook.mailitem.creationtime
                
            str1=f"Sec1:{a} Effect/due date: {b}/{e},  price123= {c}, {FieldNm}= {d} "
            df1=self.HistDF
            lgd (str1)
            lgd ( df1.shape)
            #print (df1)

            # can not use Date, it is an index column
            yDate3=self.HistDF['datetime'].values[-1]  # nw: yDate.strftime("%m") yDate in Epoch format
            print (f", type ydate= ", type(yDate3))  #, datetime.datetime.fromtimestamp( 1653022800000).strftime("%m") )
            lgd (f" due  date: {e};  {datetime.datetime.timestamp(e)} " )


            #https://datagy.io/pandas-conditional-column/
            # x 1000 since TDA timestamp uses ms, and python dt ts uses sec 
            df1.loc[df1['datetime'] > datetime.datetime.timestamp(e)*1000, f'{FieldNm}'] = d

            lgd ("step 2")



        
        
        yOL=None        







    #generate alert for stock obj and later to outlook item 
    def cal_SMA_Alert(self): 
            self.SMA=self.HistDF['SMA1'][-1]  # column 5 is sma , get this latest SMA value to stock object
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
        #pdir=r'C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\historical_data\a_Debug'
        pdir=a_Settings.URL_CVS_file
        
        path= a_utils.addDir(pdir, cdir)

        path=a_utils.DF2CSV(self.HistDF, path, self.Symbol, '')

        lgi("SaveHist() path:  " + str(path) )

    def GetHist_TDA(self):

        ySDate=a_utils.epoch_from_today( Yr=1, Mo=0, Day=0) 
        df=a_TDA_IF.TDA_Price_Hist ( Symbol=self.Symbol, StartDTStamp=ySDate, EndDTStamp=0 )

        return df


# %%
def test1():
    df123 = pd.DataFrame(
        {"a" : [4 ,5, 6], 
        "b" : [7, 8, 9], 
        "c" : [10, 11, 12]},    
        index = [1, 2, 3])
    print (df123)
    ### z1=df123['c'].values[-1]
    ### z1=df123['c'][1]  # works with indexing, =10 
    #nw z1=df123['c'][-1]
    #nw z1=df123['c',-1]
    #nw z1=df123[-1, 'c']
    #nw z1=df123.iloc['c',-1]
    #nw z1=df123.iloc[-1, 'c']
    #nw z1=df123.iloc['c',1]
    #nw z1=df123.iloc[1,'c']
    np1=df123['c'].to_numpy()
    z1=np1[-1]
    print(f" df type= {type(z1)}, { z1}    ")    

# %% running tests
if __name__ == '__main__':
    test1()



# %%
