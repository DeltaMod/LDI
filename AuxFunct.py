# -*- coding: utf-8 -*-
"""
Lumerical Data Handling
Created on Tue Aug 18 17:06:05 2020
@author: Vidar Flodgren
Github: https://github.com/DeltaMod
"""

#use this to set current directory without running code: os.chdir(os.path.dirname(sys.argv[0]))
import os
import sys
import time
import h5py
import hdf5storage
import matplotlib
import tkinter as tk
from tkinter.filedialog import askopenfilename

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d #If you want to be able to use projection="3D", then you need this:
import scipy
import numpy as np
from scipy import integrate
from scipy import interpolate
import json
from collections import Counter
import natsort


    
def cprint(String,**kwargs):
    """
    Note that some light colour variations do not work on all terminals! To get light colours on style-inedpendent terminals, you can use ts = bold!
    kwargs:
    
    mt: Message type - a string that defines one from a list of preset message formats. 
        List of acceptable entries: ['err','error','note','warning','caution','wrn','curio','status','stat','custom']. Note: only custom supports further kwargs
    fg: Foreground colour - a string with the full name or abbrviation of a colour to give to the text.
        List of acceptable entries: ['black','k','red','r','green','g','orange','o','blue','b','purple','p','cyan','c','lightgrey','lg',
                                     'darkgrey','dg','lightgreen','lgr','yellow','y','lightblue','lb','pink','pk','lightcyan','lc']
                                    Note that some light colours are accessed using bold style instead of this!
    bg: Background colour - a string with the full name or abbrviation of a colour to highlight text with.
        List of acceptable entries: ['black','k','red','r','green','g','orange','o','blue','b','purple','p','cyan','c','lightgrey','lg']
    ts: Text Style - a string indicating what style to apply to the text. Some do not work as intended.
        List of acceptable entries: ['bold','b','italic','it','underline','ul','strikethrough','st','reverse','rev','disable','db','invisible','inv']
    sc: StartCode - A custom startcode if you want to use specific colours not listed in the code. 
        Note: overwrites any bs/fg inputs, is compatible only with "custom" message type, but supports text style ts kwargs!
    jc: Join character - This is the character that will join the strings in a list together, recommend '\n' or ' ' but anything works 
    cprint also supports lists with different styles and options applied. Use:
        cprint([string1,string2],fg = [fg1,fg2],bg = [bg1,bg2],ts = [ts1,ts2])
    tr: textreturn - returns the escape character strng instead - does not produce a print output!
    """
    
    msgtype   = kwargs.get('mt','custom')
    fg_str    = kwargs.get('fg',None)
    bg_str    = kwargs.get('bg',None)  
    style_str = kwargs.get('ts',None)
    SC_str    = kwargs.get('sc',None)
    jc_str    = kwargs.get('jc',' ')
    tg_bool   = kwargs.get('tg',False)
    
    #We convert all of these to lists to make sure that we can give the software strings or lists without any problems
    if type(String) == str:
        String    = [String]
    
    def ListMatcher(SoL,matchwith):
        if type(SoL) == type(matchwith) == list:
            if len(SoL) != len(matchwith):
                TM = ['' for i in range(len(matchwith))]
                for j in range(len(SoL)):
                    if j<len(matchwith):
                        TM[j] = SoL[j]
                    
                for k in range(len(SoL),len(matchwith)):
                    TM[k] = SoL[-1]
                SoL = TM
                
        elif type(SoL) != type(matchwith):
            if type(SoL) == str:
                SoL = [SoL for i in range(len(matchwith))]
            if SoL == None:
                SoL = [None for i in range(len(matchwith))]
        
        return(SoL)
    msgtype   = ListMatcher(msgtype,String)
    fg_str    = ListMatcher(fg_str,String)
    bg_str    = ListMatcher(bg_str,String)
    style_str = ListMatcher(style_str,String)
    SC_str    = ListMatcher(SC_str,String)
    jc_str    = ListMatcher(jc_str,String) 
  
    reset ='\033[0m'
   
    EXITCODE  = reset
    class ts:
        bold          = b   ='\033[01m'
        italic        = it  = '\33[3m'
        disable       = db  = '\033[02m'
        underline     = ul  = '\033[04m'
        reverse       = rev = '\033[07m'
        strikethrough = st  = '\033[09m'
        invisible     = inv = '\033[08m'
    
    class fg:
        white      =  w  = '\33[37m'
        black      =  k  = '\033[30m'
        red        =  r  = '\033[31m'
        green      =  g  = '\033[32m'
        orange     =  o  = '\033[33m'
        blue       =  b  = '\033[34m'
        purple     =  p  = '\033[35m'
        cyan       =  c  = '\033[36m'
        lightgrey  =  lg = '\033[37m'
        darkgrey   =  dg = '\033[90m'
        lightred   =  lr = '\033[91m'
        lightgreen = lgr = '\033[92m'
        yellow     =  y  = '\033[93m'
        lightblue  =  lb = '\033[94m'
        pink       =  pk = '\033[95m'
        lightcyan  =  lc = '\033[96m'
        
    class bg:
        white     =  w  = '\33[47m'
        black     =  k  = '\033[40m'
        red       =  r  = '\033[41m'
        green     =  g  = '\033[42m'
        orange    =  o  = '\033[43m'
        blue      =  b  = '\033[44m'
        purple    =  p  = '\033[45m'
        cyan      =  c  = '\033[46m'
        lightgrey = lg  = '\033[47m'
    
    #Message preset function
    class mps: 
        err  = error =            fg.red+ts.bold
        note =                    fg.cyan+ts.bold
        wrn = warning = caution = fg.orange+ts.bold
        status = stat =           fg.green+ts.bold
        curio  =                  fg.purple+ts.bold
        frun   = funct =          bg.c+fg.o
    
    PRINTSTR = []
    for i in range(len(String)):
        STARTCODE = ''
        if msgtype[i] == 'custom':    
            
            try: 
                style = getattr(ts,style_str[i])
            except:
                if style_str[i] is not None:
                    cprint(['Attribute ts =',str(style_str[i]),'does not exist - reverting to default value'],mt='err')
                style = ''
            
            try:
                 STARTCODE = STARTCODE + getattr(fg,fg_str[i])
            except:
                if fg_str[i] is not None:
                    cprint(['Attribute fg =',str(fg_str[i]),'does not exist - reverting to default value'],mt='err')
                STARTCODE = STARTCODE 
                
            try:
                 STARTCODE = STARTCODE + getattr(bg,bg_str[i])
            except:
                if bg_str[i] is not None:
                    cprint(['Attribute bg =',str(bg_str[i]),'does not exist - reverting to default value'],mt='err')
                STARTCODE = STARTCODE 
            
            if SC_str[i] is not None:
                STARTCODE = SC_str[i]
            STARTCODE = STARTCODE+style
        else:
            try:
                STARTCODE = getattr(mps,msgtype[i])
            except:
                cprint(['Message preset', 'mt = '+str(msgtype[i]),'does not exist. Printing normal text instead!'],mt = ['wrn','err','wrn'])
   
        PRINTSTR.append(STARTCODE+String[i]+EXITCODE+jc_str[i])
         
    if tg_bool == False:
        print(''.join(PRINTSTR))
    else:
        return(''.join(PRINTSTR))



