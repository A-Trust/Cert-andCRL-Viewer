import os
imgs=[  "Logo_Small",
        "cert",
    ]
#strbasecmd="c:\Python24\Lib\site-packages\wx-2.5.3-msw-unicode\wx\tools\img2py -u -a -n folder folder.png folder_img.py"

strOut="images.py"

try:
    os.unlink(strOut)
except:
    pass
f=open(strOut,"wt")
f.write("from wx import BitmapFromImage, ImageFromStream\n")
f.write("import cStringIO\n")
f.write("#import zlib\n")
f.write("\n\n")
f.close()

strbasecmd= r"d:\Python24\Lib\site-packages\wx-2.6-msw-unicode\wx\tools\img2py.py -u -a -n "
for i in imgs:
#    cmd=strbasecmd+i+" imgs\\"+i+".png "+strOut
    cmd=strbasecmd+i+" "+i+".png "+strOut
    print cmd
    i,a=os.popen4(cmd)
    err=a.read()
    print err
    i.close()
    a.close()
