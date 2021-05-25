#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

import wx
import os,sys
import gettext
try:
    from wxPython.lib.mixins.listctrl import wxListCtrlAutoWidthMixin, wxColumnSorterMixin, wxListCtrl, wxDefaultPosition, wxDefaultSize
except:
    from wxPython.wx import *
    from wxPython.lib.mixins.listctrl import *
from utils import UTC2LocalTime,UTC2LocalTime_DTOBJ
import locale

encoding = locale.getpreferredencoding()
#
#  I18N
#
basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
localedir = os.path.join(basepath, "I18N")
langid = wx.LANGUAGE_DEFAULT
#langid = wx.LANGUAGE_ENGLISH
#langid = wx.LANGUAGE_GERMAN
# Set locale for wxWidgets
wx.Locale_AddCatalogLookupPathPrefix(localedir)
mylocale = wx.Locale(langid)
domain = "crlViewer"                 # the translation file is crlViewer.mo
##mylocale.AddCatalog(domain) ## removed, because compatibility with wx 2.4
# Set up Python's gettext
mytranslation = gettext.translation(domain, localedir,[mylocale.GetCanonicalName()], fallback = True)
mytranslation.install()
#
#
#


 


class myListCtrl(wxListCtrl, wxListCtrlAutoWidthMixin, wxColumnSorterMixin):
    
    def __init__(self, parent, ID, pos=wxDefaultPosition,size=wxDefaultSize, style=0):
        self.parent = parent
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        self.InsertColumn(0,_("Serial number").encode(encoding),width=80)
        self.InsertColumn(1,_("Serial number hex").encode(encoding),width=100)
        self.InsertColumn(2,_("Revocation date").encode(encoding),width=120)
        self.InsertColumn(3,_("Reasoncode").encode(encoding),width=130)
        
        wxListCtrlAutoWidthMixin.__init__(self)
        #EVT_LIST_COL_CLICK(self,ID,self.OnCol ) 
        wxColumnSorterMixin.__init__(self,4)
        self.itemDataMap ={}
        self._colSortFlag= [False,False,False,False]


    def columnSorter(self,key1,key2):
        col = self._col
        sortFlag = self._colSortFlag[col]
        
        data1 = self.itemDataMap[key1][col]
        data2 = self.itemDataMap[key2][col]
       
        if 0 == col:
            cmpVal = cmp( int(data1) , int(data2) )
        elif 2 == col:
            cmpVal = cmp( data1 , data2 )
        elif 3 == col:
            cmpVal = cmp( data1.lower() , data2.lower() )
        else:
            cmpVal = cmp( data1 , data2 )
        
        if sortFlag:
            return cmpVal
        else:
            return -cmpVal
    
    
    def InsertStringItem(self,index, obj ):
        wxListCtrl.SetItemData(self,index,index)
        self.itemDataMap[index] = {}
        self.itemDataMap[index][0] = obj
        return wxListCtrl.InsertStringItem(self,index,obj)    
    
    def SetStringItem(self,index, col, obj):
        wxListCtrl.SetItemData(self,index,index)
        self.itemDataMap[index][col] = obj
        return wxListCtrl.SetStringItem(self,index,col,obj)
    
    def SetDateTimeItem(self,index,col,obj):
        wxListCtrl.SetItemData(self,index,index)
        self.itemDataMap[index][col] = UTC2LocalTime_DTOBJ(obj)
        return wxListCtrl.SetStringItem(self,index,col, str(UTC2LocalTime(obj)) )        
    
    def GetListCtrl(self):
        return self
    
    def GetColumnSorter(self):
        return self.columnSorter

if __name__ == "__main__":
    from crlViewerApp import *
    main()