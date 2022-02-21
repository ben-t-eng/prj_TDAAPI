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

# yfilter=(a_utils.LevelFilter((logging.INFO, logging.CRITICAL, logging.DEBUG)) , a_utils.LevelFilter((logging.INFO, logging.CRITICAL, logging.DEBUG)))
# yfilter2=(a_utils.LevelFilter((logging.INFO, logging.DEBUG, logging.ERROR)) , a_utils.FileFilter())
# yfilter3=(a_utils.LevelFilter((logging.INFO,)) , a_utils.FileFilter())
# yfilter1=a_utils.LevelFilter((logging.WARNING, logging.INFO, logging.DEBUG))  # have to have two items , even if the same
# #global lg
# lg=a_utils.BTLogger( stdout_filter=yfilter2, stream_filter=yfilter3)

#%%
class OLI_Stock :
    def __init__(self, OLI, Logging_Log):
        self.Stock = None
        self.OLI=OLI
        self.lg = Logging_Log 

        #self.Inspector= self.OLI.GetInspector
        #self.WDoc =self.Inspector.WordEditor


    def InitStock (self):

    
        # initialize a stock 
        self.Stock=Stock( self.Get_OLI_UsrP_Value('Sec', 'QQQ'))
      

        self.Stock.HistEndDate=a_utils.epoch_date_stamp()
        self.Stock.HistStartDate=a_utils.epoch_from_today( Yr=1, Mo=0, Day=0) 

        
        self.Stock.SMAState= self.Get_OLI_UsrP_Value('SMAState', 0)
        self.Stock.SMAAlert=self.Get_OLI_UsrP_Value('SMAAlert', 0)      
        self.Stock.SMADays=self.Get_OLI_UsrP_Value('SMADays', 10)

        lgi('initStock() '+ self.Stock.Symbol + ' done')


    def Get_OLI_UsrP_Value(self, UsrPNm, Default): 
        try:
            Value=self.OLI.UserProperties.Find(UsrPNm).Value
        except:
            Value=Default 
            lgi('Failed to get Outlook user property ' + UsrPNm + ' value, set to ' + str(Default))
            lge('Failed to get Outlook user property ' + UsrPNm + ' value, set to ' + str(Default))
        return Value


    def UpdateOLIFields(self):
        lgd('Updating OLIFields')
        try: 
            #yStock.Comment=yStock.Comment+' UpdateOLIFields() ??? '  + '; '
    
            ## ySymbol =yOLI.UserProperties.Find("Sec").Value
            lgd('UpdateOLIFields() OK1a')

            #yOLI.UserProperties.Find("SMAState").Value=yStock.SMAState
            self.SetOLIUsrProp( "SMAState", self.Stock.SMAState , C.olNumber)
            
            lgd('UpdateOLIFields() OK2')    
            #yOLI.UserProperties.Find("SMAAlert").Value=yStock.SMAAlert
            self.SetOLIUsrProp("SMAAlert", self.Stock.SMAAlert , C.olNumber)
            
            
            lgd('UpdateOLIFields() OK3')
            yDT5=a_utils.DateTime2UTC(self.Stock.SMADate)
            if yDT5 != None:
                self.SetOLIUsrProp("SMADate", yDT5 , C.olDateTime)
                self.SetOLIUsrProp("PriceDate", yDT5, C.olDateTime)
                lgd('UpdateOLIFields() OK4')
            

           
            self.SetOLIUsrProp("SMA", self.Stock.SMA , C.olCurrency)


            lgd('UpdateOLIFields() OK5')
            #yOLI.UserProperties.Find("Price").Value=yStock.Price
            self.SetOLIUsrProp( "Price", self.Stock.Price , C.olCurrency)

            lgd('UpdateOLIFields() OK6')
            #yOLI.UserProperties.Find("Volume").Value=yStock.Volume
            self.SetOLIUsrProp("Volume", self.Stock.Volume , C.olNumber)

            lgd('UpdateOLIFields() OK7')
            self.SetOLIUsrProp( "SMADays", self.Stock.SMADays , C.olNumber)

            self.OLI.Save()
        except:
            lge(' UpdateOLIFields() not completed ' )




    def UpdateOLI(self):
        try:
            self.UpdateOLIFields()
            
            yInsp =self.OLI.GetInspector    
            yWDoc =yInsp.WordEditor
            #lgd('worddoc id1='+ str(id(yWDoc)))

            #!! need this to write inside add tables
            # outlook needs not be open and all happen internally 
            #! need to close the OLI, no need to close the Inspector.close did not work
            yInsp.Activate()     
            
            if yWDoc.ProtectionType != C.wdNoProtection: 
                yWDoc.Unprotect()

            ySel=yWDoc.Windows(1).Selection  # get selection obj 

            #set range to the beginning for the doc
            yRng, n =self.RngOutOfTables(ySel.Range)
            #print('n=', n)

            #move to doc top
            yRng.Move(Unit=C.wdStory, Count=-1) #w, perfectly and one step!  

            #insert content
            yWDoc.Tables.Add(Range=ySel.Range, NumRows=3, NumColumns=1,
                                DefaultTableBehavior=C.wdWord9TableBehavior, AutoFitBehavior=C.wdAutoFitFixed)

            yWDoc.Tables(yWDoc.Tables.Count).Title = "Update"
            yWDoc.Tables(yWDoc.Tables.Count).ID = 123

            #first cell with time and date 
            yTString=datetime.datetime.now().strftime('%x;  %X')

            yRng =yWDoc.Characters(1)
            yRng.InsertBefore( yTString )

            #print (type(ySel)) 
            #2nd cell with Stock.comment 
            
            yRng.Collapse(Direction=C.wdCollapseStart)
            yRng.Move(Unit=C.wdCell, Count=1 )  # when you have single column , this moves to the cell below 
            
            self.Stock.Comment=self.lg.log_StringIO.getvalue()
            #lgd("Comment="+ self.Stock.Comment)

            yRng.InsertBefore(self.Stock.Comment)

            ySel=yWDoc.Windows(1).Selection 
            ySel.Collapse()
            yRng=ySel.Range
            yRng.Collapse(Direction=C.wdCollapseStart)
            yRng.Move(Unit=C.wdCell, Count=1 )
            
           
            # file=r'C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\historical_data\a_Debug\GOOG\GOOG_SMA_04_25_21.png'
           

            self.InsertImage(yRng)

           

            lgi("completed")

            
        except: 
            lge(" ! exception ")
           
        finally:
            
            #yInsp.Close(C.olSave) #nw, no need 
            #self.OLI.Save()   # to call in main loop
            lgd("OLIUpdate finally closed at: ")


    def SetOLIUsrProp(self, Fieldnm, Value, FieldType=1):
        #find field type from here
        # https://docs.microsoft.com/en-us/office/vba/api/outlook.oluserpropertytype
        # C.olCurrency=14, C.olDateTime=5, C.olText=1, C.olNumber=3 

        lgd('SetOLIUsrProp='+ str(Fieldnm) + ', value string=' + str(Value) + ', value tpye =' + str (type(Value)))
        if Value == None:
            lge('fail to set OL fields, Fieldnm='+ Fieldnm + '; Value type='+ type(Value))
            return 

        if self.OLI.UserProperties.Find(Fieldnm) == None:
            try:
                self.OLI.UserProperties.Add(Fieldnm, FieldType)
                self.OLI.UserProperties.Find(Fieldnm).Value=Value
               # print ("ppp", 'SetOLIUserProp() ', Fieldnm, ',' , Value,', added')
            except:
                lge('ppp SetOLIUserProp() fieldnm= ' + str (Fieldnm)  + ', Value= ' + str (Value) + ' add failed')
        else:
            #nw OLItem.UserProperties.Find(Fieldnm).Value=Value
            try: 
                yPA= self.OLI.PropertyAccessor
                yProp=r"http://schemas.microsoft.com/mapi/string/{00020329-0000-0000-C000-000000000046}/" + Fieldnm
                yPA.SetProperty(yProp,Value)

                # print  ('ppp SetOLIUserProp() ', Fieldnm, ',' , Value ,', accessor done')
            except:             
                lge ('ppp SetOLIUserProp() '+ str(Fieldnm) + ',' + str(Value) + '  accessor failed ')

      
        return

    def InsertImage(self, yRng):
                    # iterate over the list:
            lgd("insert imagines")

            lgd('Stratgy = '+str(self.Stock.TA1)) #! lgi can 
            n=0 
            try:
                for yStrategy in self.Stock.TA1['Strategies']:
                        lgd(' Str='+ yStrategy)
                        for file in self.Stock.TA1['Strategies'][yStrategy]['plt_loc']:
                            
                            file=file+'.png'
                            lgd( 'plt file ='+ str(file))
                            
                           # yRng.Collapse(Direction=C.wdCollapseStart)
                           # yRng.Move(Unit=C.wdLine, Count=1 )                            
                            yRng.InlineShapes.AddPicture(file, False, True)
                            
                            n=n+1

                lgd('Inserted '+ str(n) + ' charts')
            except:
                lgd(' Insert chart operation not completed')
           

            return 

    def RngOutOfTables(self, yRng, n=0 ):
        # Recursive routine to get out of nested table in a word doc
        # where is a range/selection within a table
        # https://stackoverflow.com/questions/7226721/how-can-you-get-the-current-table-in-ms-word-vba
        # cursor exist to outside of any table in MS Word
        # n nest level   
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

            yRng,n =self.RngOutOfTables(yRng, n)
        

        return (yRng, n) 

        