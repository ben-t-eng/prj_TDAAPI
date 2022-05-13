
# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
#shared routines for commonly used features
import datetime
import os
import unittest
from dateutil import tz 

##### for logging 
import logging
import sys 
from io import StringIO
import datetime
# from a_utils import lgc,lge,lgi,lgw,lgd #! you declare the functions in this file, do NOT import it again
from logging import debug as lgd
from logging import info as lgi
from logging import error as lge
#################

# %%
# how to import functions from other jupyter files
# https://stackoverflow.com/questions/50576404/importing-functions-from-another-jupyter-notebook


# %%
## import os

def addDir( pdir, cdir ):
#https://www.geeksforgeeks.org/create-a-directory-in-python/
#https://www.w3schools.com/python/python_try_except.asp    
    path=os.path.join(pdir,cdir)

    # save it to file for later use 
    if not os.path.exists(path):
        try:
            os.makedirs(path) 
            lgd ('addDir() Dir created')
        except OSError as e:
            lge(e)
    else:
        lgd ('addDir() Dir already exists')
    return path





# %%
import datetime
import os
import unittest
import numpy as np 
import pandas as pd



def DF2CSV(PD_DF, path, filenm, tmstr=''):
    # add time string to filename    
    if tmstr=='':
        # colnm ="SMA-" + datetime.datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
        ##tmstr=datetime.datetime.now().strftime("%x")
        ##tmstr=tmstr.replace('/','_')
        tmstr=datetime.datetime.now().strftime("%Y_%m_%d-%H_%M")

    filenm1=filenm + '_' + tmstr + '.csv'
    path=os.path.join(path, filenm1)
    try:
        lgd('DF2CSV(): path='+ path)
        PD_DF.to_csv(path)
    except:
        lge('DF2CSV() error in writing csv file')
    return path
#

#%%

def FilePath(Path, FileNm, TimeString='', Suffix='txt'):
    if TimeString=='':
        ##TimeString=datetime.datetime.now().strftime("%x")
        ##TimeString=TimeString.replace('/','_')
        TimeString=datetime.datetime.now().strftime("%Y_%m_%d-%H_%M")
    filenm1=FileNm + '_' + TimeString + Suffix
    yPath=os.path.join(Path, filenm1)

    return yPath
# %%

#%% epoch time
import time
import datetime
#https://www.w3schools.com/python/python_datetime.asp

def epoch_date_stamp( yYr=0, yMo=1, yDate=1):
     if yYr >1980 and yMo >0 and yMo <13 and yDate >0 and yDate<31  :
         yDate=datetime.datetime(yYr,yMo, yDate)
     else :
         yDate=datetime.datetime.now()

     lgd (yDate.strftime("%x"))
     return round(yDate.timestamp())   # TDA requires ms, therefore needs x1000


# %%
import time
import datetime
#https://www.w3schools.com/python/python_datetime.asp

def epoch_from_today( Yr=0, Mo=0, Day=0):
     if Yr >= 0 and Mo >=0 and Mo <13 and Day >=0 and Day <=31 :

         Day=Day+Mo*31 +Yr*365
         Date=datetime.datetime.now()-datetime.timedelta(days=Day )
         
     else :
         Date=datetime.datetime.now()

     lgd(Date.timestamp)
     return round(Date.timestamp())  # TDA requires ms, therefore needs x1000

#%%
#return UTC time for outlook, which treat py dt obj as UTC time
# outlook is not aware of a py dt object is tz specified
#

