# this file is for setting 
import os

URL_debug_data_file=r'\HistoricalData\Debug\GOOG_2022_02_20-21_03.csv'
URL_CVS_file=r'\HistoricalData'
URL_plt_path=r"\HistoricalData"

URL_ChromeDriver=r'C:\Users\ben t\Downloads\chromedriver_win32\chromedriver.exe'

# Outlook image insertion requires absolute path while Pandas CVS write does not 
absolute_path=os.getcwd()

URL_debug_data_file=absolute_path+URL_debug_data_file
#URL_hist_data_file=absolute_path+r'\HistoricalData\Debug\GOOG_2022_02_20-21_03.csv'
URL_CVS_file=absolute_path+URL_CVS_file
URL_plt_path=absolute_path+URL_plt_path