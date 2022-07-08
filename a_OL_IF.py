## OL_IF == Outlook Interface 
##
#####https://stackoverflow.com/questions/52889704/python-win32com-excel-com-model-started-generating-errors
### print(win32com.__gen_path__) #to find the win32com dir and delete it if there is error about 
### or try this: python -m win32com.client.makepy "Excel.Application" or 'Outlook.Application"

# %%
## imports
from email.headerregistry import Address
from attr import NOTHING
from numpy import empty
from sqlalchemy import null
import win32com.client as win32
from win32com.client import constants as C
import datetime 
import time
from dateutil import tz 
from a_Stock_IF import Stock
import a_utils
import a_TDA_IF

import logging
from logging import debug    as lgd   #10
from logging import info     as lgi   #20
from logging import warning  as lgw   #30
from logging import error    as lge   #40
from logging import critical as lgc   #50 
import a_Settings

# yfilter=(a_utils.LevelFilter((logging.INFO, logging.CRITICAL, logging.DEBUG)) , a_utils.LevelFilter((logging.INFO, logging.CRITICAL, logging.DEBUG)))
# yfilter2=(a_utils.LevelFilter((logging.INFO, logging.DEBUG, logging.ERROR)) , a_utils.FileFilter())
# yfilter3=(a_utils.LevelFilter((logging.INFO,)) , a_utils.FileFilter())
# yfilter1=a_utils.LevelFilter((logging.WARNING, logging.INFO, logging.DEBUG))  # have to have two items , even if the same
# #global lg
# lg=a_utils.BTLogger( stdout_filter=yfilter2, stream_filter=yfilter3)

