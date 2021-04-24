
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
        tmstr=datetime.datetime.now().strftime("%x")
        tmstr=tmstr.replace('/','_')
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
        TimeString=datetime.datetime.now().strftime("%x")
        TimeString=TimeString.replace('/','_')
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
def DateTime2UTC(DateTime):
    localDateTime=DateTime.astimezone()  # add tz info to DT object
    localTZinfo=localDateTime.tzinfo        # get tzinfo obj 
    
    lgd('DateTime2UTC(): Local timezone name===', localTZinfo.tzname(localDateTime) )

    TimeDelta=localTZinfo.utcoffset(localDateTime)
 
    UTCDT= localDateTime+TimeDelta
 
    #UTCDT1= UTCDT.astimezone(timezone.utc)
    return UTCDT


#%%
#from datetime import datetime
def TDAepoch2DT(TDA_TS ):
    # in ms
    ySTARTDATE_TS=315561600000    #1980/1/1

    if TDA_TS >= ySTARTDATE_TS:
        yDT=datetime.datetime.fromtimestamp(TDA_TS/1000)
    else :
        yDT=datetime.datetime.fromtimestamp(ySTARTDATE_TS/1000)

    return yDT

#%%
import logging
import sys 
from io import StringIO
import datetime

class LevelFilter(logging.Filter):
    ##example: yFilter1=LevelFilter((logging.INFO, logging.WARNING, logging.ERROR))
    def __init__(self, levels=(logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL, logging.DEBUG) ):
        self.levels = levels # logging level tuple

    def filter(self, record):
        return record.levelno in self.levels


class BTLogger:
    def __init__(self, lognm='', stream_filter=None, stdout_filter=None, stderr_filter=None ):

        self.loggernm=lognm
        self.filter_stream =stream_filter  #type LevelFilter
        self.filter_stdout=stdout_filter
        self.filter_stderr=stderr_filter


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
        log_format='+%(funcName)s\%(lineno)s|%(levelname)s: %(message)s [%(filename)s %(asctime)s]'
        dt_format= '%m/%d:%I:%M'#  %p'
        yHandler.setFormatter(logging.Formatter(log_format, datefmt=dt_format))
        
        yHandler.setLevel=(logging.INFO) #c no effect 
        if self.filter_stdout != None : yHandler.addFilter( self.filter_stdout )

        self.log_stream=StringIO()
        yHandler1=logging.StreamHandler(self.log_stream)          
        log_format='+%(funcName)s\%(lineno)s|%(levelname)s: %(message)s [%(filename)s %(asctime)s]'
        dt_format= '%m/%d:%I:%M'#  %p'
        yHandler1.setFormatter(logging.Formatter(log_format, datefmt=dt_format))   
        
        yHandler1.setLevel=(logging.INFO) #c no effect 
        if self.filter_stream != None : yHandler1.addFilter( self.filter_stream )
        
    
        if (yLog.hasHandlers()):
            yLog.handlers.clear()  #c logging has its default handle if logging basic config is called 
        yLog.addHandler(yHandler)
        yLog.addHandler(yHandler1)
        
    
        self.d=lambda y: yLog.debug(y)
        self.i=lambda y: yLog.info(y)
        self.w=lambda y: yLog.warning(y)
        self.e=lambda y: yLog.error(y)
        self.c=lambda y: yLog.critical(y)

        # start the very first log with datetime
        logging.info('logging started at:' + datetime.datetime.now().strftime('%x'))

        

#lgi=lambda y: logging.info(y)
#gw=lambda y: logging.warning(y)
#lge=lambda y: logging.error(y)
#lgc=lambda y: logging.critical(y)
#lgd=lambda y: logging.debug(y)
    