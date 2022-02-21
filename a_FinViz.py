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
            browser.visit(yFinVizURL)
            screenshot_path = browser.find_by_tag('img').first.screenshot(yPath)

             ### dictionary  yTA1.container.TA1 ---------- 
            yStock.TA1['Strategies']['FinViz']['plt_loc'].append(screenshot_path)

             #close browser
            browser.quit()
            lgi("FinViz plt saved at:" + str(screenshot_path) ) 
        
        except:
            lge('FinViz plt not saved to' + str(yPath))


       