# this file is for setting 
import os

URL_debug_data_file=r'\HistoricalData\Debug\GOOG_2022_02_20-21_03.csv'
URL_CVS_file=r'\HistoricalData'
URL_plt_path=r"\HistoricalData"

#has to match chrome browser revision ,as of 4/09/2022, rev 100
URL_ChromeDriver=r'\chromedriver_win32\chromedriver_100.exe'

# Outlook image insertion requires absolute path while Pandas CVS write does not 
# browser
absolute_path=os.getcwd()

URL_ChromeDriver=absolute_path+URL_ChromeDriver
URL_debug_data_file=absolute_path+URL_debug_data_file
#URL_hist_data_file=absolute_path+r'\HistoricalData\Debug\GOOG_2022_02_20-21_03.csv'
URL_CVS_file=absolute_path+URL_CVS_file
URL_plt_path=absolute_path+URL_plt_path