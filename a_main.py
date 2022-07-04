# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
###############
# main.ipynb is where you test run and put everything together 
# released classes, functions with  test code are converted to 
#         1.  a_nnn.py as modules to use,  and 
#         2.     nnn.ipynb for further development
#
#  ipynb is by nature for testing codes
#  py is for usage ( allow import of def and etc.)
#  
# add import session to top cell of all py and ipynb files 
# add status and date to  2nd top cell of all py and ipynb files 
# 
# #nw: no working 
# ## temporary try  
# 


# %%
# logging for debugging 
import logging
# for every module/library file 
# need below code block in this debug cell in very file / module to use lgd,ldi,lgw,lge, lgc 
# [from xxx import yyy as zzz] is to rename yyy to zzz
from logging import debug    as lgd   #10
from logging import info     as lgi   #20
from logging import warning  as lgw   #30
from logging import error    as lge   #40
from logging import critical as lgc
#from types import NoneType

from sqlalchemy import null   #50 #

# step 2, select one of below line 
import a_logging as alog
# to customize the logging obj, all format propregate to root logging obj
lg=alog.BTLogger( stdout_filter=alog.yfilter20, stream_filter=alog.yfilter40)




# %%
# imports
from io import StringIO
from signal import SIG_DFL
#####################
import sys 
import datetime
import a_utils
import a_Settings
################
import a_Stock_IF
#################
import a_OL_IF
#(base) PS C:\Users\ben t> conda install -c anaconda pywin32 for win32com
# conda list pywin32
# (base) PS C:\Users\ben t> pip install pywin32 --upgrade
# Collecting pywin32
#   Downloading pywin32-304-cp38-cp38-win_amd64.whl (12.3 MB)
#      |████████████████████████████████| 12.3 MB 3.3 MB/s
# Installing collected packages: pywin32
#   Attempting uninstall: pywin32
#     Found existing installation: pywin32 227
#     Uninstalling pywin32-227:
#       Successfully uninstalled pywin32-227
# Successfully installed pywin32-304
#(base) C:\Users\ben t>pip install --upgrade pywin32==300  #works, 304 does not
import win32com.client as win32 
from win32com.client import constants as C
################# TA1_plt.py
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
import a_TA1_Plt
import a_FinViz

# %%
# sumnmary DF


def genSummaryDF():
    try:
        yDF=pd.DataFrame(
        { "Datetime":[datetime.datetime.now()],    
          "Symbol":['Summary'],
          "Close":[1],
          "Volume" : [2],
          "PriceDate":[np.NaN],
          "Cost":[0],
          "Shares":[0],
          "Flag":['Flags'], 
          "Link2Plot":['lk1'], 
          "Link2OLI":['lk2']
        },
    index=[0]) 
    except:
        lge('failed')
    finally:
        return yDF