#%%
def PathSet(filename,**kwargs):
    """"
    p/pt/pathtype in [rel,relative,abs,absolute]
    Note that rel means you input a relative path, and it auto-completes it to be an absolute path, 
    whereas abs means that you input an absolute path!
    """
    ## Setting up the path and pathtype type correctly:  
    kwargdict = {'p':'pathtype','pt':'pathtype','pathtype':'pathtype'}
    class P: 
        pathtype='rel'
        
    for kwarg in kwargs:
        try:
            setattr(P,kwargdict[kwarg], kwargs.get(kwarg,None))
        except:
            cprint(['kwarg =',kwarg,'does not exist!',' Skipping kwarg eval.'],mt = ['wrn','err','wrn','note'])
            
    if P.pathtype not in ['rel','abs']: 
        cprint('pathtype set incorrectly, correcting to \'rel\' and assuming your path is correct',mt='caution')
        P.pathtype = 'rel'
    
    if P.pathtype in ['abs','absolute']:
        WorkDir = ""
        
        
    elif P.pathtype in ['rel','relative']:
        WorkDir = os.getcwd()+'\\'

        
    return(WorkDir+filename)

#%%
def jsonhandler(**kwargs):
    kwargdict = {'f':'filename','fn':'filename','filename':'filename',
                 'd':'data','dat':'data','data':'data',
                 'a':'action','act':'action','action':'action',
                 'p':'pathtype','pt':'pathtype','pathtype':'pathtype'}
    class j:
        pathtype = 'rel'
        pass
        
    for kwarg in kwargs:
        try:
            setattr(j,kwargdict[kwarg], kwargs.get(kwarg,None))
        except:
            cprint(['kwarg =',kwarg,'does not exist!',' Skipping kwarg eval.'],mt = ['wrn','err','wrn','note'])
   
    if hasattr(j,"filename") and hasattr(j,"action") == True:    
        if j.action in ['read','r']:
            with open(j.filename,'r') as fread:
                data = json.load(fread)
                return(data)
            
        elif j.action in ['write','w']:
            try:
                with open(j.filename,'w') as outfile:
                    cprint(['saved',str(j.data),'to',str(outfile)],mt=['note','stat','note','stat'])
                    json.dump(j.data,outfile)
            except:
                cprint('Data does not exist! Remember to enter d/dat/data = dict',mt='err')
    else:
        cprint('No filename given! Cannot read or write to json file!',mt='err')
    
