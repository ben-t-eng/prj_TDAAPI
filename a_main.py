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

#?from sqlalchemy import null   #50 #

# step 2, select one of below line 
import a_logging 

# to customize the logging obj, all format propregate to root logging obj
lg=a_logging.BTLogger( stdout_filter=a_logging.yfilter30, stream_filter=a_logging.yfilter40)




# %%
# imports
from io import StringIO
from signal import SIG_DFL
#####################
import sys 
import datetime
import a_utils
from a_utils import xLB
from a_utils import xL2UTC

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
          "Link2OLI":['lk2'],
          "Note":['notes'],
          "LSUpdate":[datetime.datetime.now()],
          "Sort":[0],
          "Sector":[''],
          "Stage":[''],
          "PriceChg":[0],       #%  over prvious price
          "VolChg":[0],         #%  over preious volumn
          "Streak":[0]           #consective up +, or down - days
        },
    index=[0]) 
    except:
        lge('failed')
    finally:
        return yDF

# %%
# TDAAPI mainEntry function   from Outlook list of securities 
def mainEntry(only_Selected=0, testrun=1, Clear_Flag=0 ):
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
    #   http://www.icodeguru.com/webserver/Python-Programming-on-Win32/ very through pages

    ySummaryDF=genSummaryDF()

    #https://stackoverflow.com/questions/50127959/win32-dispatch-vs-win32-gencache-in-python-what-are-the-pros-and-cons
    ##yWD= win32.gencache.EnsureDispatch("Word.Application")  # gencache.EnsureDispatch for wdConstant enumeration
    ##yOL = win32.gencache.EnsureDispatch("Outlook.Application")  #w, needed for importing constants:
    yWD= win32.dynamic.Dispatch("Word.Application")  # gencache.EnsureDispatch for wdConstant enumeration
    yOL = win32.dynamic.Dispatch("Outlook.Application")  #w, needed for importing constants:


    yNS = yOL.GetNamespace("MAPI")
    yFolder = yNS.Folders['BXSelfCurrent'].Folders['BTHM'].Folders['0-outlook usage'].Folders['Test Run Outlook Usage'].Folders['Securities']
    yFolder1 =yNS.Folders['BXSelfCurrent'].Folders['BTHM'].Folders['0-outlook usage'].Folders['Test Run Outlook Usage'].Folders['Securities'].Folders['History']

    #####copy select sec OLIs from \sec to \history for further processing
    for yOLI in yFolder.Items:
        #print(yOLI.UserProperties.Find("SEC").Value +'-------------------------------------------------------------')
       

        #################################################################
        #only go further for those are marked "Test" in OLI subject field
        yMsg=''
        if testrun==1  and yOLI.Subject  !='Test':
            continue


        
        #https://docs.microsoft.com/en-us/office/vba/api/outlook.olimportance
        #https://docs.microsoft.com/en-us/office/vba/api/outlook.mailitem.importance
        if only_exclamation==1 and yOLI.Importance!= 2: continue

        if only_Selected==1 and yOLI.UserProperties.Find("SELECTED") is None: continue 
        if only_Selected==1 and yOLI.UserProperties.Find("SELECTED").Value == False : continue

        if yOLI.UserProperties.Find("Sec").Value == "Summary": continue

        ################################################################
        #good
        
        a_OL_IF.SetOLIUsrPropDir(yOLI,'Update' , 'Updating',1)
        yOLI.Close(0)  #w! this is required, or else OLI in \Sec [update] is not set to 'Updating'

        yOLI1=yOLI.Copy()
        a_OL_IF.SetOLIUsrPropDir(yOLI1, "EID", yOLI.EntryID, FieldType=1)
        yOLI1.Save()
        yOLI1.Move(yFolder1) 
        lgd(f' EID = {yOLI1.UserProperties.Find("EID").Value }' )

        yUpdateDT=datetime.datetime.now() # for filtering latest OLI
        print(yOLI.UserProperties.Find("SEC").Value +' in \Sec--------------------')

    # when adding new fields, need to add them manually at OL
    
    I2=yFolder1.Items.Restrict("[Update]='Updating' ") 
    lgw(f' total sec in updating status {I2.Count}    ')
    yUpdateDT=datetime.datetime.now() # for filtering latest OLI
    for yOLI in I2:
        
        lg.FlushStringIO()

        if yOLI.UserProperties.Find("Sec").Value == "Summary": continue

        ################################################################
        #good
        print(yOLI.UserProperties.Find("SEC").Value +' in \history-------------------')
        
        if Clear_Flag != 0:  yOLI.ClearTaskFlag()
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
        ###070422 this update of deleting "Updating" confused the filter: a_OL_IF.SetOLIUsrPropDir(yOLI,'Update', 'Updated',1)  # done with updating, so next round, it is not selected per update
        
        #! if OLI save with error not tringgering lge, lgd, something is wrong with outlook,
        #! disable the addins in outlook, outlookchangenotifier is especially suspicious
        yOLI.Save()
        #lgw("debug1")


        #so to save a new copy to /history/ folder
        # delete the previous one for compressedBD and event processing
         #delete the original updating OLI at \sec 
        try:
            yEID=yOLI.UserProperties.Find("EID").Value
            lgd(f" EID is {yEID} ")
            #delete the org in \sec 
            yOLI3=yNS.GetItemFromID(yEID, yFolder.StoreID)
            yOLI3.Delete()
        except:
            lge(f"fail to get EID of {yOLI.UserProperties.Find('Sec').Value} ")

        #works with yOLI.EntryID, but not with yOLI2.EntryID, why???070422
        yO_S.Stock.updateSummaryDF(ySummaryDF, yOLI)     


        # can't not clear "update" field within thie for loop due to the filter by [update]
        #lgw("debug4")
        yOLI.Close(0)  #! save the outlook item, error means something wrong in writing to OLI 
        # 7/3, 611f18d (HEAD -> main, origin/main) w/ RPC server issue, but summaryOLI is almost done
        # is now functional without "RPC not available" issue 
        # without specific change on window 10 !!!!!!!need to have outlook running 
       
        #https://docs.microsoft.com/en-us/office/vba/api/outlook.mailitem.copy
        yOLI2=yOLI.Copy()

        a_OL_IF.OLICleanup1(yOLI2) 
        yOLI2.Save()
        yOLI2.Close(0) 
        yOLI2.Move(yFolder)


    a_OL_IF.updateSummaryOLI(ySummaryDF,  yFolder) 
    
    #debug dataframe
    #not the DF being sorted, use the one inside summaryOLI a_utils.DF2CSV(ySummaryDF, a_Settings.URL_debug_data_path, "SummaryDF")
    
    
    

    # not needed since eid is used to track and delete the one from \sec, as updated ones are copy to \sec
    #delete original OLIs for update, clear updated OLIs [update] field
    I1=yFolder.Items.Restrict("[Update]='Updating' ") 
    lgd(f'clr udpate field for {I1.Count} \sec OLIs ')
    for yOLI in I1:
        try:
            yLSUpdate=yOLI.UserProperties.Find("LSUpdate").Value
            yLSUpdate1=yLSUpdate.astimezone() - xL2UTC
            yLSUpdate2=datetime.datetime.fromtimestamp((datetime.datetime.timestamp(yLSUpdate1)))
            lgw(f" yUpdate time {yUpdateDT} {type(yUpdateDT)}, yLSUpdate {yLSUpdate1} {type(yLSUpdate1)}")
            
            if yLSUpdate2 < yUpdateDT:
                yOLI.Delete()
                lgw(f'{yOLI.UserProperties.Find("LSUpdate").Value}, LSUpdate2 < UPdate start    ' )
            else: 
                a_OL_IF.SetOLIUsrPropDir(yOLI,'Update', ' ',1) 
                yOLI.Save()
        except:
            lge(f'failed to clear update field in \Sec {yOLI.UserProperties.Find("Sec").Value}')
        

    #clear oli with [update] field in \history
    #this is necessary due to the previous for loop for \history is filter by [update] filter
    # SW is confused if [update] is changed within the for loop 
    yStrg=yUpdateDT.strftime("%m/%d/%y  %H:%M%p" )
    I1=yFolder1.Items.Restrict(f"[LSUpdate] >= '{yStrg}' ") 
    lgw(f' to clear update fields in \history OLIs, total {I1.Count} ')  #nw! \history OLIs; { yOLI.UserProperties.Find("LSUpdate").Value} > {yStrg}    ')
    for yOLI in I1:
        try:
            a_OL_IF.SetOLIUsrPropDir(yOLI,'Update', ' ',1) 
            yOLI.Save()
        except:
            lge('Failed to clear update in \history')
    #lgw(f"Summary DF= {ySummaryDF}")

    #########################
    #debugging entryID chg when move OIL 
    #I2=yFolder1.Items.Restrict("[Subject]='yOLI2' and [Sec]='QQQ' ") 
    #yOLI3=I2.GetFirst()
    #lgd(f' yOLI3 entryID: {yOLI3.EntryID }')
    #########################


    print(">>>>>>>>>>>>Finsihed iteration of SEC OLIs")    
        
    yWD=None
    yOL=None   



