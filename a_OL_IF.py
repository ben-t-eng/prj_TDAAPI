##
##
#####https://stackoverflow.com/questions/52889704/python-win32com-excel-com-model-started-generating-errors
### print(win32com.__gen_path__) #to find the win32com dir and delete it if there is error about 
### or try this: python -m win32com.client.makepy "Excel.Application" or 'Outlook.Application"


## imports
import win32com.client as win32
from win32com.client import constants as C
import datetime 
import time
from dateutil import tz 
from a_Stock_IF import Stock
import a_utils
import a_TDA_IF

import logging
from logging import debug as lgd
from logging import info as lgi
from logging import error as lge

#%%


#%%
def InitStock (yOLI):

    yAlert=''
    try:
        ySymbol= yOLI.UserProperties.Find("Sec").Value
    except:
        ySymbol = "QQQ"
        yAlert=r'Alert: can\'t get symbol from OLI Sec field; use QQQ instead' 
        
    yStock=Stock(ySymbol)
    yStock.Comment=yStock.Comment+r'\r\n InitStock():'+ yAlert + '; '

    yStock.HistEndDate=a_utils.epoch_date_stamp()
    yStock.HistStartDate=a_utils.epoch_from_today( Yr=1, Mo=0, Day=0) 

    try:
        yStock.SMAState=yOLI.UserProperties.Find("SMAState").Value
    except: 
        yStock.SMAState = 0
        Stock.Comment=yStock.Comment+'SMAState initialized to 0 '  + '; '

    try:
        yStock.SMAAlert=yOLI.UserProperties.Find("SMAAlert").Value
    except: 
        yStock.SMAAlert = 0
        Stock.Comment=yStock.Comment+'SMAAert initialized to 0 '  + '; '
    try:
        yStock.SMADays=yOLI.UserProperties.Find("SMADays").Value
    except: 
        yStock.SMADays = 10
        Stock.Comment=yStock.Comment+'SMADays initialized to 10 '  + '; '


    lgi('initStock() '+ yStock.Symbol + ' done')
    return yStock

#%%
def UpdateOLIFields1(yOLI, yStock):
    lgd('Updating OLIFields')
    try: 
        #yStock.Comment=yStock.Comment+' UpdateOLIFields() ??? '  + '; '
  
        ## ySymbol =yOLI.UserProperties.Find("Sec").Value
        lgd('UpdateOLIFields() OK1a')

        #yOLI.UserProperties.Find("SMAState").Value=yStock.SMAState
        SetOLIUsrProp2(yOLI, "SMAState", yStock.SMAState , C.olNumber)
        
        lgd('UpdateOLIFields() OK2')    
        #yOLI.UserProperties.Find("SMAAlert").Value=yStock.SMAAlert
        SetOLIUsrProp2(yOLI, "SMAAlert", yStock.SMAAlert , C.olNumber)
        
        lgd('UpdateOLIFields() OK3')

        #yOLI.UserProperties.Find("SMADate").Value=a_utils.DateTime2UTC(yStock.SMADate)
        yDT5=a_utils.DateTime2UTC(yStock.SMADate)
        SetOLIUsrProp2(yOLI, "SMADate", yDT5 , C.olDateTime)


        #yOLI.UserProperties.Find("SMA").Value=yStock.SMA
        #print (" SMA=", yStock.SMA)
        SetOLIUsrProp2(yOLI, "SMA", yStock.SMA , C.olCurrency)


        #yOLI.UserProperties.Find("Price").Value=yStock.Price
        SetOLIUsrProp2(yOLI, "Price", yStock.Price , C.olCurrency)

        #yOLI.UserProperties.Find("PriceDate").Value=a_utils.DateTime2UTC(yStock.PriceDate)
        yDT6=a_utils.DateTime2UTC(yStock.PriceDate)
        lgd('yDT6='+ yDT6)
        SetOLIUsrProp2(yOLI, "PriceDate", yDT6, C.olDateTime)

        #yOLI.UserProperties.Find("Volume").Value=yStock.Volume
        SetOLIUsrProp2(yOLI, "Volume", yStock.Volume , C.olNumber)

        SetOLIUsrProp2(yOLI, "SMADays", yStock.SMADays , C.olNumber)
    except:
        lge(' UpdateOLIFields() not completed ' )


