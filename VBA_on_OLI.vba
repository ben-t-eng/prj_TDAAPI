    
Sub a_SortByColumn5()
Dim yTbl
wdNoProtection = -1
'2022 0710

If TypeName(ActiveWindow) = "Inspector" Then
      
      
    If ActiveInspector.IsWordMail And ActiveInspector.EditorType = olEditorWord Then
    
    'make it in edit mode in one click
    If Not ActiveInspector.WordEditor.ProtectionType = wdNoProtection Then
        ActiveInspector.CommandBars.ExecuteMso ("EditMessage")
    End If
    
    With ActiveInspector.WordEditor.Application.ActiveDocument
         Set yTbl = .Tables(1)
         yDoc = ActiveInspector.WordEditor.Application.ActiveDocument
         
         ySort = 0
         Msg = "table sort by column 5, click yes in reversed order"
         If MsgBox(Msg, vbYesNo) = vbYes Then
            ySort = 1
         End If
         
         yTbl.Sort ExcludeHeader:=True, FieldNumber:="Column 5", SortOrder:=ySort
        
    End With
    End If
Else
    MsgBox ("Valid only inside an OL inspector window")
End If



End Sub

Sub a_SortByColumn4()
Dim yTbl
wdNoProtection = -1
    
If TypeName(ActiveWindow) = "Inspector" Then
      
      
    If ActiveInspector.IsWordMail And ActiveInspector.EditorType = olEditorWord Then
    
    'make it in edit mode in one click
    If Not ActiveInspector.WordEditor.ProtectionType = wdNoProtection Then
        ActiveInspector.CommandBars.ExecuteMso ("EditMessage")
    End If
    
    With ActiveInspector.WordEditor.Application.ActiveDocument
         Set yTbl = .Tables(1)
         yDoc = ActiveInspector.WordEditor.Application.ActiveDocument
         
         ySort = 0
         Msg = "table sort by column 4, click yes in reversed order"
         If MsgBox(Msg, vbYesNo) = vbYes Then
            ySort = 1
         End If
         
         yTbl.Sort ExcludeHeader:=True, FieldNumber:="Column 4", SortOrder:=ySort
        
    End With
    End If
Else
    MsgBox ("Valid only inside an OL inspector window")
End If



End Sub

Sub a_SortByColumnSelect()

Dim yTbl
wdNoProtection = -1
    
If TypeName(ActiveWindow) = "Inspector" Then
      
      
    If ActiveInspector.IsWordMail And ActiveInspector.EditorType = olEditorWord Then
    
    'make it in edit mode in one click
    If Not ActiveInspector.WordEditor.ProtectionType = wdNoProtection Then
        ActiveInspector.CommandBars.ExecuteMso ("EditMessage")
    End If
    
    With ActiveInspector.WordEditor.Application.ActiveDocument
         Set yTbl = .Tables(1)
         yDoc = ActiveInspector.WordEditor.Application.ActiveDocument
         
         
         Msg = "Please enter number 1 to n to select which column to be sorted"
         yColumn = InputBox(Msg)
         If Not IsNumeric(yColumn) Then yColumn = 4
         If yColumn > 5 Or yColumn < 1 Then yColumn = 4
         
         ySort = 1
         Msg = "Table will be sorted by column " & yColumn & ", click [No] to reverse order"
         If MsgBox(Msg, vbYesNo) = vbYes Then
            ySort = 0
         End If
         
         yTbl.Sort ExcludeHeader:=True, FieldNumber:="Column " & yColumn, SortOrder:=ySort
    End With
    End If
Else
    MsgBox ("Valid only inside an OL inspector window")
End If
End Sub



Sub SortByColumn45()
Dim yTbl
wdNoProtection = -1
    

    
    With ActiveInspector.WordEditor.Application.ActiveDocument
         Set yTbl = .Tables(1)
         yDoc = ActiveInspector.WordEditor.Application.ActiveDocument
        
         
            MsgBox "table " & yTbl.Title & " by column 45"
            yTbl.Sort ExcludeHeader:=True, FieldNumber:="Column 5", SortOrder:=0
        
    End With
  


End Sub
