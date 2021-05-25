#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

import wx
import gettext
import os,sys,getopt
from crlViewerFrame import crlViewerFrame, ParseCRLException
from utils import ldap2file,http2file
import myEncodings
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
mytranslation.install(unicode=True)
#
#
#

class myApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        self.frame = crlViewerFrame(None, -1,"")
        self.SetTopWindow(self.frame)
        #self.frame.Show()
        return 1

    def SetNewTopFrame(self,newframe):
        self.SetTopWindow(newframe)

    def SetDefaultTopFrame(self):
        self.SetTopWindow(self.frame)
        
    def ParseCRL(self,filename):
        self.frame.ParseCRL(filename)
        
    def Show(self):
        self.frame.Show()
        
    def serial_search(self,serial):
        self.frame.serial_search(serial)
        
#    def OnExit(self):
#        self.Destroy()
# end of class myApp

def printhelp():
    print
    print _("Platform independent Certificate Revocation List Viewer").encoding(encoding)
    print "\t"+_("provided by a.trust (www.a-trust.at)").encoding(encoding)
    print   ""
    print _("start with path to CRL as argument").encoding(encoding)
    print _("start without argument to select a CRL").encoding(encoding)
    
    
def main():
    
    search_serial = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h',['help'])
        for o, a in opts:
            if o in ('-h','--help'):
                printhelp()
                return
            
    except (getopt.error, IOError), msg:
        print _("Error").encode(encoding), msg
        printhelp()
        return    
    
    filename=""
    
    crlViewerApp = myApp(0)
    
    if len(args)==0:
        strWild="Certificate Revocation List (*.crl)|*.crl|All files (*.*)|*.*"
        dlg=wx.FileDialog(None,_("Select a Certificate Revocation List").encode(encoding) ,wildcard=strWild,style=wx.OPEN|wx.FILE_MUST_EXIST|wx.HIDE_READONLY )
        ret = dlg.ShowModal()
        dlg.Destroy()
        if  wx.ID_OK == ret:
            filename=dlg.GetPath()
        else:
            return
    else:
        filename = ""
        
        
        dlg= wx.MessageDialog(None, "Trying to get CRL from LDAP (PORT 389) or HTTP Server (Port 80), please verify that you are connected to the internet.", "Question", wx.OK | wx.CANCEL |  wx.ICON_QUESTION | wx.STAY_ON_TOP  )
        if dlg.ShowModal() == wx.ID_CANCEL:
            dlg.Destroy()
            return
        dlg.Destroy()
        
        if args[0][:4].lower() == 'ldap':
            #LDAP
            filename = ldap2file(args[0],'certificaterevocationlist')
            if None == filename :
                err= wx.MessageDialog(None, "Can't get File from LDAP! Maybe network connection lost.", "Error", wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP  )
                err.ShowModal()
                err.Destroy()
                return
        elif args[0][:4].lower() == 'http':
            #HTTP HTTPS
            filename  = http2file(args[0])
            if None == filename :
                err= wx.MessageDialog(None, "Can't get File from HTTP! Maybe network connection lost.", "Error", wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP  )
                err.ShowModal()
                err.Destroy()
                return
        else:
            filename =args[0]
        
        if len(args) == 2:
            search_serial = args[1]
    
    try:
        crlViewerApp.ParseCRL(filename)
    except ParseCRLException, e:
        message=str(e)
        dlg = wx.MessageDialog(None,message,_('Error').encode(encoding), wx.OK | wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        dlg.Destroy()
    else:
        crlViewerApp.serial_search(search_serial)
        crlViewerApp.Show()
        crlViewerApp.MainLoop()
        
            
if __name__ == "__main__":
    main()