#%%
# u
# Recursive routine to get out of nested table in a word doc
# where is a range/selection within a table
# https://stackoverflow.com/questions/7226721/how-can-you-get-the-current-table-in-ms-word-vba
# cursor exist to outside of any table in MS Word
# n nest level 
def RngOutOfTables(yRng, n=0 ):
  
    if yRng.Information(C.wdWithInTable)==True and n < 500 :
        n=n+1 

        yRng.Collapse(Direction=C.wdCollapseStart) 
        yRow=yRng.Information(C.wdEndOfRangeRowNumber)
        yCell=yRng.Information(C.wdEndOfRangeColumnNumber)
        
        if yCell > yRng.Tables(1).Columns.Count: yCell=yRng.Tables(1).Columns.Count # a bug? 

     #   print (' inside table level = ', n)
     #   print (' At Row=', yRow,', Col=',yCell) 

       # print (' Table row=', yRng.Tables(1).Rows.Count,', Col=',yRng.Tables(1).Columns.Count)                  
        #print (' nested level= ', yRng.Tables(1).NestingLevel)
       
        #w yCellRng=yRng.Tables(1).Rows(yRow).Cells(yCell).Range
        yCellRng=yRng.Tables(1).Cell(Row=yRow, Column=yCell).Range
        yCellRng.MoveEnd(Unit=C.wdCharacter, Count=-1)  #remove the last cell ending char

        lgd('Nested in'+str(yRng.Tables(1).NestingLevel) +"; cell("+ str(yRow) +','+ str(yCell) +')='+  str( yCellRng.Text)  )
        #print ("cell(",yRow ,',', yCell,')=')
        yRng.Tables(1).Range.Collapse(Direction=C.wdCollapseStart)

        #yRng.Move(Unit=C.wdCell, Count=-1)  # NotW: cell, row, not working; Wrks: cell,word, character, sentence, wdParagraph,Story 
        #yRng.Move(Unit=C.wdCharacter, Count=+1) # to beyond table end     
        #yRng.Move(Unit=C.wdCharacter, Count=-1) #w to beyond table front will travse cell by cell

       ############################################### 

        mvUnit=C.wdParagraph

        m=yRng.Move(Unit=mvUnit, Count=-1)  # to the top of first level table if it is from inside of the table
        #w2 m=yRng.Move(Unit=C.wdStory, Count=-1)  # to the beginning of the whole doc
        if m==0: 
            m=yRng.Move(Unit=C.wdRow, Count=-1)
            if m==0:
                yRng.InsertBreak(Type=C.wdColumnBreak)
        #################################################


        yRng,n  =RngOutOfTables(yRng, n)
    

    return (yRng, n) 


def UpdateOLI1(yOLI, yStock):

   UpdateOLIFields1(yOLI, yStock )
  
   # get update the item 
   yInsp= yOLI.GetInspector
   yWDoc =yInsp.WordEditor
   #print('worddoc id=', id(yWDoc))
    
   if yWDoc.ProtectionType != C.wdNoProtection: 
       yWDoc.Unprotect()

   ySel=yWDoc.Windows(1).Selection  # get selection obj 

   #set range to the beginning for the doc
   yRng, n =RngOutOfTables(ySel.Range)
   #print('n=', n)

   #move to doc top
   yRng.Move(Unit=C.wdStory, Count=-1) #w, perfectly and one step!  

   #insert content
   yWDoc.Tables.Add(Range=ySel.Range, NumRows=3, NumColumns=1,
                    DefaultTableBehavior=C.wdWord9TableBehavior, AutoFitBehavior=C.wdAutoFitFixed)

   yWDoc.Tables(yWDoc.Tables.Count).Title = "Update"
   yWDoc.Tables(yWDoc.Tables.Count).ID = 123

   #first cell with time and date 
   yTString=datetime.datetime.now().strftime('%x')

   yRng =yWDoc.Characters(1)
   yRng.InsertBefore( yTString )

   #print (type(ySel)) 
   #2nd cell with Stock.comment 
 
   yRng.Collapse(Direction=C.wdCollapseStart)
   yRng.Move(Unit=C.wdCell, Count=1 )  # when you have single column , this moves to the cell below 
   
   yRng.InsertBefore(yStock.Comment)
   #3nd cell for user notes:  
   yRng.Collapse(Direction=C.wdCollapseStart)
   yRng.Move(Unit=C.wdCell, Count=1 ) 

        

   yInsp.Close(C.olSave)  #works, must run to see result 
    #w message.Close(0)
    #w message.Save()


#%%
def SetOLIUsrProp2(yOLI, Fieldnm, Value, FieldType=1):
#find field type from here
# https://docs.microsoft.com/en-us/office/vba/api/outlook.oluserpropertytype
# C.olCurrency=14, C.olDateTime=5, C.olText=1, C.olNumber=3 

    lgd('SetOLIUsrProp='+ Fieldnm+ ','+ Value, ','+FieldType)
    
    if yOLI.UserProperties.Find(Fieldnm) == None:
        try:
            yOLI.UserProperties.Add(Fieldnm, FieldType)
            yOLI.UserProperties.Find(Fieldnm).Value=Value
            lgd ('SetOLIUserProp() '+ Fieldnm+ ',' + Value,', added')
        except:
            lge ('SetOLIUserProp() '+ Fieldnm+ ',' + Value+' add failed')
    else:
        #nw OLItem.UserProperties.Find(Fieldnm).Value=Value
        try: 
            yPA= yOLI.PropertyAccessor
            yProp=r"http://schemas.microsoft.com/mapi/string/{00020329-0000-0000-C000-000000000046}/" + Fieldnm
            yPA.SetProperty(yProp,Value)

            lgd ('SetOLIUserProp() '+ Fieldnm+ ',' + Value+', accessor done')
        except:             
            lge ('SetOLIUserProp() '+ Fieldnm+ ',' + Value+'  accessor failed ')
    return
 