# %%
class OLI_Stock :
    def __init__(self, OLI, Logging_Log):
        self.Stock = None
        self.OLI=OLI
        self.lg = Logging_Log 

        #self.Inspector= self.OLI.GetInspector
        #self.WDoc =self.Inspector.WordEditor

    # def __init__(self, OLI):
    #     self.Stock = None
    #     self.OLI=OLI
    #     #self.lg = Logging_Log 

    def InitStock (self):

    
        # initialize a stock 
        self.Stock=Stock( self.Get_OLI_UsrP_Value('Sec', 'QQQ'))
      

        self.Stock.HistEndDate=a_utils.epoch_date_stamp()
        self.Stock.HistStartDate=a_utils.epoch_from_today( Yr=1, Mo=0, Day=0) 

        
        self.Stock.TA1['Strategies']['SMA']['Params']["State"]= self.Get_OLI_UsrP_Value('SMAState', 
                        self.Stock.TA1['Strategies']['SMA']['Params']["State"])

        self.Stock.TA1['Strategies']['SMA']['Params']["Alert"]= self.Get_OLI_UsrP_Value('SMAAlert', 
                        self.Stock.TA1['Strategies']['SMA']['Params']["Alert"])

        self.Stock.TA1['Strategies']['SMA']["Params"]["Period"]= self.Get_OLI_UsrP_Value('SMAPeriod', 
                        self.Stock.TA1['Strategies']['SMA']['Params']["Period"])  

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
            self.SetOLIUsrProp( "SMAState", self.Stock.TA1['Strategies']['SMA']['Params']['State'] , C.olNumber)
            
            lgd('UpdateOLIFields() OK2')    
            #yOLI.UserProperties.Find("SMAAlert").Value=yStock.SMAAlert
            self.SetOLIUsrProp("SMAAlert", self.Stock.TA1['Strategies']['SMA']['Params']['Alert'], C.olNumber)
            
            
            lgd('UpdateOLIFields() OK3')
            yDT5=a_utils.DateTime2UTC4OLI(self.Stock.TA1['Strategies']['SMA']['Params']['Date'])
            ### yDT5=self.Stock.SMADate # GMT time, 
            lgd(f"yDT5 is {yDT5} ")
            
            if yDT5 != None:
                #self.SetOLIUsrProp("SMADate", yDT5 , C.olDateTime)
                self.SetOLIUsrProp( "SMADate", yDT5 , C.olDateTime)
                self.SetOLIUsrProp("PriceDate", yDT5, C.olDateTime)
                lgd('UpdateOLIFields() OK4')
            

           
           


            lgd('UpdateOLIFields() OK5')
            #yOLI.UserProperties.Find("Price").Value=yStock.Price
            self.SetOLIUsrProp( "Price", self.Stock.Price , C.olCurrency)

            lgd('UpdateOLIFields() OK6')
            #yOLI.UserProperties.Find("Volume").Value=yStock.Volume
            self.SetOLIUsrProp("Volume", self.Stock.Volume , C.olNumber)

            lgd('UpdateOLIFields() OK7') 
            self.SetOLIUsrProp("SMA", self.Stock.SMA , C.olCurrency)
            self.SetOLIUsrProp( "SMAState", self.Stock.TA1['Strategies']['SMA']['Params']["State"] , C.olNumber)
            self.SetOLIUsrProp( "SMAAlert", self.Stock.TA1['Strategies']['SMA']['Params']["Alert"] , C.olNumber)
            self.SetOLIUsrProp( "SMAPeriod", self.Stock.TA1['Strategies']['SMA']["Params"]["Period"], C.olNumber)
            
           

 

            # outlook userproperty stores time in GMT (UTC), when set, it auto change to UTC by know system time is PST 
            # therefore add 6-7 hours ( ahead) 
            sma_dict=str(self.Stock.TA1['Strategies']['SMA']['Params'])
            lgd(f'UpdateOLIFields() OK8 {sma_dict}; ydt5={yDT5}')
            #https://docs.microsoft.com/en-us/office/vba/api/outlook.oluserpropertytype
            #https://docs.microsoft.com/en-us/office/vba/api/outlook.timezone.standardbias

            #tz=self.OLI.Application.TimeZones.CurrentTimeZone
            #lgd('timezone Bias:', tz.Bias, '; daylight b:', tz.DaylightBias, '; std b ;', tz.StandardBiaz ) 

            self.SetOLIUsrProp( "LSUpdate", a_utils.DateTime2UTC4OLI(datetime.datetime.now()) , C.olDateTime)       #last success update date
            ###self.SetOLIUsrProp( "LSUDate", datetime.datetime.now() , C.olDateTime)

            #########################20220607
            ## when run cell returns with "RPC server not found" or other msg NOT from python exception msg 
            ## it is likely the issue is with outlook addin setting of 
            lgd(f'OK9')

            self.OLI.Save()


        except:
            lge(' UpdateOLIFields() not completed ' )




    def UpdateOLI(self, yMsg=''):
        try:
            self.UpdateOLIFields()
            lgd(" field updated")
            yInsp =self.OLI.GetInspector    
            yInsp.Activate()   
            
            # wordeditor is word.document obj : https://docs.microsoft.com/en-us/office/vba/api/word.document
            yWDoc =yInsp.WordEditor 
            #lgd('worddoc id1='+ str(id(yWDoc)))
            
            #!! need this to write inside add tables
            # outlook needs not be open and all happen internally 
            #! need to close the OLI, no need to close the Inspector.close did not work
              
           
            if yWDoc.ProtectionType != C.wdNoProtection: 
                yWDoc.Unprotect()

            
            #2022 05/15  can delete all contents within the worddoc obj
            #https://docs.microsoft.com/en-us/office/vba/api/word.range.delete
            ### yRng.Delete()  # did not delete all 
            # https://docs.microsoft.com/en-us/office/vba/api/word.document.content is a range 
           
            # yWDoc.Content.Select()  # content is a range obj 
            yWDoc.Content.Delete()  
          
           
            ySel=yWDoc.Windows(1).Selection  # get selection obj , https://docs.microsoft.com/en-us/office/vba/api/word.windows
            # selection itself is a word window object https://docs.microsoft.com/en-us/office/vba/api/word.window
            
            #https://docs.microsoft.com/en-us/dotnet/api/microsoft.office.interop.word.range?view=word-pia
            #Each Range object is defined by a starting and ending character position. 
            # Similar to the way bookmarks are used in a document, 
            # Range objects are used to identify specific portions of a document. 
            # However, unlike a bookmark, a Range object only exists 
            # while the programming code that defined it is running. 
            # Range objects are independent of the selection.
            # it is usually not necessary to select text before modifying the text. 
            # Instead, you create a Range object that refers to a specific portion of the document. 
            # For information about defining Range objects
            
            #https://bettersolutions.com/word/paragraphs/vba-range-vs-selection.htm
            # range is a section of text/area in word document 
            # selection is a selected section of text/area
            # selection is for user to pick using GUI 
            # selection object delete() is similar to range delete() 
            # selection delete() need to run selection() first, while range delelte() need not 
            
            #set range to the beginning for the doc
            # not needed if content is delete beforehand
            yRng, n =self.RngOutOfTables(ySel.Range)
            #print('n=', n)

            #move to doc top
            yRng.Move(Unit=C.wdStory, Count=-1) #w, perfectly and one step!  


            #insert content
            yWDoc.Tables.Add(Range=ySel.Range, NumRows=5, NumColumns=1,
                                DefaultTableBehavior=C.wdWord9TableBehavior, AutoFitBehavior=C.wdAutoFitFixed)

            yWDoc.Tables(yWDoc.Tables.Count).Title = "Update"
            yWDoc.Tables(yWDoc.Tables.Count).ID = 123

            #first cell with time and date 
            yTString="Charts for " + self.Stock.Symbol +"; Created at: " + datetime.datetime.now().strftime('%x;  %X') + yMsg
           
            yRng =yWDoc.Characters(1)
            yRng.InsertBefore( yTString )

           
            ################################################
            #print (type(ySel)) 
            #2nd cell with Stock.comment 
            ySel=yWDoc.Windows(1).Selection 
            ySel.Collapse()
            yRng=ySel.Range
            lgd("1 ")
            yRng.Collapse(Direction=C.wdCollapseStart)
            yRng.Move(Unit=C.wdCell, Count=4 )  # when you have single column , this moves to the cell below 
            
            self.Stock.Comment=self.lg.log_StringIO.getvalue()
            ### self.Stock.Comment=logging.log_StringIO.getvalue()
            #lgd("Comment="+ self.Stock.Comment)
            yRng.InsertBefore(self.Stock.Comment)

            ##############################################
            ySel=yWDoc.Windows(1).Selection 
            ySel.Collapse()
            yRng=ySel.Range

            yRng.Collapse(Direction=C.wdCollapseStart)
            yRng.Move(Unit=C.wdCell, Count=3 )
            # file=r'C:\Users\bt\Documents\GitHub\SigmaCodingBTC\TDAAPI\historical_data\a_Debug\GOOG\GOOG_SMA_04_25_21.png'
            self.InsertImage(yRng)
            
            ##################################################
            lgd(" before insert events")
            self.insertEvents(yWDoc)

            # cleanup fields after new content
            #do this after it is copied to \history 
            #w self.OLICleanup()

            lgd("completed")

            
        except: 
            lge(" ! exception ")
           
        finally:
            # yWDoc.Close(SaveChanges=-1)
            # yWDoc.Save()
            yInsp.Close(C.olSave) #nw, no need 
            #self.OLI.Save()   # to call in main loop
            lgd("OLIUpdate finally closed at: ")

    def insertEvents1(self):
        lgd(f" step 0")

    def insertEvents(self, yWDoc):
        try:
            lgd(f" step 0")          
            ySel=yWDoc.Windows(1).Selection 
            ySel.Collapse()
            yRng=ySel.Range

            #https://docs.microsoft.com/en-us/office/vba/api/word.wdunits
            yRng.Collapse(Direction=C.wdCollapseStart)
            yRng.Move(Unit=C.wdCell, Count=1 )
            yRng.InsertAfter("Comment or URL: ")
    
            lgd(f" step 1")
            yDF=self.Stock.HistDF
        
            #lgd("df shape"+ str( yDF.shape))
            #ySec=self.stock.HistDF.Symbol
            yDF1=yDF[yDF["EventLink"].notnull() ]
            
            
            lgd(f" DF count = {len(yDF1)}")

            for i in range(0, len(yDF1)):
                yOLIID=yDF1["EventLink"].values[i]   
                yDT=yDF1["EventDate"].values[i]
                yEvSubj=yDF1["EventSubject"].values[i]
                #from stock.HistDF to excel, EventDate is a datetime object, 
                yDTStr=yDT.strftime("%Y_%m_%d-%H_%M")

                lgd(f"TextToDisplay=<{i}>-{yDTStr}")

                yRng.Collapse(Direction=C.wdCollapseEnd)
                yRng.InsertBreak(C.wdLineBreak)  # https://docs.microsoft.com/en-us/office/vba/api/word.wdbreaktype
                yRng.InsertAfter("New")
                # https://docs.microsoft.com/en-us/office/vba/api/word.hyperlinks.add
                yHL=yWDoc.Hyperlinks.Add(Anchor=yRng, Address=f"Outlook:{yOLIID}", TextToDisplay=f"<{i+1}> {yEvSubj}: {yDTStr} ") 
                    
                
                yRng=yHL.Range
        except:
            lge("failed")
 




    def SetOLIUsrProp(self, Fieldnm, Value, FieldType=1):
        #find field type from here
        # https://docs.microsoft.com/en-us/office/vba/api/outlook.oluserpropertytype
        # C.olCurrency=14, C.olDateTime=5, C.olText=1, C.olNumber=3 

        lgd('SetOLIUsrProp='+ str(Fieldnm) + ', value string=' + str(Value) + ', value tpye =' + str (type(Value)))
        #nu if Value == None:
        #nu    lge('fail to set OL fields, Fieldnm='+ Fieldnm + '; Value type='+ type(Value))
        #nu  return 

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
                            
                            ##file=file+'.png'
                            lgd( 'plt file ='+ str(file))
                            
                           # yRng.Collapse(Direction=C.wdCollapseStart)
                           # yRng.Move(Unit=C.wdLine, Count=1 )        
                           # https://docs.microsoft.com/en-us/office/vba/api/word.inlineshapes.addpicture                    
                            yPic=yRng.InlineShapes.AddPicture(file, True, True)
                            yPic.ScaleHeight=75
                            yPic.ScaleWidth=75

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
        #https://docs.microsoft.com/en-us/office/vba/api/word.range
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

    #so that when the update OLI is copied back to /sec dir, it is not a valid event for next update
    def OLICleanup(self):
        try:
            yDT=datetime.date(2022,7,1)    #w!(2022,7,1,18)  #too old a date for pywin32: fromisoformat("1900-01-01")       #w  datetime.datetime.today()   #nw date(1900,1,1)
            lge(f"1. set date to {yDT}")
            self.OLI.TaskDueDate= yDT  #nw, triggerred except: None, NOTHING, null
            lge(f"1.2.")
            yUP=self.OLI.UserProperties.Find("EventDate")
            lge(f"2. yUProp {type(yUP)}")
            if  yUP is not None:
                yUP.Delete()       #w!, this deletes eventdate not delete() !!        
            
            lge(f"3. set date to {yDT}")
            # self.SetOLIUsrProp("EventDate", a_utils.DateTime2UTC4OLI(datetime.datetime.now()) , C.olDateTime)
            #self.SetOLIUsrProp("EventDate", yDT, C.olDateTime)
            #assign  "None", nothing happened
            #        "NOTHING" , "due date" gets 12/29/1899
            #        "null" , same as "NOTHING"
            #           datetime.datetime.day(4501,1,1), same as NOTHING
            #           "empty", same as NOTHING   
        
            
        except:
            lge("failed")

