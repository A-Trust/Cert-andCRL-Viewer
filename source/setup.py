import sys,glob
from distutils.core import setup

# check for win32 support
if sys.platform == 'win32':
    # win32 allows building of executables
    import py2exe

# check for OS X support
if sys.platform == 'darwin':
    import py2app
    pkg_data.append( ('../Frameworks', 
       ['/usr/local/lib/wxPython-unicode-2.5.3.1/lib/libwx_macud-2.5.3.rsrc'])
    )

excludes = [
    'excludes',
    'Tkinter',
    'htmllib',
    'macurl2path',
    'popherlib',
    'cgi',
    'fcntl',
    'OpenSSL',
    'jarray',
    'java.io.IOException',
    'java.io.InterruptedIOException',
    'java.net',
    'javax.comm',
    'readline',
    'sgi',
    'win32com.client',
    'win32com.client.dynamic',
    'win32com.client.makepy',
]

includes = [
    'encodings.*',
    'codecs.*',
#    'httplib',
#    'ftplib',
#    'chunk',
#    'fnmatch',
#    'struct',
]


setup(  name='crlViewer',
        version='0.9',
        description='crlViewer',
        long_description='',
        url='http://labs.a-trust.at',
        author='a-trust',
        author_email='developer@a-trust.at',
        windows=[{"script": "crlViewerApp.py",
                  #"icon_resources": [(1, "imgs\Logo2.ico")] 
                  }],
        #console=["crlViewerApp.py"],
        app = ['crlViewerApp.py'],
        scripts=['crlViewerApp.py',],
#        options={"py2exe": {"packages": ["encodings", 'rdflib'], },
        options={"py2exe": {"excludes": excludes,
                            "includes": includes, 
                            "optimize": 2,
                            "bundle_files": 1,
                          
               },}
        #data_files = [
        #('imgs', glob.glob("imgs/log*.png")+glob.glob("imgs/bur*.gif")),
        #('i18n_/de/LC_MESSAGES', glob.glob("i18n_/de/LC_MESSAGES/*.mo")),
        #]
    )