from dateutil import tz 
#
def DateTime2UTC4OLI(DateTime):
    localDateTime=DateTime.astimezone()  # add tz info to DT object
    localTZinfo=localDateTime.tzinfo        # get tzinfo obj 
    
    #lgd('Local timezone name=', localTZinfo.tzname(localDateTime) )

    TimeDelta=localTZinfo.utcoffset(localDateTime)
 
    #when + timedelta: utc now is  2022_05_08-16_14 CA now is  2022_05_08-23_14; ==> wrong 
    #when - timedelta: utc now is  2022_05_09-06_18 CA now is  2022_05_08-23_18; ==> correct 
    UTCDT= localDateTime + TimeDelta # +TimeDelta to make outlook datetime field "LSUDATE" dispiay PST times
     #lgd('Local timezone delta =', TimeDelta. )
    #UTCDT1= UTCDT.astimezone(timezone.utc)
    return UTCDT

def DateTime2UTC(DateTime):
    localDateTime=DateTime.astimezone()  # add tz info to DT object
    localTZinfo=localDateTime.tzinfo        # get tzinfo obj 
    
    #lgd('Local timezone name=', localTZinfo.tzname(localDateTime) )

    TimeDelta=localTZinfo.utcoffset(localDateTime)
 
    #when + timedelta: utc now is  2022_05_08-16_14 CA now is  2022_05_08-23_14; ==> wrong 
    #when - timedelta: utc now is  2022_05_09-06_18 CA now is  2022_05_08-23_18; ==> correct 
    UTCDT= localDateTime - TimeDelta # +TimeDelta to accomodate outlook datetime field "LSUDATE" match PST times
     #lgd('Local timezone delta =', TimeDelta. )
    #UTCDT1= UTCDT.astimezone(timezone.utc)
    return UTCDT

#%%
#from datetime import datetime; some error 
def TDAepoch2DT(TDA_TS ):
    # for Timestamp from TD-Ameritrade API 
    # need to add 15 hours = 54000000 ms to PST time ; 
    # TDATrade quote uses 12pm Timestamp until 9pm of the trade day,  
    # after 9pm, quote comes with 1 pm timestamp
    # in ms; POSIX timestamp is in seconds
    ySTARTDATE_TS=315561600000   #1980/1/1
    yBiasTDA2SD=54000000   

    if round(TDA_TS) > round(ySTARTDATE_TS):
        yDT=datetime.datetime.fromtimestamp((TDA_TS + yBiasTDA2SD)/1000)
    else :
        yDT=datetime.datetime.fromtimestamp(ySTARTDATE_TS/1000)

    return yDT

#%%
# May 5 /2022 : below logging codes are replaced by a_logg.py 
import logging
import sys 
from io import StringIO
import datetime

###################################################
#yfilter=a_utils.LevelFilter((logging.CRITICAL,logging.INFO, logging.WARNING, logging.DEBUG))
#yfilter=(a_utils.LevelFilter((logging.INFO, logging.CRITICAL, logging.DEBUG)), None) , a_utils.FileFilter())
#yfilter=(LevelFilter((logging.INFO, logging.CRITICAL, logging.DEBUG)) , a_utils.LevelFilter((logging.INFO, logging.CRITICAL, logging.DEBUG)))
#yfilter2=(LevelFilter((logging.INFO, logging.CRITICAL, logging.DEBUG)) , a_utils.FileFilter())

#yfilter1=(LevelFilter((logging.WARNING, logging.INFO, logging.DEBUG)),)  # have to have two items , even if the same
#yfilter3=[LevelFilter([logging.WARNING])]

###################################################
class LevelFilter(logging.Filter):
    ##example: yFilter1=LevelFilter((logging.INFO, logging.WARNING, logging.ERROR))
    def __init__(self, levels=(logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL, logging.DEBUG) ):
        self.levels = levels # logging level tuple

    def filter(self, record):
        return record.levelno in self.levels


class FileFilter(logging.Filter):
    #works 
    def __init__(self,files=('font_manager.py',) ):
        self.files=files

    def filter(self, record):
        if record.filename in self.files : 
            return False
        return True 