def OLICleanup1(yOLI):
        try:
            
            ##################
            # as of 6/26 no need to clear Due date since effdate is in use
            #  due date will be used for flagging buy sell signal 
            ##################
            #yDT= datetime.datetime(1990,1,1)            #nw datetime.datetime(1960,1,1)            #nw datetime.datetime.date(2022,7,1) #w datetime.datetime(2022,7,1)  #nw.date(2022,7,1)    #w!(2022,7,1,18)  #nw fromisoformat("1900-01-01")       #w  datetime.datetime.today()   #nw date(1900,1,1)
            #lgw(f"1. set date to {yDT}")
            # yOLI.TaskDueDate=yDT  #nw "None", "null", "empty","" #only accepts datetime obj, not date obj  #nw, triggerred except: None, NOTHING, null
            
            #lgw(f"1.2.")

            yUP=yOLI.UserProperties.Find("EventDate")
            #lgw(f"2. yUProp {type(yUP)}")
            if  yUP is not None:
                yUP.Delete()       #w!, this deletes eventdate not delete() !!        
            
            yUP=yOLI.UserProperties.Find("Effdate")
            #lgw(f"2. yUProp {type(yUP)}")
            if  yUP is not None:
                yUP.Delete()       #w!, this deletes eventdate not delete() !!   

            yUP=yOLI.UserProperties.Find("Update")
            if  yUP is not None:
                yUP.Delete()
                #yOLI.SetOLIUsrPropDir(yOLI,'Update', '',1) 

            #lgw(f"3. set date to {yDT}")
            #self.SetOLIUsrProp("EventDate", a_utils.DateTime2UTC4OLI(datetime.datetime.now()) , C.olDateTime)
            #self.SetOLIUsrProp("EventDate", yDT, C.olDateTime)
            #assign  "None", nothing happened
            #        "NOTHING" , "due date" gets 12/29/1899
            #        "null" , same as "NOTHING"
            #           datetime.datetime.day(4501,1,1), same as NOTHING
            #           "empty", same as NOTHING   
        
            
        except:
            lge("failed")
        