def CUV(**kwargs):
    ACTLIST = ['reset','load']
    action   = kwargs.get('act',None)
    if len(kwargs) == 0:
        action = str(input(cprint(['Please enter one of the following actions',' [', ",".join(ACTLIST),']'],mt=['note','stat'],tg=True)))
        if action not in ['reset','load']:
           cprint('Ignoring command, you did not select a valid entry',mt='err')
    
    
    if action == 'reset':
        cprint('Writing default settings to file',mt='note')
        RFile = os.getcwd()+"\\DataImportSettings.json"
        Default = {'Debug':False,'FileLoad':True,'AltFile':None,'DefaultFile':RFile}
        jsonhandler(f = Default['DefaultFile'],d = Default,a='w')
        return(jsonhandler(f=RFile,a='r'))
       
    if action == 'load':
        root = tk.Tk()
        file_path = askopenfilename()
        tk.Tk.withdraw(root)
        print(file_path)
        
    if action == 'init':
        DefaultFile = os.getcwd()+"\\DataImportSettings.json"
        ddata = jsonhandler(f = DefaultFile,a='r')
        if ddata['AltFile'] is not None:
            try:
                data = jsonhandler(f = ddata['AltFile'],a='r')
                cprint(['Loading user set settings from path = ',ddata['AltFile']],mt=['note','stat'])
                return(data)
            except:
                cprint(['Failed to load alt user settings file, using defaults instead'],mt=['err'])
                return(ddata)
        else:
            cprint(['Initialising with last session user settings'],mt=['note'])
            return(ddata)
        
        return(jsonhandler(f=ddata['D'],a='r'))
    
def Get_FileList(path,**kwargs):
    """
    A function that gives you a list of filenames from a specific folder
    path = path to files. Is relative unless you use kwarg pathtype = 'abs'
    kwargs**:
        pathtype: enum in ['rel','abs'], default = 'rel'. Allows you to manually enter absolute path    
        ext: file extension to look for, use format '.txt'. You can use a list e.g. ['.txt','.mat','.png'] to collect multiple files. Default is all files
        sorting: "alphabetical" or "numeric" sorting, default is "alphabetical"
    """
    #Collecting kwargs
    for kwarg in list(kwargs.keys()):
        if kwarg not in ['pathtype','ext','sorting']:
            cprint('your kwarg = '+kwarg+ ' does not match any kwargs in the code. The code will still run using defaults, but you should check your spelling.',mt='err')
    PT  = kwargs.get('pathtype','rel')
    ext = kwargs.get('ext',None)
    ST  = kwargs.get('sorting',None)  
    
    cprint('=-=-=-=-=-=-=-=-=-=-=- Running: Get_FileList -=-=-=-=-=-=-=-=-=-=-=',mt = 'funct')
    Dpath = PathSet(path,pt=PT)
    #Checking that ST has been selected correctly
    if ST not in [None,'alphabetical','numeric']:
        cprint('sorting was not set correctly, reverting to using alphabetical sorting (no extra sorting)',mt='note')
        ST = None
    
    #Filtering out the intended file types from the filenames
    #First, checking that the format for ext is correct.
    if type(ext) is str and ext.startswith('.') is False:
        ext = '.'+ext
        cprint('Correcting incorrect extension from ext = \''+ext[1:]+ '\' to ext = \''+ext+'\'',mt='caution')
    elif type(ext) is tuple:
        extreplacer = []
        for i in range(len(ext)):
            if ext[i].startswith('.') is False:
                extreplacer.append('.'+ext[i])
                cprint('tuple ext['+str(i)+'] was corrected from ext['+str(i)+'] = \''+ext[i]+'\' to ext['+str(i)+'] = \'.'+ext[i]+'\'',mt='caution')
            else:
                extreplacer.append(ext[i])
        ext = tuple(extreplacer)
        print(ext)
    else:
        ext = None
        cprint('ext must be in string or tuple format - setting ext = None and gathering all files instead',mt='err')
        
    summary = []
    if ext is not None:
        NList = {}
        DList = {}
        summary = ['\nSummary:']
        for ex in ext:
            NList[ex] = [file for file in os.listdir(Dpath) if file.endswith(ex)]
            if ST == 'numeric':
                NList[ex] = natsort.natsorted(NList[ex], key=lambda y: y.lower())
                cprint([ex, ' files were sorted numerically'],fg=['g','c'],ts='b')
            DList[ex] = [Dpath+'\\'+name for name in NList[ex]]
            
        
            DSum = len(DList[ex])
            summary.append(str(DSum) + ' ' + ex + ' files')
                       
    else:
        NList = [file for file in os.listdir(Dpath)]
        if ST == 'numeric':
            NList = natsort.natsorted(NList, key=lambda y: y.lower())
            cprint([ex, ' files were sorted numerically'],fg=['g','c'])
        DList = [Dpath+'\\'+name for name in NList]
    
    cprint(['A total of',str(len(DList)), 'filenames were recovered.']+summary,ts='b',fg=['c','g','c',None,'g'],jc = [' ',' ','\n'])
    
    
    return(DList,NList)

