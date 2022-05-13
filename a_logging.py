##### for logging 
##### https://realpython.com/python-logging/
### 4/23/2022 https://docs.python.org/3/howto/logging.html


# %%
# for main.py
# step1 copy this debug cell to main.py and every library module 
import logging
# for every module/library file 
# need below code block in this debug cell in very file / module to use lgd,ldi,lgw,lge, lgc 
# [from xxx import yyy as zzz] is to rename yyy to zzz
from logging import debug    as lgd   #10
from logging import info     as lgi   #20
from logging import warning  as lgw   #30
from logging import error    as lge   #40
from logging import critical as lgc   #50 

# step 2, select one of below line 
## import a_logging as alog
# to customize the logging obj, all format propregate to root logging obj
# to customize the logging obj, all format propregate to root logging obj
## lg=alog.BTLogger( stdout_filter=alog.yfilter30, stream_filter=alog.yfilter10)

# %%
# for a_logging.py code
import sys 
from io import StringIO
import datetime
from h11 import ERROR




# %%
# module code
class LevelFilter(logging.Filter):
    ##example: yFilter1=LevelFilter((logging.INFO, logging.WARNING, logging.ERROR))
    def __init__(self, levels=(logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL, logging.DEBUG) ):
        self.levels = levels # logging level tuple

    def filter(self, record):
        return record.levelno in self.levels

class FileFilter(logging.Filter):
    #works 
    def __init__(self,files=('font_manager.py','__init__.py',) ):
        self.files=files

    def filter(self, record):
        if record.filename in self.files : 
            return False
        return True 

class BTLogger:
    def __init__(self, lognm='', stream_filter=None, stdout_filter=None, stderr_filter=None ):

        self.loggernm=lognm

        
        self.filters_stream =stream_filter  #type LevelFilter

        self.filters_stdout=stdout_filter

        self.filters_stderr=stderr_filter


        logging.basicConfig(level=logging.NOTSET)
        if self.loggernm =='':
            yLog=logging.getLogger()
        else:
            yLog=logging.getLogger(self.loggernm)

        # yLog.handlers.pop()
        # yLog.propagate=False   #when no handler to handle a log message at current level
        #yLog.setLevel(logging.DEBUG)  # critial,error,warning,info,debug, notset 
        #logging.basicConfig(format='%(asctime)s | %(levelname)s: %(message)s', level=logging.NOTSET)

        yHandler=logging.StreamHandler(sys.stdout) #stdout, so cell output is white  #if stderr, so cell output is red   
        ##log_format='+%(funcName)s\%(lineno)s|%(levelname)s: %(message)s [%(filename)s %(asctime)s]'
        log_format='>%(levelname)s[%(filename)s[L:%(lineno)s[%(funcName)s()[%(message)s [%(asctime)s'
        dt_format= '%m/%d,%I:%M'#  %p'
        yHandler.setFormatter(logging.Formatter(log_format, datefmt=dt_format))
        
        yHandler.setLevel=(logging.INFO) #c no effect 
        # if self.filter_stdout != None : yHandler.addFilter( self.filter_stdout )
        if self.filters_stdout != None : 
            for filter in self.filters_stdout:
                yHandler.addFilter(filter)

        self.log_StringIO=StringIO()

        yHandler1=logging.StreamHandler(self.log_StringIO)          
        ##log_format='~%(funcName)s\%(lineno)s|%(levelname)s: %(message)s [%(filename)s %(asctime)s]'
        log_format='>>%(levelname)s[%(name)s[%(filename)s[%(lineno)s[%(funcName)s[%(message)s [%(asctime)s'
        dt_format= '%m/%d:%I:%M %S'#  %p'
        yHandler1.setFormatter(logging.Formatter(log_format, datefmt=dt_format))   
        
        yHandler1.setLevel=(logging.INFO) #c no effect 
        if self.filters_stream != None : 
            for filter in self.filters_stream:
                yHandler1.addFilter(filter)
    
        if (yLog.hasHandlers()):
            yLog.handlers.clear()  #c logging has its default handle if logging basic config is called 
        yLog.addHandler(yHandler)
        yLog.addHandler(yHandler1)
        
        # not conenvient for in the log calling function info is always lambda
        # b=BTLogger(),   b.w("BTLogger w")
        # not freq used
        self.d=lambda y: yLog.debug(y)
        self.i=lambda y: yLog.info(y)
        self.w=lambda y: yLog.warning(y)
        self.e=lambda y: yLog.error(y)
        self.c=lambda y: yLog.critical(y)

        # start the very first log with datetime
        ###logging.info('logging started at:' + datetime.datetime.now().strftime('%x'))
        logging.info('logging started' + "; level at:" + str(yLog.getEffectiveLevel()))

    def FlushStringIO(self):
        self.log_StringIO.seek(0)
        self.log_StringIO.truncate(0)
        
# %%
# module setup 
yfilter10=(LevelFilter((logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL, )) , FileFilter())
yfilter20=(LevelFilter((logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL,)) , FileFilter())
yfilter30=(LevelFilter((logging.WARNING, logging.ERROR, logging.CRITICAL, )) , FileFilter())
yfilter40=(LevelFilter((logging.ERROR, logging.CRITICAL, )) , FileFilter())
yfilter50=(LevelFilter(( logging.CRITICAL,)) , FileFilter())


# %%
#####################################################################################################
# testing module codes
#####################################################################################################
# always comments out the tlogging() caller when ready for use as module

def tLogging():
        
   
       
       
        cl=BTLogger(lognm=__name__ , stdout_filter=yfilter20, stream_filter=yfilter20)
        ### wks on 4/23 b=BTLogger()  #has to be blank to work 
        ol=BTLogger( stdout_filter=yfilter20, stream_filter=yfilter20)

        lgd("lgd")
        lgi("lgi")
        lge("lge")
        lgw("lgw")
        lgc("lgc")
        logging.critical("logging.critical")


        ol.w("BTLogger w OL")
        cl.w("BTLogger w cL")  #works, but not popular


#%%
#import logging
def tLogging1():
    l=logging.getLogger(__name__)
    l.warning("warning with l")
    logging.warning ("warning with logging")


if __name__ == '__main__':
    tLogging()
    #tLogging1()





# %%