def updateSummaryOLI(yDF, yFolder):
    try:
        

       
    
        yFolder.Items.Sort(Property="[LastModificationTime]", Descending= True ) 
        #only the first entry is use

        sFilter=f"[SEC]='Summary'  " 
        I2=yFolder.Items.Restrict(sFilter)
        lgd(f' I2 len: { I2.Count }')
        yOLI=I2.GetFirst()
        lgd(f' yOLI entryID: {yOLI.EntryID }')

        #init the variable 
        yInsp=None
        
        if yOLI is not null:

            yOLI1=yOLI.Copy()
            yOLI1.Move(yFolder.Folders['History'])

            # base on updateOLI() above
            yInsp =yOLI.GetInspector  
            yInsp.Activate()     
            yWDoc =yInsp.WordEditor 
          

            if yWDoc.ProtectionType != C.wdNoProtection: 
                yWDoc.Unprotect()

            
            yWDoc.Content.Delete()  
            ySel=yWDoc.Windows(1).Selection 
            yRng=ySel.Range

            lgd(f"rng: {type(yRng)}")
            
            yRng.Move(Unit=C.wdStory, Count=-1) #w, perfectly and one step!  
            
           
            

            #Top of table
            yTString=f"Summary table; created at: {datetime.datetime.now().strftime('%x;  %X')}"           
            yRng =yWDoc.Characters(1)
            yRng.InsertBefore( yTString )
          
            yRng.Collapse(Direction=C.wdCollapseEnd)

            #insert table
            yWDoc.Tables.Add(Range=yRng, NumRows=len(yDF), NumColumns=3,
                                DefaultTableBehavior=C.wdWord9TableBehavior, AutoFitBehavior=C.wdAutoFitFixed)

            yWDTbl=yWDoc.Tables(yWDoc.Tables.Count)
            yWDTbl.Title = "Summary"
            yWDTbl.ID = 123

            lgw(f" yDF len : {len(yDF)};  ")
            #ignore the first row as the template setter 
            yDF2=yDF.loc[yDF.index >0 ]

            yDF1=yDF2.sort_values('Sort', ascending=False)
            yDF1.reset_index(drop=True, inplace=True)
            a_utils.DF2CSV(yDF1, a_Settings.URL_debug_data_path, "SummaryDF")

            lgw(f'summary DF shape { yDF1.shape}')
            for i in range(0, len(yDF1)):
                
                lgd(f" cell [{i},1 ] is {yDF1['Symbol'].iloc[i]} ")
                ##########################################
                #https://docs.microsoft.com/en-us/office/vba/api/word.cell
                yRng=yWDTbl.Cell(i,2).Range

                #lgw(f'yRng is a range 1')
                #yRng.Collapse(Direction=C.wdCollapseStart)
                yRng.Text=f"{yDF1['Symbol'].iloc[i]}"
                
                #lgw(f'yRng is a range 2')
                yHL=yWDoc.Hyperlinks.Add(Anchor=yRng, Address=f"Outlook:{yDF1['Link2OLI'].iloc[i]}", TextToDisplay=f"{yDF1['Symbol'].iloc[i] } ")

                yString=f"LSUpdate:{yDF1['LSUpdate'].iloc[i]}   ;Price Date:{yDF1['PriceDate'].iloc[i]} ; Close: {yDF1['Close'].iloc[i]} ; Volume: {yDF1['Volume'].iloc[i]} "    

                yRng=yHL.Range
                yRng.Collapse(Direction=C.wdCollapseEnd)
                yRng.InsertBreak(C.wdLineBreak)  # https://docs.microsoft.com/en-us/office/vba/api/word.wdbreaktype
                yRng.InsertAfter(f"{yString}")

                                
                ########################################
                yRng=yWDTbl.Cell(i,1).Range
                yRng.Collapse(Direction=C.wdCollapseStart)
                yFPth=yDF1['Link2Plot'].iloc[i]

                lgd(f" yFilePath : {yFPth} ")
                yPic=yRng.InlineShapes.AddPicture(yFPth, True, True)
                yPic.ScaleHeight=75
                yPic.ScaleWidth=75

                ########################################
                yRng=yWDTbl.Cell(i,3).Range
                yRng.Collapse(Direction=C.wdCollapseStart)
                yString=f"Flags:{yDF1['Flag'].iloc[i]} ; cost: {yDF1['Cost'].iloc[i]} ; Shares: {yDF1['Shares'].iloc[i]} "    

                yRng.Text=f"{yString}"


            yInsp.Close(C.olSave)

    except:
        lge("failed")    
    finally:
        a=1

