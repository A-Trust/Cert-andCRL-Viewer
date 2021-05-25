#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

import wx
import os,sys
from pisces import asn1
from utils import Str2Unicode, bin2hex, UTC2LocalTime, UTC2GMT
from myListCtrl import myListCtrl
import Images
import locale

encoding = locale.getpreferredencoding()


class ParseCRLException:
    def __init__(self,msg):
        self.msg = msg

    def __str__(self):
        # Convert the exception to a string
        return ("Error: %s" %(self.msg))


Oid2Name={"1.2.840.113549.1.1.1": 'RSA',
          "1.2.840.113549.1.1.2": 'md2RSA',
          "1.2.840.113549.1.1.3": 'md4RSA',
          "1.2.840.113549.1.1.4": 'md5RSA',
          "1.2.840.113549.1.1.5": 'sha1RSA',
          "1.2.840.113549.1.1.6": 'rsaOAEPEncryptionSET',
          "2.5.4.3" : 'Common Name (CN)',
          "2.5.4.4" : 'Surname (S)',
          "2.5.4.5" : 'Serialnumber',          
          "2.5.4.6" : 'Country Name (C)',
          "2.5.4.10" : 'Organization Name (O)',
          "2.5.4.11" : 'Organizational Unit Name (OU)',
          "2.5.29.20" : 'CRL Number',
          "2.5.29.35" : 'Authority Key Identifier',
          "1.2.840.113549.1.9.1" : 'e-mail Address',
          }  

Oid2shortName={"2.5.4.3" : 'CN',
          "2.5.4.4" : 'S',
          "2.5.4.6" : 'C',
          "2.5.4.10" : 'O',
          "2.5.4.11" : 'OU',
          "1.2.840.113549.1.9.1" : 'e-mail',
          }  

RevokeReasonCode = { "0" : 'unspecified',
                    "1" : 'keyCompromise',
                    "2" : 'cACompromise',
                    "3" : 'affiliationChanged',
                    "4" : 'superseded',
                    "5" : 'cessationOfOperation',
                    "6" : 'certificateHold',
                    "7" : 'removeFromCRL',
                    }
    

class crlViewerFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        
        # begin wxGlade: crlViewerFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, -1)
        self.notebook_3 = wx.Notebook(self.panel_1, -1, style=0)
        self.notebook_3_pane_1 = wx.Panel(self.notebook_3, -1)
        self.bitmap_3 = wx.StaticBitmap(self.notebook_3_pane_1, -1, Images.getIconBitmap())
        self.label_5 = wx.StaticText(self.notebook_3_pane_1, -1, "General Information")
        self.list_General = wx.ListCtrl(self.notebook_3_pane_1, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.txtserial = wx.TextCtrl(self.notebook_3_pane_1, -1, "")
        self.bsearch = wx.Button(self.notebook_3_pane_1, -1, "Search")
        self.list_CRL = myListCtrl(self.notebook_3_pane_1, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.text_Value = wx.TextCtrl(self.notebook_3_pane_1, -1, "", style=wx.TE_MULTILINE|wx.TE_LINEWRAP)
        self.bcpy2file = wx.Button(self.notebook_3_pane_1, -1, "&Copy to File ...")
        self.label_1 = wx.StaticText(self.notebook_3_pane_1, -1, "provided by" )        
        self.bitmap_1 = wx.StaticBitmap(self.notebook_3_pane_1, -1, Images.getLogoBitmap())
        self.OK_Button = wx.Button(self.panel_1, -1, "OK")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        wx.EVT_BUTTON(self, self.OK_Button.GetId(), self.OnOk)
        wx.EVT_LIST_ITEM_SELECTED(self, self.list_General.GetId(), self.OnGeneralSelect)
        wx.EVT_LIST_ITEM_SELECTED(self, self.list_CRL.GetId(), self.OnCRLSelect)
        wx.EVT_BUTTON(self, self.bcpy2file.GetId(), self.btnCopyToFile)
        wx.EVT_BUTTON(self, self.bsearch.GetId(), self.bOnSearch)
        self.revoked_list = {}
    
    def visible(self):
        self.Visible = True
        
    def invisible(self):
        self.Visible = False
        
    def bOnSearch(self, event):
        serial = self.txtserial.GetValue()
        self.serial_search(serial)
    
    def serial_search(self,serial):
        if serial == "" or serial == " ":
            return
        if serial.isdigit() == False:
            err= wx.MessageDialog(None, "The entered serial number ist not a number!", "Error", wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP  )
            err.ShowModal()
            err.Destroy()
            return
        
        index = self.list_CRL.FindItem(-1, serial)
        if -1 == index:
            info= wx.MessageDialog(None, "Your certificate is not revoked! The entered serial number %d ist not in the certificate revocation list!" % int(serial) ,"Information", wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP  )
            info.ShowModal()
            info.Destroy()            
            return
        
        self.list_CRL.SetItemState(index,wx.LIST_STATE_FOCUSED|wx.LIST_STATE_SELECTED ,wx.LIST_STATE_FOCUSED|wx.LIST_STATE_SELECTED)
        self.list_CRL.EnsureVisible(index) 
        

    def btnCopyToFile(self, event):
        strWild="Certificate Revocation List (*.crl)|*.crl|All files (*.*)|*.*"
        dlg=wx.FileDialog(self,"Export Certificate Revocation List",wildcard=strWild,style=wx.HIDE_READONLY|wx.SAVE )
        if dlg.ShowModal() == wx.ID_OK:
            filedest=dlg.GetPath()
            import shutil
            shutil.copyfile(self.filename,filedest)
        dlg.Destroy()
        
        
    def OnOk(self, event): # wxGlade: certViewerFrame.<event_handler>
        self.Destroy()

    def OnGeneralSelect(self,event):
        index=event.m_itemIndex
        #item=self.list_General.GetItem(index,1)
        key=self.list_General.GetItemText(index)
        
        self.text_Value.SetValue( key+":\n"+ self.infoGeneral[index])
        
    def OnCRLSelect(self,event):
        index=event.m_itemIndex
        key=self.list_CRL.GetItemText(index)
        item = self.revoked_list[key]
       
        line = ""
        line += "Serial number (dec)" + ":  " + str(item[0]) + "\n"
        line += "Serial number (hex)" + ":  " + item[1] + "\n"
        line += "Revocation date" + ":  " + str(UTC2LocalTime( item[2] )) + "\n\t(GMT:" + str(UTC2GMT( item[2] ))+")\n"
        line += "Reasoncode" + ":  " + item[3] + "\n"

        self.text_Value.SetValue( line )
    
    def ParseCRL(self,filename):
        self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT ))
        self.filename=filename
        try:
            f = open(self.filename, 'rb')
        except IOError, msg:
            print "Error", msg
            raise ParseCRLException(str(msg))
            return None
        s=f.read()
        f.close()
        ret = self.ParseCRLFromString(s)
        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        return ret

    def ParseCRLFromString(self,stream):
        versioninfo = True
        crl = asn1.parse(stream)
