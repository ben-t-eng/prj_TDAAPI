#%% testing datetime solution
import time
import datetime
from dateutil import tz 

#%%
DateTime=datetime.datetime.now()
localDateTime=DateTime.astimezone()  # add tz info to DT object
localTZinfo=localDateTime.tzinfo        # get tzinfo obj 
    
#lgd('DateTime2UTC(): Local timezone name===', localTZinfo.tzname(localDateTime) )
TimeDelta=localTZinfo.utcoffset(localDateTime)
 
UTCDT= localDateTime   +TimeDelta
 
#localTZinfo
#TimeDelta
UTCDT


# %% 
# checking time zone
yDT=datetime.datetime.now()


lTmStamp=yDT.timestamp()*1000 

#4/07/2022 5:00 from TDA to excel
lTmStamp= 1649394000000 #1649307600000 

lDT = datetime.datetime.fromtimestamp(int(lTmStamp)/1000)
print ( lDT)
localTZinfo=lDT.astimezone().tzinfo
TimeDelta=localTZinfo.utcoffset(localDateTime)

print ( lDT -TimeDelta)
print ( lDT +TimeDelta)
# %%