#%%
#We probably only want to only load one matfile at a time, because otherwise we're going to quickly run out of memory!

  
def MatLoader(file,**kwargs):
    cprint('=-=-=-=-=-=-=-=-=-=-=- Running: MatLoader -=-=-=-=-=-=-=-=-=-=-=',mt = 'funct')
    FIELDDICT = {}
    f = h5py.File(file,'r')
    for k, v in f.items():
        FIELDDICT[k] = np.array(v)
    FIELDLIST = list(FIELDDICT.keys()) 
    data = {}
    if '#refs#' in FIELDLIST: 
        FIELDLIST.remove('#refs#')
        cprint(["Scanning fields:"]+FIELDLIST,fg='c',ts='b')
    if len(FIELDLIST) == 1:
        dfields = list(f[FIELDLIST[0]].keys())
        
        for field in dfields:
            data[field] = np.array(f[FIELDLIST[0]][field])
            if len(data[field].shape) == 2 and data[field].shape[0] == 1:
                oldshape    = data[field].shape
                data[field] = data[field][0]
                cprint(['corrected','data['+str(field)+'].shape','from',str(oldshape),'to',str(data[field].shape)],mt=['note','status','note','wrn','note','status'])
    
    
        
    tranconf = 0
    powconf  = 0 
    
    if 'trans' in FIELDLIST[0].lower():
        cprint('Best guess is that you just loaded the data from a Transfer Box analysis group!', mt = 'curio')
        tranconf = 1
    if any(substring in FIELDLIST[0].lower() for substring in ['pow','pabs']):
        cprint('Best guess is that you just loaded the data from a power absorption analysis group!',mt = 'curio')
        powconf = 1
    if [tranconf,powconf] == [1,1]:
        cprint('Naming convention might be strange - you should know better what type of file you loaded...',fg='o')    
    return(data,dfields) 


def AbsPowIntegrator(Data,x,y,z,WL):
    
    """
    "A function that uses a RectBivariateSpline function to determine the total absorbed power from a pabs_adv lumerical file."
    Calculating total power absorption as a power fraction:s
    Lumerical initially gives P_abs in terms of W/m^3, but then converts it by dividing by the source power - which is why the values are seemingly massive. 
    SP   = meshgrid4d(4,x,y,z,sourcepower(f));
    Pabs = Pabs / SP;
    
    If we then look inside the P_abs_tot analysis group script, we can see that this simply becomes an integration over each 2d slice:
    Pabs_integrated = integrate2(Pabs,1:3,x,y,z);
    We could simply export Pabs_tot, but I think we get more control if we do it manually, and we also save data!
    """
    
    P_tot = []
    for i in range(len(WL)):
        BivarSpline = [np.abs(z[0]-z[1])*scipy.interpolate.RectBivariateSpline(y,x,Data[i,k,:,:]).integral(y[0],y[-1],x[0],x[-1]) for k in range(len(z))]

        P_tot.append(np.sum(BivarSpline))
    
    return(P_tot)