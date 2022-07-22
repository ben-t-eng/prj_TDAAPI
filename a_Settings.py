# this file is for setting 
import os

URL_debug_data_file0=r'\HistoricalData\Debug\GOOG_2022_02_20-21_03.csv'
URL_CSV_file0=r'\HistoricalData'
URL_Funda_CSV0=r'\HistoricalData'
URL_plt_path0=r"\HistoricalData"
URL_debug_data_path0=r'\HistoricalData\Debug'
URL_summary_data_path0=r'\HistoricalData\Summary'
#has to match chrome browser revision ,as of 4/09/2022, rev 100
URL_ChromeDriver0=r'\chromedriver_win32\chromedriver_102.exe'

# Outlook image insertion requires absolute path while Pandas CSV write does not 
# browser
absolute_path=os.getcwd()

URL_ChromeDriver=absolute_path+URL_ChromeDriver0
URL_debug_data_file=absolute_path+URL_debug_data_file0
#URL_hist_data_file=absolute_path+r'\HistoricalData\Debug\GOOG_2022_02_20-21_03.csv'
URL_CSV_file=absolute_path+URL_CSV_file0
URL_Funda_CSV=absolute_path+URL_Funda_CSV0
URL_plt_path=absolute_path+URL_plt_path0
URL_debug_data_path=absolute_path+URL_debug_data_path0
URL_summary_data_path=absolute_path+URL_summary_data_path0