######################################################
# %%
# running mainEntry ()
# outlook needs to be running, or else there will be  PRC error 
if __name__ == "__main__" :
    a=1
    mainEntry(only_Selected=1, testrun=0) 


###################################################
#%%
# testing module code
###################################################


# %%
#w! for outlook table item filter on date comparison, 
def yTestVB():
    yWD= win32.dynamic.Dispatch("Word.Application")  # gencache.EnsureDispatch for wdConstant enumeration
    yOL = win32.dynamic.Dispatch("Outlook.Application")  #w, needed for importing constants:


    yNS = yOL.GetNamespace("MAPI")
    yFolder = yNS.Folders['BXSelfCurrent'].Folders['BTHM'].Folders['0-outlook usage'].Folders['Test Run Outlook Usage'].Folders['Securities']
    yFolder1 =yNS.Folders['BXSelfCurrent'].Folders['BTHM'].Folders['0-outlook usage'].Folders['Test Run Outlook Usage'].Folders['Securities'].Folders['History']

    yDT=datetime.datetime(2022,7,5,0,50)
    yDTStrg=yDT.strftime("%m/%d/%y  %H:%M%p" )
    sFilter= f" [LSUpdate] > '{yDTStrg}' "
    print(sFilter)
    I2=yFolder.Items.Restrict(sFilter)
    print (f" i count={I2.Count}")

if __name__ == "__main__" :
    #yTestVB()
    a=1