def SetOLIUsrPropDir(yOLI, Fieldnm, Value, FieldType=1):
        #find field type from here
        # https://docs.microsoft.com/en-us/office/vba/api/outlook.oluserpropertytype
        # C.olCurrency=14, C.olDateTime=5, C.olText=1, C.olNumber=3 

        lgd('SetOLIUsrProp='+ str(Fieldnm) + ', value string=' + str(Value) + ', value tpye =' + str (type(Value)))
        #nu if Value == None:
        #nu    lge('fail to set OL fields, Fieldnm='+ Fieldnm + '; Value type='+ type(Value))
        #nu  return 

        if yOLI.UserProperties.Find(Fieldnm) == None:
            try:
                yOLI.UserProperties.Add(Fieldnm, FieldType)
                yOLI.UserProperties.Find(Fieldnm).Value=Value
               # print ("ppp", 'SetOLIUserProp() ', Fieldnm, ',' , Value,', added')
            except:
                lge('ppp SetOLIUserProp() fieldnm= ' + str (Fieldnm)  + ', Value= ' + str (Value) + ' add failed')
        else:
            #nw OLItem.UserProperties.Find(Fieldnm).Value=Value
            try: 
                yPA= yOLI.PropertyAccessor
                yProp=r"http://schemas.microsoft.com/mapi/string/{00020329-0000-0000-C000-000000000046}/" + Fieldnm
                yPA.SetProperty(yProp,Value)

                # print  ('ppp SetOLIUserProp() ', Fieldnm, ',' , Value ,', accessor done')
            except:             
                lge ('ppp SetOLIUserProp() '+ str(Fieldnm) + ',' + str(Value) + '  accessor failed ')

      
        return
#########################################################################

# %%
# testing module functiions
# https://docs.python.org/3/library/datetime.html#date-objects

def ltest1():
    dtobj1=a_utils.DateTime2UTC4OLI(datetime.datetime.now()) 
    print( "utc now is ", dtobj1.strftime("%Y_%m_%d-%H_%M"), "CA now is ", datetime.datetime.now().strftime("%Y_%m_%d-%H_%M") )
    # utc now is  2022_05_09-02_47 CA now is  2022_05_08-19_47

if __name__ =='__main__':
    a=1
    ltest1()
   

# %%