# %%
# TDAAPI mainEntry function   from Outlook list of securities 
def mainEntry(only_Selected=0, testrun=1 ):
    ##only_Selected=0   # only OLI with [Selected] is true
    ##testrun=1          # only use saved data file in csv format, not need to connect to internew
    only_exclamation=0 # only those outlook exclamation marked items are updated
    ####################################
    # for compressed buy, sell and shares + cost need to set "due date" to take effect, 
    # once set, they are not changed until further change
    # compressed buy, sell and shares + cost effect is sticky , changes are made in  \Sec folder
    # 
    # for events, OLI subject and "eventdate" are required to put it on the chart 
    # events are single date items, need to be added in \history foldler 
    # 


    ySummaryDF=genSummaryDF()

    #https://stackoverflow.com/questions/50127959/win32-dispatch-vs-win32-gencache-in-python-what-are-the-pros-and-cons
    ## yWD= win32.gencache.EnsureDispatch("Word.Application")  # gencache.EnsureDispatch for wdConstant enumeration
    ## yOL = win32.gencache.EnsureDispatch("Outlook.Application")  #w, needed for importing constants:
    yWD= win32.dynamic.Dispatch("Word.Application")  # gencache.EnsureDispatch for wdConstant enumeration
    yOL = win32.dynamic.Dispatch("Outlook.Application")  #w, needed for importing constants:


    yNS = yOL.GetNamespace("MAPI")
    yFolder = yNS.Folders['BXSelfCurrent'].Folders['BTHM'].Folders['0-outlook usage'].Folders['Test Run Outlook Usage'].Folders['Securities']
    yFolder1 =yNS.Folders['BXSelfCurrent'].Folders['BTHM'].Folders['0-outlook usage'].Folders['Test Run Outlook Usage'].Folders['Securities'].Folders['History']

    for yOLI in yFolder.Items:
        print(yOLI.UserProperties.Find("SEC").Value +'-------------------------------------------------------------')
        # flush the string_io for next security
        lg.FlushStringIO()

    
        #################################################################
        #only go further for those are marked "Test" in OLI subject field
        yMsg=''
        if testrun==1  and yOLI.Subject  !='Test':
            continue
        elif testrun==1 :
            yMsg=" -------> Using Test Data <-------" 

        
        #https://docs.microsoft.com/en-us/office/vba/api/outlook.olimportance
        #https://docs.microsoft.com/en-us/office/vba/api/outlook.mailitem.importance
        if only_exclamation==1 and yOLI.Importance!= 2: continue

        if only_Selected==1 and yOLI.UserProperties.Find("SELECTED") is None: continue 
        if only_Selected==1 and yOLI.UserProperties.Find("SELECTED").Value == False : continue

        if yOLI.UserProperties.Find("Sec").Value == "Summary": continue

        ################################################################
        #good
        yOLI1=yOLI.Copy() # for gettingh the latest setting from user, so compressedBS and Event info can be on plot
        yOLI1.Move(yFolder1)
        
        
        yO_S=a_OL_IF.OLI_Stock(yOLI,lg)
        yO_S.InitStock()


        if yO_S.Stock.GetHist(testrun) == 0: continue  # 20220218 , changed from 1 to 0 ; 1 for testing, 0 for getting data from TDA 

        yTA3=a_TA1_Plt.TA1(yO_S.Stock) 
        yTA3.createPriceDS() 

        #print('TAS=', yTA3.TAs)
        #print( 'Prices=', yTA3.prices)

        yTA3.set_TAs()

        #print("ta3=", yTA3.TAs)
        yPlt=a_TA1_Plt.TA1_Plt()    

        yO_S.Stock.SaveHist()
        yPlt.plt_all(yTA3)

    
        #get plot from FinViz.com
        yFV=a_FinViz.FinViz()
        yFV.getChart(yO_S.Stock)

        #save hist here so to include TA1 data
        ###yO_S.Stock.SaveHist()

        # lgi(" before Updating OLI")

        yO_S.UpdateOLI(yMsg)
        
        #! if OLI save with error not tringgering lge, lgd, something is wrong with outlook,
        #! disable the addins in outlook, outlookchangenotifier is especially suspicious
        yOLI.Save()
        lgw("debug1")
        #so to save a new copy to /history/ folder
        # delete the previous one for compressedBD and event processing
        yOLI1.Delete()

        #https://docs.microsoft.com/en-us/office/vba/api/outlook.mailitem.copy
        yOLI2=yO_S.OLI.Copy()
        #copy newly processed item from \sec to\ history
        lgw("debug2")
        yOLI2.Move(yFolder1)
        a_OL_IF.OLICleanup1(yO_S.OLI) 
        lgw("debug3")

        #delete the eventdate and due date
        
        lgw("debug4")
        yO_S.OLI.Close(0)  #! save the outlook item, error means something wrong in writing to OLI 

        yO_S.Stock.SummaryDF(ySummaryDF, "1212121ID")

  

    a_utils.DF2CSV(ySummaryDF, a_Settings.URL_debug_data_path, "SummaryDF")
    a_OL_IF.updateSummaryOLI(ySummaryDF,  yFolder) 
    #lgw(f"Summary DF= {ySummaryDF}")


    print(">>>>>>>>>>>>Finsihed iteration of SEC OLIs")    
        
    yWD=None
    yOL=None   



######################################################
# %%
# running mainEntry ()
if __name__ == "__main__" :
    mainEntry(only_Selected=1, testrun=0) 


###################################################
#%%
# testing module code
###################################################


# %%
if __name__ == "__main__" :
    yDF= genSummaryDF()
    print (yDF)

