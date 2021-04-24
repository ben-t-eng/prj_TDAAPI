
# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
#shared routines for commonly used features
import datetime
import os
import unittest
from dateutil import tz 


# %%
# how to import functions from other jupyter files
# https://stackoverflow.com/questions/50576404/importing-functions-from-another-jupyter-notebook


# %%
import os

def addDir( pdir, cdir ):
#https://www.geeksforgeeks.org/create-a-directory-in-python/
    
    path=os.path.join(pdir,cdir)

    # save it to file for later use 
    if not os.path.exists(path):
        try:
            os.makedirs(path) 
            print ('addDir() Dir created')
        except OSError as e:
            print(e)
    else:
        print ('addDir() Dir already exists')
    return path

# test code
symbol='AMD'
cdir=symbol
pdir=r'C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\historical_data'
path= addDir(pdir, cdir)

print(path) 



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
        print('DF2CSV(): path=', path)
        PD_DF.to_csv(path)
    except:
        print('DF2CSV() error in writing csv file')
    return path
#



#r'C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\historical_data'
#path=r'c:\abc\efg'
filenm='AZM'
tmstr=datetime.datetime.now().strftime("%x")
tmstr=tmstr.replace('/','_')
filenm1=filenm+'_'+tmstr+'.csv'
path1=os.path.join(path,filenm)

PD_DF= pd.DataFrame({"a":[4,5,6],'b':[7,8,9]},index=[1,2,3])
print("PDDF=", PD_DF)

DF2CSV(PD_DF,path, filenm)
print('path=', path)

# 417, not complete
class tDF2CSV(unittest.TestCase):
    def test_1(self):
        result=DF2CSV(PD_DF,  path, filenm,tmstr) 
        self.assertEqual(result,"expected value")


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

     print (yDate.strftime("%x"))
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

     print (Date.timestamp)
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
    
    print('DateTime2UTC(): Local timezone name=', localTZinfo.tzname(localDateTime) )

    TimeDelta=localTZinfo.utcoffset(localDateTime)
 
    UTCDT= localDateTime+TimeDelta
 
    UTCDT1= UTCDT.astimezone(timezone.utc)
    return UTCDT1


#%%
from datetime import datetime
def TDAepoch2DT(TDA_TS ):
    # in ms
    ySTARTDATE_TS=315561600000    #1980/1/1

    if TDA_TS >= ySTARTDATE_TS:
        yDT=datetime.fromtimestamp(TDA_TS/1000)
    else :
        yDT=datetime.fromtimestamp(ySTARTDATE_TS/1000)

    return yDT