#        print crl
        tbsCrlList = crl[0]
        
        
        self.infoGeneral = {}
       
        ##signatureValue = crl[2]
        
        # Version
        index=self.list_General.GetItemCount()
        index=self.list_General.InsertStringItem(index,"Version")
        if tbsCrlList[0] == 0:
            self.list_General.SetStringItem(index,1,"V1" )
            self.infoGeneral[index] = "V1"
        elif tbsCrlList[0] == 1:
            self.list_General.SetStringItem(index,1,"V2" )
            self.infoGeneral[index] = "V2"
        elif tbsCrlList[0] == 2:
            self.list_General.SetStringItem(index,1,"V3" )
            self.infoGeneral[index] = "V3"
        else:
            self.list_General.SetStringItem(index,1,"V2" )
            self.infoGeneral[index] = "V2"            
            versioninfo = False
        
        
        #issuer
        index=self.list_General.GetItemCount()
        index=self.list_General.InsertStringItem(index,"Issuer".encode(encoding))
        line = ""
        line2 = ""
        
        
        if False == versioninfo:
            crlValue = tbsCrlList[1]
        else:
            crlValue = tbsCrlList[2]
         
        line = u""
        line2 = u""  
        for x in crlValue:
            value = Str2Unicode( str(x[0][1]) )
            try:
                line += str( Oid2shortName[ str(x[0][0]) ] )+" =  "+ value + ";  "
            except:
                line += str(x[0][0])+" =  "+ value + ";  "
                
            try:
                line2 += str( Oid2Name[ str(x[0][0]) ] ) +" =  "+ value + "\n"
            except:
                line2 += str(x[0][0])+" =  "+ value + ";  "
            
        self.list_General.SetStringItem(index,1,line.encode(encoding))
        self.infoGeneral[index] = line2.encode(encoding)
             
        
        #thisUpdate
        if False == versioninfo:
            crlValue = tbsCrlList[2]
        else:
            crlValue = tbsCrlList[3]
            
        index=self.list_General.GetItemCount()
        index=self.list_General.InsertStringItem(index,"Effective update")
        self.list_General.SetStringItem(index,1, UTC2LocalTime(crlValue) + '  (GMT: ' + UTC2GMT(crlValue)+' )' )
        self.infoGeneral[index] = UTC2LocalTime(crlValue) + '\n(GMT: ' + UTC2GMT(crlValue)+' )'

        #next Update
        if False == versioninfo:
            crlValue = tbsCrlList[3]
        else:
            crlValue = tbsCrlList[4]
            
        index=self.list_General.GetItemCount()
        index=self.list_General.InsertStringItem(index,"Next update")
        self.list_General.SetStringItem(index,1, UTC2LocalTime(crlValue) + '  (GMT: ' + UTC2GMT(crlValue)+' )'  )
        self.infoGeneral[index] = UTC2LocalTime(crlValue) + '\n(GMT: ' + UTC2GMT(crlValue)+' )'
        
        #signatureAlgorithmIdentifier1
        signatureAlgorithmIdentifier1 = crl[1]
        index=self.list_General.GetItemCount()
        index=self.list_General.InsertStringItem(index,"Signature algorithm")
        try:
            self.list_General.SetStringItem(index,1,Oid2Name[str(signatureAlgorithmIdentifier1[0])] )
            self.infoGeneral[index] = Oid2Name[str(signatureAlgorithmIdentifier1[0])]
        except:
            self.list_General.SetStringItem(index,1,str(signatureAlgorithmIdentifier1[0]))
            self.infoGeneral[index] = Oid2Name[str(signatureAlgorithmIdentifier1[0])]
        
        try:
            if False == versioninfo:
                revokedCertificates = tbsCrlList[4]
            else:
                revokedCertificates = tbsCrlList[5]
                
            for revoked in revokedCertificates:
                break
        except:
            # kein Inhalt
            pass
        else:
            for revoked in revokedCertificates:
                index=self.list_CRL.GetItemCount()
                index=self.list_CRL.InsertStringItem(index,str(revoked[0]) )
                serialhex = hex(revoked[0])[2:] ## in hex umwandeln und 0x ist wegschneiden
                serialhex = serialhex[:len(serialhex)-1]
                self.list_CRL.SetStringItem(index,1,serialhex )
                self.list_CRL.SetDateTimeItem(index,2,revoked[1])
                reason = ''
                try:
                    reason = ord( asn1.parse( revoked[2][0][1] ) )
                    reason = RevokeReasonCode[ str(reason) ]
                    self.list_CRL.SetStringItem(index,3,reason )
                except:
                    pass

                self.revoked_list[str(revoked[0])]= (revoked[0],serialhex,revoked[1],reason)
        
        
        #extensions

        i=2
        while i <10:
            try:
                if tbsCrlList[i].tag==0: #extension
                    break
            except:
                pass
            i += 1
        
        try:
            if tbsCrlList[i].tag==0: #extension
                extensions=asn1.parse(tbsCrlList[i].val)
                
                for extension in extensions:
                   
                    if str(extension[0]) == "2.5.29.20":
                        #OID "2.5.29.20" = CRL Number                      
                        index = self.list_General.GetItemCount()
                        index = self.list_General.InsertStringItem(index,str( Oid2Name[ str(extension[0]) ] ) )
                        value = str(asn1.parse(str(extension[1])))
                        self.list_General.SetStringItem(index,1, value )
                        self.infoGeneral[index] = value
                        
                    elif str(extension[0]) == "2.5.29.35":
                        #OID "2.5.29.35" = Authority Key Identifier
                        
                        AuthorityKeyIdentifier  = asn1.parse( str(extension[1]) )[0]
                        if AuthorityKeyIdentifier.tag == 0:
                            index = self.list_General.GetItemCount()
                            index = self.list_General.InsertStringItem(index,str( Oid2Name[ str(extension[0]) ] ) )
                            value = str(bin2hex( AuthorityKeyIdentifier.val))
                            self.list_General.SetStringItem(index,1,  value )
                            self.infoGeneral[index] = value
        except:
            pass
        
        self.Refresh()


    def __set_properties(self):
        # begin wxGlade: crlViewerFrame.__set_properties
        self.SetTitle("Certificate Revocation List")
        self.SetSize((600, 700))
        self.list_General.SetSize((470, 120))
        self.list_CRL.SetSize((470, 120))
        self.text_Value.SetSize((470, 70))
        self.label_1.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.bsearch.SetDefault()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: crlViewerFrame.__do_layout
        sizer_12 = wx.BoxSizer(wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(self.bitmap_3, 0, wx.ALL, 3)
        label_3 = wx.StaticText(self.notebook_3_pane_1, -1, "Certificate Revocation List Information")
        label_3.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_6.Add(label_3, 0, wx.RIGHT|wx.TOP|wx.BOTTOM, 3)
        sizer_1.Add(sizer_6, 0, 0, 0)
        sizer_1.Add(self.label_5, 0, wx.ALL, 3)
        sizer_1.Add(self.list_General, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 3)
        label_2_copy_copy = wx.StaticText(self.notebook_3_pane_1, -1, "Certificate Revocation List:")
        sizer_1.Add(label_2_copy_copy, 0, wx.ALL, 3)
        label_6 = wx.StaticText(self.notebook_3_pane_1, -1, "Serialnumber (dec):")
        sizer_7.Add(label_6, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 6)
        sizer_7.Add(self.txtserial, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 6)
        sizer_7.Add(self.bsearch, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 6)
        sizer_1.Add(sizer_7, 0, wx.ALIGN_RIGHT, 0)
        sizer_1.Add(self.list_CRL, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 3)
        label_4 = wx.StaticText(self.notebook_3_pane_1, -1, "Value:".encode(encoding))
        sizer_1.Add(label_4, 0, wx.LEFT|wx.RIGHT|wx.TOP, 3)
        sizer_1.Add(self.text_Value, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 3)
        sizer_5.Add(sizer_1, 1, wx.EXPAND, 0)
        sizer_9.Add(self.bcpy2file, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 12)
        sizer_2.Add(sizer_9, 1, 0, 0)
        sizer_8.Add(self.label_1, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 6)
        sizer_8.Add(self.bitmap_1, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_RIGHT, 6)
        sizer_2.Add(sizer_8, 0, wx.ALIGN_RIGHT, 0)
        sizer_5.Add(sizer_2, 0, wx.EXPAND, 0)
        self.notebook_3_pane_1.SetAutoLayout(True)
        self.notebook_3_pane_1.SetSizer(sizer_5)
        sizer_5.Fit(self.notebook_3_pane_1)
        sizer_5.SetSizeHints(self.notebook_3_pane_1)
        self.notebook_3.AddPage(self.notebook_3_pane_1, "General")
        #sizer_4.Add(wx.NotebookSizer(self.notebook_3), 1, wx.ALL|wx.EXPAND, 3)
        sizer_4.Add(self.notebook_3, 1, wx.ALL|wx.EXPAND, 3)
        sizer_4.Add(self.OK_Button, 0, wx.ALL|wx.ALIGN_RIGHT, 3)
        self.panel_1.SetAutoLayout(True)
        self.panel_1.SetSizer(sizer_4)
        sizer_4.Fit(self.panel_1)
        sizer_4.SetSizeHints(self.panel_1)
        sizer_12.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_12)
        self.Layout()
        # end wxGlade
        self.list_General.InsertColumn(0,"Field",width=150)
        self.list_General.InsertColumn(1,"Value",width=300)
     

# end of class crlViewerFrame


if __name__ == "__main__":
    from crlViewerApp import *
    main()
