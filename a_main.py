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
##############
# all the imports
##### for logging 
import logging
from logging import debug as lgd
from logging import info as lgi
from logging import error as lge
from logging import warning as lgw
from logging import critical as lgc
from io import StringIO
#####################
import sys 
import datetime
import a_utils
################
import a_Stock_IF
#################
import a_OL_IF
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


# %%
# logging for debugging 
#
#yfilter=a_utils.LevelFilter((logging.CRITICAL,logging.INFO, logging.WARNING, logging.DEBUG))
yfilter=(a_utils.LevelFilter((logging.INFO, logging.CRITICAL, logging.DEBUG)) , a_utils.LevelFilter((logging.INFO, logging.CRITICAL, logging.DEBUG)))
yfilter2=(a_utils.LevelFilter((logging.INFO, logging.DEBUG)) , a_utils.FileFilter())
yfilter3=(a_utils.LevelFilter((logging.INFO,)) , a_utils.FileFilter())
yfilter1=a_utils.LevelFilter((logging.WARNING, logging.INFO, logging.DEBUG))  # have to have two items , even if the same
global lg
lg=a_utils.BTLogger( stdout_filter=yfilter3, stream_filter=yfilter3)


# %%
# start from Outlook 
yWD= win32.gencache.EnsureDispatch("Word.Application")  # gencache.EnsureDispatch for wdConstant enumeration
yOL = win32.gencache.EnsureDispatch("Outlook.Application")  #w, needed for importing constants:
yNS = yOL.GetNamespace("MAPI")
yFolder = yNS.Folders['BXSelfCurrent'].Folders['BTHM'].Folders['0-outlook usage'].Folders['Test Run Outlook Usage'].Folders['Securities']

for yOLI in yFolder.Items:
    print('-------------------------------------------------------------')
    # flush the string_io for next security
    lg.FlushStringIO()

    yO_S=a_OL_IF.OLI_Stock(yOLI,lg)
    yO_S.InitStock()
    yO_S.Stock.GetHist()  

    yTA3=a_TA1_Plt.TA1(yO_S.Stock) 
    yTA3.createPriceDS() 

    #print('TAS=', yTA3.TAs)
    #print( 'Prices=', yTA3.prices)

    yTA3.set_TAs()

    #print("ta3=", yTA3.TAs)
    yPlt=a_TA1_Plt.TA1_Plt()    


    yPlt.plt_all(yTA3)

   
    yO_S.UpdateOLI()


    #yStock=a_OL_IF.InitStock (yOLI)
    #yStock.GetHist() # include TA and saving 
    #a_OL_IF.UpdateOLI1(yOLI, yStock, lg)

   # print ('----OL comment:'+lg.log_StringIO.getvalue())
    yOLI=None
    break
    


