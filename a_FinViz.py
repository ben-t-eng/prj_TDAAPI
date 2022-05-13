#%%
#rom curses import ACS_DARROW
#from socket import ALG_SET_AEAD_ASSOCLEN
#from attr import asdict
from splinter import Browser
from selenium import webdriver
import a_Settings 
import a_Stock_IF
import a_utils

import logging
from logging import debug as lgd
from logging import info as lgi
from logging import error as lge
from logging import warning as lgw
from logging import critical as lgc
from io import StringIO

#%%

class FinViz:
    def __init__(self):
        self.executable_path={'executable_path':a_Settings.URL_ChromeDriver }
        self.options=webdriver.ChromeOptions()
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-notifications")




    def getChart(self, yStock):
        try:
            
            filenm = f'{yStock.Symbol}_FinViz'    
            yPath= a_utils.addDir(yStock.TA1['plt_path'], yStock.Symbol)
            yPath= a_utils.FilePath(Path=yPath, FileNm=filenm, TimeString='', Suffix='')

            yFinVizURL="https://charts2.finviz.com/chart.ashx?t=" + yStock.Symbol +"&ty=c&ta=1&p=d&s=l"
                
            browser=Browser('chrome',**self.executable_path, headless=False) #headless means invisible
            browser.driver.set_window_size(900, 480)
            browser.visit(yFinVizURL)
            #screenshot_path = browser.find_by_tag('img').first.screenshot(yPath)
            screenshot_path = browser.screenshot(yPath)

             ### dictionary  yTA1.container.TA1 ---------- 
            yStock.TA1['Strategies']['FinViz']['plt_loc'].append(screenshot_path)

             #close browser
            browser.quit()
            lgi("FinViz plt saved at:" + str(screenshot_path) ) 
        
        except:
            lge('FinViz plt not saved to' + str(yPath))


#%% local function 
# running 220406
def getChart2( yStockSymbol, savePath):
        try:
            
             abs_path=os.getcwd()
             filenm = f'{yStockSymbol}_FinViz'    
             yPath=  a_utils.addDir( abs_path+savePath, yStockSymbol)  # addDir will create new dir if not exists
             yPath=  a_utils.FilePath(Path=yPath, FileNm=filenm, TimeString='', Suffix='')
             
             #has to match chrome browser revision ,as of 4/09/2022, rev 100
             yBrowserExe= {'executable_path': abs_path+r'\chromedriver_win32\chromedriver_100.exe'}
            
            
             #has to match chrome browser revision ,as of 4/09/2022, rev 100=
             yFinVizURL="https://charts2.finviz.com/chart.ashx?t=" + yStockSymbol +"&ty=c&ta=1&p=d&s=l"
             


             browser=Browser('chrome',**yBrowserExe, headless=False) #headless means invisible
             #browser=Browser('chrome',**yBrowserExe)
             
             browser.driver.set_window_size(900, 480)
             browser.visit(yFinVizURL)
             #screenshot_path = browser.find_by_tag('img').first.screenshot(yPath)  # require abs path, but no c:\
             screenshot_path = browser.screenshot(yPath)  # require abs path, but no c:\
            
              #close browser
             browser.quit()
             lgi("FinViz plt saved at:" + str(screenshot_path) )         

        except:
             lge('FinViz plt not saved to: ' + str(yPath))       


#%% 

if __name__ == '__main__':
    import a_utils
    import os

    getChart2("goog", "\HistoricalData\Debug")





# %%