class BTLogger:
    def __init__(self, lognm='', stream_filter=None, stdout_filter=None, stderr_filter=None ):

        self.loggernm=lognm

        
        self.filters_stream =stream_filter  #type LevelFilter

        self.filters_stdout=stdout_filter

        self.filters_stderr=stderr_filter


        logging.basicConfig(level=logging.NOTSET)
        if self.loggernm =='':
            yLog=logging.getLogger()
        else:
            ylog=logging.getLogger(self.loggernm)

        # yLog.handlers.pop()
        # yLog.propagate=False   #when no handler to handle a log message at current level
        #yLog.setLevel(logging.DEBUG)  # critial,error,warning,info,debug, notset 
        #logging.basicConfig(format='%(asctime)s | %(levelname)s: %(message)s', level=logging.NOTSET)

        yHandler=logging.StreamHandler(sys.stdout) #stdout, so cell output is white  #if stderr, so cell output is red   
        ##log_format='+%(funcName)s\%(lineno)s|%(levelname)s: %(message)s [%(filename)s %(asctime)s]'
        log_format='>%(levelname)s[%(filename)s[%(lineno)s[%(funcName)s[ %(message)s [%(asctime)s'
        dt_format= '%m/%d:%I:%M %S'#  %p'
        yHandler.setFormatter(logging.Formatter(log_format, datefmt=dt_format))
        
        yHandler.setLevel=(logging.INFO) #c no effect 
        # if self.filter_stdout != None : yHandler.addFilter( self.filter_stdout )
        if self.filters_stdout != None : 
            for filter in self.filters_stdout:
                yHandler.addFilter(filter)

        self.log_StringIO=StringIO()

        yHandler1=logging.StreamHandler(self.log_StringIO)          
        ##log_format='~%(funcName)s\%(lineno)s|%(levelname)s: %(message)s [%(filename)s %(asctime)s]'
        log_format='>>%(levelname)s[%(filename)s[%(lineno)s[%(funcName)s[%(message)s [%(asctime)s'
        dt_format= '%m/%d:%I:%M %S'#  %p'
        yHandler1.setFormatter(logging.Formatter(log_format, datefmt=dt_format))   
        
        yHandler1.setLevel=(logging.INFO) #c no effect 
        if self.filters_stream != None : 
            for filter in self.filters_stream:
                yHandler1.addFilter(filter)
    
        if (yLog.hasHandlers()):
            yLog.handlers.clear()  #c logging has its default handle if logging basic config is called 
        yLog.addHandler(yHandler)
        yLog.addHandler(yHandler1)
        
        # not convient for in the log calling function info is always lambda
        self.d=lambda y: yLog.debug(y)
        self.i=lambda y: yLog.info(y)
        self.w=lambda y: yLog.warning(y)
        self.e=lambda y: yLog.error(y)
        self.c=lambda y: yLog.critical(y)

        # start the very first log with datetime
        logging.info('logging started at:' + datetime.datetime.now().strftime('%x'))

    def FlushStringIO(self):
        self.log_StringIO.seek(0)
        self.log_StringIO.truncate(0)
        
        

#lgi=lambda y: logging.info(y)
#gw=lambda y: logging.warning(y)
#lge=lambda y: logging.error(y)
#lgc=lambda y: logging.critical(y)
#lgd=lambda y: logging.debug(y)


# %% 
# testing module codes 
################################################

if __name__ == "__main__" : 
    # Epoch number from https://developer.tdameritrade.com/quotes/apis/get/marketdata/%7Bsymbol%7D/quotes
    print ('Quotetimelong:' ,TDAepoch2DT(1652158800000), "; tradetimelong:", TDAepoch2DT(315561600000), "; regularMarketTradeTimeInLong:", TDAepoch2DT(1652212800523)) 
    #Quotetimelong: 2022-05-10 16:58:13.837000 ; 
    #tradetimelong: 2022-05-10 16:58:13.837000 ; 
    #regularMarketTradeTimeInLong: 2022-05-10 13:00:00.523000

# %%
