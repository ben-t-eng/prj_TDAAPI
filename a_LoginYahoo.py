## working on 4/4/ 6:20pm


# %%
import time
from splinter import Browser
from selenium import webdriver
from login import username, password
username


# %%
# 4/4: splinter to interact with websits programmatically 
#chrome/firefox  driver
#select the same ver as you current chrome browser 
#Google Chrome is up to date
#Version 89.0.4389.114 (Official Build) (64-bit)
# exec_path= {'executable_path':''}
# https://chromedriver.chromium.org/downloads

# exec_path={'executable_path':r"C:\Users\bt\Downloads\chromedriver_win32"}
# e.g. driver = webdriver.Chrome(executable_path=r'C:/path/to/chromedriver.exe')
# from https://stackoverflow.com/questions/47148872/webdrivers-executable-may-have-wrong-permissions-please-see-https-sites-goo
exec_path={'executable_path':r"C:/Users/bt/Downloads/chromedriver_win32/chromedriver.exe"}

yWebsite='https://accounts.google.com/'
yYahoo="https://login.yahoo.com//"



# %%


#  set default behavior for browser
yOptions=webdriver.ChromeOptions()

yOptions.add_argument("--start-maximized")
yOptions.add_argument("--disable-notifications")
yOptions.add_argument("--disable-web-security")
yOptions.add_argument("--allow-running-insecure-content")
#yOptions.add_argument("--user-data-dir")

# headless makes browsers not visible
yBsr=Browser('chrome', **exec_path, headless=False, options=yOptions)

yBsr.visit(yYahoo)

# works as 11:16am 
# yBsr.visit(yWebsite)


# %%
# this is for c or
# https://stackoverflow.com/questions/45953043/selenium-test-scripts-to-login-into-google-account-through-new-ajax-login-form
#yBsr.find_by_id("identifierId").fill(username) # "email" did not work, but "identifierID" OK
#yBsr.find_by_id("identifierNext").click()
# google claims this login is not sure 

# try yahoo
yBsr.find_by_id("login-username").fill("txb321@yahoo.com")
time.sleep(0.5)
yBsr.find_by_id("login-signin").click()

time.sleep(3)  # need to wait long enough

yBsr.find_by_id("login-passwd").fill("pwd4yh002")
time.sleep(0.5)
yBsr.find_by_id("login-signin").click()

time.sleep(20)
# %%
# try yahoo 


