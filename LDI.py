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
from tkinter.filedialog import askopenfilename, askdirectory

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d #If you want to be able to use projection="3D", then you need this:
import scipy
import numpy as np
from scipy import integrate
from scipy import interpolate
import json
from collections import Counter
import natsort


def Init_LDI():
    """
    A function that aims to set up the file structure of a new project. Running this function first will create the DataImportSettings.json and populate it with the default settings.
    Then, it will call an "add" command for DataDirectories.json, prompting you to select a data folder. 
    """
    
    #First, check if each of the files exist in your working directory:
    DIS = "DataImportSettings.json"
    Ddir= "DataDirectories.json"
    if os.path.isfile(PathSet(DIS, pt = 'rel')) and os.path.isfile(PathSet(Ddir,pt='rel')) == True:
        cprint(['Comment out your Init_LDI! You already have both',DIS,'and',Ddir],mt = ['wrn','stat','wrn','stat'])
    if os.path.isfile(PathSet(DIS, pt = 'rel')) == False:
        cprint(['Creating',DIS],mt=['curio','stat'])
        CUV(act='reset',pt='rel')
    
    if os.path.isfile(PathSet(Ddir,pt='rel')) == False:
        cprint(['Creating',DIS,'Please also select the first Data folder to append!'],mt=['curio','stat','note'],jc=[' ',':\n ',''])
        DataDir(act='add')
    
    
def KwargEval(fkwargs,kwargdict,**kwargs):
    """
    A short function that handles kwarg assignment and definition using the same kwargdict as before. To preassign values in the kw.class, you use the kwargs at the end
    use: provide the kwargs fed to the function as fkwargs, then give a kwarg dictionary. 
    
    Example:
        
        kw = KwargEval(kwargs,kwargdict,pathtype='rel',co=True,data=None)
        does the same as what used to be in each individual function. Note that this function only has error handling when inputting the command within which this is called.
        Ideally, you'd use this for ALL kwarg assigments to cut down on work needed.
    """
    #create kwarg class 
    class kwclass:
        pass
    
    #This part initialises the "default" values inside of kwclass using **kwargs. If you don't need any defaults, then you can ignore this.
    if len(kwargs)>0:
        for kwarg in kwargs:
            kval = kwargs.get(kwarg,False)
            try:
                setattr(kwclass,kwargdict[kwarg.lower()], kval)
                
            except:
                cprint(['kwarg =',kwarg,'does not exist!',' Skipping kwarg eval.'],mt = ['wrn','err','wrn','note'])
    #Setting the class kwargs from the function kwargs!     
    for kwarg in fkwargs:
        fkval = fkwargs.get(kwarg,False)
        try:
            setattr(kwclass,kwargdict[kwarg.lower()], fkval)
            
        except:
            cprint(['kwarg =',kwarg,'does not exist!',' Skipping kwarg eval.'],mt = ['wrn','err','wrn','note'])
    return(kwclass)

    
def cprint(String,**kwargs):
    """
    WARNING: The format of this script's kwarg importing is severely different from all other functions in this sheet - consider revising to make use instead of the kwargdict and assigning variables through that!
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
    co: console output - a global variable if you want an option to disable console ouput throughout your code!
        list of acceptable entries: [True,False], default: False
    """
    kwargdict = {'mt':'mt','message type':'mt','message':'mt',
                 'fg':'fg', 'foreground':'fg',
                 'bg':'bg', 'background':'bg',
                 'ts':'ts', 'text style':'ts', 'style':'ts',
                 'sc':'sc', 'start code':'sc',
                 'jc':'jc', 'join character':'jc', 'join char':'jc',
                 'tr':'tr', 'text return':'tr', 'return':'tr',
                 'co':'co', 'console':'co','console output':'co'}
    
    kw = KwargEval(kwargs,kwargdict,mt='custom',fg=None,bg=None,ts=None,sc=None,jc=' ',tr=False,co=True)
    
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
    kw.mt    = ListMatcher(kw.mt,String)
    kw.fg    = ListMatcher(kw.fg,String)
    kw.bg    = ListMatcher(kw.bg,String)
    kw.ts    = ListMatcher(kw.ts,String)
    kw.sc    = ListMatcher(kw.sc,String)
    kw.jc    = ListMatcher(kw.jc,String) 
  
    reset ='\033[0m'
   
    EXITCODE  = reset
    #Note: These can eventually be generated from a script - but probably still need manual definition. Consider to replace with KwargEval in the future, but it's fine for now! 
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
        if kw.mt[i] == 'custom':    
            
            try: 
                style = getattr(ts,kw.ts[i])
            except:
                if kw.ts[i] is not None:
                    cprint(['Attribute ts =',str(kw.ts[i]),'does not exist - reverting to default value'],mt='err')
                style = ''
            
            try:
                 STARTCODE = STARTCODE + getattr(fg,kw.fg[i])
            except:
                if kw.fg[i] is not None:
                    cprint(['Attribute fg =',str(kw.fg[i]),'does not exist - reverting to default value'],mt='err')
                STARTCODE = STARTCODE 
                
            try:
                 STARTCODE = STARTCODE + getattr(bg,kw.bg[i])
            except:
                if kw.bg[i] is not None:
                    cprint(['Attribute bg =',str(kw.bg[i]),'does not exist - reverting to default value'],mt='err')
                STARTCODE = STARTCODE 
            
            if kw.sc[i] is not None:
                STARTCODE = kw.sc[i]
            STARTCODE = STARTCODE+style
        else:
            try:
                STARTCODE = getattr(mps,kw.mt[i])
            except:
                cprint(['Message preset', 'mt = '+str(kw.mt[i]),'does not exist. Printing normal text instead!'],mt = ['wrn','err','wrn'])
   
        PRINTSTR.append(STARTCODE+String[i]+EXITCODE+kw.jc[i])
    if kw.co == True:     
        if kw.tr == False:
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
    kw = KwargEval(kwargs, kwargdict,pathtype='rel')
            
    if kw.pathtype not in ['rel','abs']: 
        cprint('pathtype set incorrectly, correcting to \'rel\' and assuming your path is correct',mt='caution')
        kw.pathtype = 'rel'
    
    if kw.pathtype in ['abs','absolute']:
        WorkDir = ""
        
        
    elif kw.pathtype in ['rel','relative']:
        WorkDir = os.getcwd()+'\\'

    if filename == None:
        filename = ''
    return(WorkDir+filename)

#%%
def jsonhandler(**kwargs):
    """
     DESCRIPTION.
     A simple script that handles saving/loading json files from/to python dictionaries. 

    Parameters
    ----------
    **kwargs :
            kwargdict = {'f':'filename','fn':'filename','filename':'filename',
                 'd':'data','dat':'data','data':'data',
                 'a':'action','act':'action','action':'action',
                 'p':'pathtype','pt':'pathtype','pathtype':'pathtype'}

    Returns
    -------
    Depends: If loading, returns the file, if saving - returns nothing

    """
    kwargdict = {'f':'filename','fn':'filename','filename':'filename',
                 'd':'data','dat':'data','data':'data',
                 'a':'action','act':'action','action':'action',
                 'p':'pathtype','pt':'pathtype','pathtype':'pathtype'}
    
    kw = KwargEval(kwargs, kwargdict, pathtype='rel')
   
    if hasattr(kw,"filename") and hasattr(kw,"action") == True:    
        if kw.action in ['read','r']:
            with open(PathSet(kw.filename,pt=kw.pathtype),'r') as fread:
                data = json.load(fread)
                return(data)
            
        elif kw.action in ['write','w']:
            try:
                with open(PathSet(kw.filename,pt=kw.pathtype),'w') as outfile:
                    cprint(['saved',str(kw.data),'to',str(outfile)],mt=['note','stat','note','stat'])
                    json.dump(kw.data,outfile)
            except:
                cprint('Data does not exist! Remember to enter d/dat/data = dict',mt='err')
    else:
        cprint('No filename given! Cannot read or write to json file!',mt='err')

def Rel_Checker(path):
    """
    Simple function that checks if a file location is relative to the working directory, and if so - replaces the file directory with a relative coordinate version.
    Returns: (path,pt). So, relative (path) (if found to be relative), and path type (pt) just in case
    """
    #First, we check if the current working directory is actually correct!
    DIS  = "DataImportSettings.json"
    Ddir = "DataDirectories.json"
    if os.path.isfile(PathSet(DIS, pt = 'rel')) or os.path.isfile(PathSet(Ddir,pt='rel')) == True:
        WorkDir = os.getcwd()+'\\'
        if os.path.isabs(path) == True:
            if WorkDir in path:
                path = path.replace(WorkDir,'')
                pt = 'rel'
            else:
                pt = 'abs'
        else:
            pt = 'rel'
        return(path,pt)
    else:
        cprint(['One of the required ',DIS,' or ',Ddir,' files are missing! Consider running ','Init_LDI()',' again before continuing!'],mt=['wrn','err','wrn','err','wrn','curio','wrn'])

def DataDir(**kwargs):
    """
    Function to handle loading new data from other directories - should be expanded to support an infinitely large list of directories, by appending new data to the file.
    Note: to change currently active data-dir, you need to select a new file in CUV. I'm going to set up a function that allows you to both select a file, and to make a new one! 
    
    What to do here? I'm saving a file with directories, and I'm giving an option to set the save location in a different directory, isn't that a bit much?
    Maybe I should just have the option in CUV to select a new DataDirectories file, and let this one only pull the directory from CUV?
    
    Current implementation:
        UVAR = CUV(act='init') means UVAR now contains all your variables, and to save you would do CUV(d=UVAR,act = 'session'), which keeps all changes and additions you made to UVAR.
        If you want to add a data directory using DataDir, it too will use CUV(act='init') to load the file, but this does not take into account any changes made in UVAR.
        Solution: Add CUV(act='data_dir') to add a new empty .json file with a particular name, or to select a previously created data_dir file, and make that file the new 
        UVAR['Data_Directories_File']. 
        
        How do you make sure that UVAR is updated properly? 
        Current solution is to give a cprint call telling you to load UVAR again if you make this change, or to return the newly edited file with the function...
    """ 
    
    kwargdict = {'a':'act','act':'act','action':'act'}
    
    actdict =   {'a':'add','add':'add','addfile':'add',
                 'd':'delete','del':'delete','delete':'delete',
                 'dupl':'dupes','dupes':'dupes','duplicates':'dupes',
                 'list':'list','lst':'list','show':'list',
                 'load':'load'}
      
    if len(kwargs) == 0:
        
        kw_keys  = np.unique(list(kwargdict.values()))
        act_keys = np.unique(list(actdict.values()))
        act_keydict    = {}
        for i in range(len(act_keys)):    
            act_keydict[i]    = act_keys[i] 
        kwText   = ":".join(['List of Actions']+[str(i)+' : '+ act_keys[i] for i in range(len(act_keys))]+['INPUT SELECTION']).split(':')
        kwjc     = [':\n']+list(np.concatenate([[':']+['\n'] for i in range(int((len(kwText)-1)/2)) ]))+[':']
        kwFull   = np.concatenate([[kwText[i]]+[kwjc[i]] for i in range(len(kwjc))])
        kwmt     = ['note']+['note']+list(np.concatenate([['stat']+['wrn']+['stat']+['stat'] for i in range(len(act_keys)) ]))+['curio']+['curio']
        kwID = input(cprint(kwFull,mt=kwmt,tr=True))
        
        kwargs = {'act':act_keydict[int(kwID)]}
        
        """
        This is the function call that needs to go into CUV later!
        dID  = {input(cprint(['Do you want to set a custom directories file?', '[y/n]:'],mt = ['note','curio'],jc=['\n',''],tr = True)):True}
        
        if dID.get('y',False) == True:
            root = tk.Tk()
            file_path = tk.filedialog.asksaveasfilename(title = 'Select/write filename for your data directories list!',defaultextension='*.*',filetypes=[('json files','*.json'),('All Files','*.*')]).replace('/','\\')    
            tk.Tk.withdraw(root)
            kwargs['dir'] =  file_path
        """
    kw = KwargEval(kwargs, kwargdict, act=False)    
    
    UV_dir = CUV(act='init',co=False)['Data_Directories_File']
    UV_dir,UV_pt = Rel_Checker(UV_dir)
    UV_dir = PathSet(UV_dir,p=UV_pt)
    setattr(kw,'ddir', UV_dir)
    
        
    try:
        kw.act = actdict[kw.act]
    except:
        cprint(['Note that ','kw.act',' = ',str(kw.act),' does not correspond to an action!',' Skipping kwarg eval.'],mt = ['wrn','err','wrn','note'])
        
    #Check if file exists, else write an empty file:
    if os.path.isfile(kw.ddir) == False:
            jsonhandler(f = kw.ddir,d={},pt='abs',a='w')    
    DirDict = jsonhandler(f = kw.ddir,pt='abs', a='r')
    
    if kw.act == 'add':
        root = tk.Tk()
        file_path = askdirectory(title = 'Please select a data directory to append to your data directories list!').replace('/','\\')
        
        tk.Tk.withdraw(root)
        """
        WARNING! askdirectory gives out the wrong format 
        """
        DirDict[str(1+len(DirDict))] = file_path
        if file_path != '':
            jsonhandler(f = kw.ddir,d=DirDict,pt='abs', a='w')
        else:
            cprint('No file selected, aborting!',mt='err')

    def NewDict(Dict):
        NewDict  = {}
        if type(Dict) == dict:
            Dict = list(Dict.items())
        elif type(Dict) == list:
            pass
            
        for i in range(len(Dict)):
            NewDict[i]  = Dict[i][1]
        return(NewDict)
    
    if kw.act == 'delete':
        listdel  = ['Select a data directory to delete:\n']
        cplist   = ['note'] 
        DDI = list(DirDict.items())
        for i in range(len(DDI)):
            cplist = cplist + ['wrn','note','stat','stat']
            listdel = listdel+ [str(i),' : ',DDI[i][1], '\n']
        cplist = cplist + ['curio']
        listdel = listdel+['Enter number here: ']
        
        IPT = cprint(listdel,mt=cplist,jc='',tr=True)
        index = input(IPT)
        try:
            index = int(index)
        except:
            cprint('Non integer string entered! No fields will be deleted!',mt='err')
        if type(index) == int:
            DirDict.pop(DDI[index][0])
            DirDict = NewDict(DirDict)
                
            jsonhandler(f = kw.ddir,d=DirDict,pt='abs', a='w')
            
            cprint(['Deleted ', '{'+str(DDI[index][0]),' : ',DDI[index][1],'}', ' from directory list file'],mt = ['note','wrn','note','stat','wrn','note'])
            
    if kw.act == 'dupes':
        DDK = list(DirDict.keys())
        DDI = list(DirDict.values())
        UNQ = np.unique(DDI)
        if len(DDI) == len(UNQ):
            cprint('No duplicates found!',mt='note')
        else:
            dupeID = []
            for unique in UNQ:
                hits = [i for i,val in enumerate(DDI) if val == unique]

                if len(hits) > 1:
                    dupeID += hits[1:]
                    
            print(DirDict)
            for dID in dupeID:
                cprint(['Deleting', '{',DDK[dID], ':',DDI[dID],'}','from',kw.ddir],mt = ['note','wrn','curio','wrn','curio','wrn','note','stat'],jc=' ')
                DirDict.pop(DDK[dID])
                
            cprint(['A total of','[',str(len(dupeID)),']','dupes were deleted.'],mt = ['note','wrn','curio','wrn','note'])
            DirDict = NewDict(DirDict)
            jsonhandler(f = kw.ddir,d=DirDict,pt='abs', a='w')
            
        
    if kw.act == 'list':
        listshow  = ['List of currently saved directories:\n']
        cplist   = ['note'] 
        DDI = list(DirDict.items())
        for i in range(len(DDI)):
            cplist = cplist + ['wrn','note','stat','stat']
            listshow = listshow+ [str(i),' : ',DDI[i][1], '\n']
        cplist = cplist
        cprint(listshow,mt=cplist)
        
    if kw.act == 'load':
        return(DirDict)

        
def MultChoiceCom(**kwargs):
    pass
    
            
    
def CUV(**kwargs):
    """
    Change_User_Variables -- or CUV -- is a function used to save and load user defined variables at the start, and then at the end, of any session.
    Parameters
    ----------
    **kwargs : 
        [act,action,a]              : 
            ['reset','r','res'] - fully replaces the current DataImportSettings.json default file with default settings. This action cannot be undone
            ['load','l']        - loads a specific file. This function opens up a file dialog for selection, so you don't need to add anything else. This also saves the location to Aux_File.
            ['init','i','initialise'] - initialises your file with the current DataImportSettings. It will load Aux_File if the field is not None
            ['sesh','save session','session'] - requires a data kwarg field with a dictionary listed. It will accept ANY dictionary, and save this to the currently active DataImportSettings file (or Aux_File, if loaded)
            ['ddir','data dir','directories'] - will allow you to select a new data directories file. If the file does not exist, you can save it as a new file by writing a new name for it. 
            
        [co, console, console out]  = Select if console output is set to [True/False]
        [path, pathtype, pt]        = Choose path type preference ['rel','abs']. Selecting 'rel' will save the directory of selected files in using a relative address, but only if it can! It the start of the address does not match the current working directory, absolute address will be used automatically.
        [data, dat, d]              = Specify DataImportSettings data <type: Dict>. Must be included in act='sesh' and 'save' (when implemented), but is ignored otherwise. 

    Returns 
    -------
    Dictionary data saved to DataImportSettings.json or Aux_File indicated within DataImportSettings.json!

    """
    kwargdict = {'act':'act','action':'act','a':'act',
                 'co':'co','console':'co','console out':'console',
                 'path':'pathtype','pathtype':'pathtype','pt':'pathtype',
                 'data':'data','dat':'data','d':'data'}
    
    actdict = {'reset':'reset','r':'reset','res':'reset',
               'l':'load','load':'load',
               'i':'init','init':'init','initialise':'init',
               'sesh':'session','save session':'session','session':'session',
               'ddir':'ddir','data dir':'ddir','directories':'ddir'}
    
    ACTLIST = list(np.unique(list(actdict.values())))
    kw =  KwargEval(kwargs,kwargdict,pathtype='rel',co=True,data=None,act=None)
    if len(kwargs) == 0:
        kw.act = str(input(cprint(['Please enter one of the following actions',' [', ",".join(ACTLIST),']'],mt=['note','stat'],tr=True)))
        if kw.act not in ['reset','load']:
           cprint('Ignoring command, you did not select a valid entry',mt='err',co=kw.co)
           
    try:
        kw.act = actdict[kw.act]
    except:
        cprint(['Note that','kw.act = ',str(kw.act),' does not correspond to an action!',' Skipping kwarg eval.'],mt = ['wrn','err','wrn','note'])
    
   
    #list all acceptable "get/set" inputs - consider using .lower() in the future to remove duplicates/case sensitivity - I think, however, we won't do this! 
    #Instead, import to variable using init or load - change that variable - then save using session.
    getdict = {'debug':'Debug','Debug':'Debug',
               'FL':'File_Load','File_Load':'File_Load','fileload':'File_Load','file_load':'File_Load',
               'DF':'Default_File','default':'Default_File','default_file':'Default_File','Default_File':'Default_File',
               'DDF':'Data_Directories_File','data_directories_file':'Data_Directories_File','data_directory':'Data_Directories_File','ddf':'Data_Directories_File',
               'console':'Console_Output','CO':'Console_Output','Console_Output':'Console_Output',
               'txt':'txt_import','text_import':'txt_import','TI':'txt_import'}
    
    
    
    #Give default filename and try to load default data
    RFile = "DataImportSettings.json"
    try:
        ddata =  jsonhandler(f = RFile,pt=kw.pathtype,a='r')
    except:
        cprint('You don\'t have any default data! Run Init_LDI() or use CUV(act=\'reset\') to reset to default!',mt='err')

    
    #We make sure to check if we have provided data! If we have, we will check ddata['Alt_File'] and write to the correct file.
    if kw.data != None:
        if ddata['Alt_File'] !=None:
            Target_File = ddata['Alt_File']
            
        else:
            Target_File = RFile
    if kw.act == 'reset':
        print(kw.pathtype)
        cprint('Writing default settings to file',mt='note',co=kw.co)
        Default = {"Debug": True, "File_Load": True, "Alt_File": None, "Default_File": RFile,"Data_Directories_File":"DataDirectories.json", "Console_Output": True, "txt_import": True}    
        jsonhandler(f = Default['Default_File'],pt=kw.pathtype,d = Default,a='w')
        return(jsonhandler(f=RFile,pt=kw.pathtype,a='r'))
          
    if kw.data == None:
        kw.data = jsonhandler(f = RFile ,pt=kw.pathtype,a='r')
        
        if kw.data['Alt_File'] is not None:
            Target_File = kw.data['Alt_File']
            kw.data = jsonhandler(f = kw.data['Alt_File'] ,pt=kw.pathtype,a='r')
        else:
            Target_File  = RFile
    

    
    if kw.act == 'session':
            try:
                cprint(['Saving user set settings to path = ',Target_File],mt=['note','stat'],co=kw.co)
                jsonhandler(f = Target_File,pt=kw.pathtype, d = kw.data, a='w')
                
            except:
                cprint(['Alt_File failed, setting user set settings to path = ',ddata['Default_File']],mt=['wrn','stat'],co=kw.co)
                jsonhandler(f = RFile,pt=kw.pathtype, d = kw.data, a='w')

       
    if kw.act == 'load':
        root = tk.Tk()
        file_path = askopenfilename(title = 'Select a settings file',filetypes=[('json files','*.json'),('All Files','*.*')]).replace('/','\\')    
        tk.Tk.withdraw(root)
        file_path,kw.pathtype = Rel_Checker(file_path) 
        if file_path != "":
            kw.data = jsonhandler(f = file_path,pt=kw.pathtype, a='r')
            if ddata['Alt_File'] == None:
                ddata['Alt_File'] = Rel_Checker(file_path)[0]
                jsonhandler(f = RFile,pt=kw.pathtype, d = ddata, a='w')  
            return(kw.data)
        else:
            cprint("Cancelled file loading",mt='note',co=kw.co)
        
    if kw.act == 'init':
            try:
                kw.data = jsonhandler(f = Target_File,a='r')
                cprint(['Loading user set settings from path = ',Target_File],mt=['note','stat'],co=kw.co)
                return(kw.data)
            except:
                cprint(['Failed to load alt user settings file, using defaults instead'],mt=['err'],co=kw.co)
                return(ddata)
        
        
    
    if kw.act == 'ddir':
        RFile = "DataImportSettings.json"
        ddata = jsonhandler(f = RFile,pt=kw.pathtype,a='r')
        root = tk.Tk()
        file_path = askopenfilename(title = 'Select or write in a new Data Directories file',filetypes=[('json files','*.json'),('All Files','*.*')])
        tk.Tk.withdraw(root)
        
        file_path,kw.pathtype = Rel_Checker(file_path) 
        kw.data['Data_Directories_File'] = file_path
        
        if ddata['Alt_File'] is not None:
            try:
                cprint(['Saving user set settings to path = ',ddata['Alt_File']],mt=['note','stat'],co=kw.co)
                
                jsonhandler(f = ddata['Alt_File'],pt=kw.pathtype, d = kw.data, a='w')
                
            except:
                cprint(['Alt_File failed, setting user set settings to path = ',ddata['Default_File']],mt=['wrn','stat'],co=kw.co)
                jsonhandler(f = ddata['Default_File'],pt=kw.pathtype, d = kw.data, a='w')
        else:
            cprint(['Writing current user settings to path = ',PathSet(ddata['Default_File'],pt=kw.pathtype)],mt=['note','stat'],co=kw.co)
            jsonhandler(f = ddata['Default_File'],pt=kw.pathtype, d = kw.data, a='w')  
            
            
    
def Get_FileList(path,**kwargs):
    """
    A function that gives you a list of filenames from a specific folder
    path = path to files. Is relative unless you use kwarg pathtype = 'abs'
    kwargs**:
        pathtype: enum in ['rel','abs'], default = 'rel'. Allows you to manually enter absolute path    
        ext: file extension to look for, use format '.txt'. You can use a list e.g. ['.txt','.mat','.png'] to collect multiple files. Default is all files
        sorting: "alphabetical" or "numeric" sorting, default is "alphabetical"
    """
    kwargdict = {'pathtype':'pt','pt':'pt','path':'pt','p':'pt',
                 'extension':'ext','ext':'ext','ex':'ext','e':'ext',
                 's':'sort','sort':'sort','sorting':'sort'}
    #Collecting kwargs
    kw = KwargEval(kwargs, kwargdict, pt = 'rel',ext = None, sort = None)
    
    cprint('=-=-=-=-=-=-=-=-=-=-=- Running: Get_FileList -=-=-=-=-=-=-=-=-=-=-=',mt = 'funct')
    Dpath = PathSet(path,pt=kw.pt)
    #Checking that kw.sort has been selected correctly
    if kw.sort not in [None,'alphabetical','numeric']:
        cprint('sorting was not set correctly, reverting to using alphabetical sorting (no extra sorting)',mt='note')
        kw.sort = None
    
    #Filtering out the intended file types from the filenames
    #First, checking that the format for ext is correct.
    extreplacer = []
    if type(kw.ext) is str:
        if kw.ext.startswith('.') is False:
            kw.ext = '.'+kw.ext
            cprint('Correcting incorrect extension from ext = \''+kw.ext[1:]+ '\' to ext = \''+kw.ext+'\'',mt='caution')
        extreplacer.append(kw.ext)
        kw.ext = tuple(extreplacer)
    elif type(kw.ext) is tuple: 
        
        for i in range(len(kw.ext)):
            if kw.ext[i].startswith('.') is False:
                extreplacer.append('.'+kw.ext[i])
                cprint('tuple ext['+str(i)+'] was corrected from ext['+str(i)+'] = \''+kw.ext[i]+'\' to ext['+str(i)+'] = \'.'+kw.ext[i]+'\'',mt='caution')
            else:
                extreplacer.append(kw.ext[i])
        kw.ext = tuple(extreplacer)
    else:
        kw.ext = None
        cprint('ext must be in string or tuple format - setting ext = None and gathering all files instead',mt='err')
        
    summary = []
    if kw.ext is not None:
        NList = {}
        DList = {}
        summary = ['\nSummary:']
        for ex in kw.ext:
            NList[ex] = [file for file in os.listdir(Dpath) if file.endswith(ex)]
            if kw.sort == 'numeric':
                NList[ex] = natsort.natsorted(NList[ex], key=lambda y: y.lower())
                cprint([ex, ' files were sorted numerically'],fg=['g','c'],ts='b')
            DList[ex] = [Dpath+'\\'+name for name in NList[ex]]
            
        
            DSum = len(DList[ex])
            summary.append(str(DSum) + ' ' + ex + ' files')
                       
    else:
        NList = [file for file in os.listdir(Dpath)]
        if kw.sort == 'numeric':
            NList = natsort.natsorted(NList, key=lambda y: y.lower())
            cprint([ex, ' files were sorted numerically'],fg=['g','c'])
        DList = [Dpath+'\\'+name for name in NList]
    
    cprint(['A total of',str(len(DList)), 'file extensions were scanned.']+summary,ts='b',fg=['c','g','c',None,'g'],jc = [' ',' ','\n'])
    
    
    return(DList,NList)

#%%
#We probably only want to only load one matfile at a time, because otherwise we're going to quickly run out of memory!

def maxRepeating(str, **kwargs): 
    """
    DESCRIPTION.
    A function used to find and count the max repeating string, can be used to guess
    Parameters
    ----------
    str : TYPE
        DESCRIPTION.
    **kwargs : 
        guess : TYPE = str
        allows you to guess the escape character, and it will find the total number of that character only!

    Returns
    -------
    res,count
    Character and total number consecutive

    """
    guess = kwargs.get('guess',None)
    l = len(str) 
    count = 0
  
    # Find the maximum repeating  
    # character starting from str[i] 
    res = str[0] 
    for i in range(l): 
          
        cur_count = 1
        for j in range(i + 1, l): 
            if guess is not None:
                if (str[i] != str[j] or str[j] != guess):
                        break
            else:
                if (str[i] != str[j]):
                        break
            cur_count += 1
  
        # Update result if required 
        if cur_count > count : 
            count = cur_count 
            res = str[i] 
    return(res,count)
  
def MatLoader(file,**kwargs):
    cprint('=-=-=-=-=-=-=-=-=-=-=- Running: MatLoader -=-=-=-=-=-=-=-=-=-=-=',mt = 'funct')
    
    kwargdict = {'txt':'txt','textfile':'txt',
                 'dir':'path','directory':'path','path':'path','p':'path',
                 'tf':'tf','txtfile':'tf',
                 'esc':'esc','escape_character':'esc','e':'esc','esc_char':'esc'}
    kw = KwargEval(kwargs, kwargdict, txt  = False, path = 'same', tf  = None, esc  = None)
    
    #Mat File Loading
    FIELDDICT = {}
    f = h5py.File(file,'r')
    
    for k, v in f.items():
        FIELDDICT[k] = np.array(v)
    FIELDLIST = list(FIELDDICT.keys()) 
    data = {}
    dfields = []
    if '#refs#' in FIELDLIST: 
        FIELDLIST.remove('#refs#')
        cprint(["Scanning fields:"]+FIELDLIST,fg='c',ts='b')
    for i in range(len(FIELDLIST)):
        dfields.append(list(f[FIELDLIST[i]].keys()))
        
        for field in dfields[i]:
            data[field] = np.array(f[FIELDLIST[i]][field])
            if len(data[field].shape) == 2 and data[field].shape[0] == 1:
                oldshape    = data[field].shape
                data[field] = data[field][0]
                cprint(['corrected','data['+str(field)+'].shape','from',str(oldshape),'to',str(data[field].shape)],mt=['note','status','note','wrn','note','status'])
    
    mname = file.split('\\')[-1]
    data['matfilepath'] = file
    data['matname'] = mname
    #.txt File Loading
    if kw.txt == True:
        
        fname = mname.split('.')[0]
        if kw.tf == None and kw.path == 'same':
            path = os.path.dirname(file)
        txtlp = Get_FileList(path, ext='.txt',pathtype='abs')[0]

        txtind = [i for i, s in enumerate(txtlp['.txt']) if (s.split('\\')[-1]).split('.')[0] in fname]
        data['txtfilepath'] = txtlp['.txt'][txtind[0]]
        data['txtname'] = data['txtfilepath'].split('\\')[-1]
        d = []
        
        #determine escape character if none is given
        
        with open(data['txtfilepath'],'r') as source:
            line1 = source.readline()
            skipline1 = False
            if len(line1)<=1:
                line1 = source.readline()
                skipline1 = True
            if kw.esc == None or kw.esc not in line1:
                if '\t' not in line1:
                    numspc = maxRepeating(line1,guess=' ')
                    kw.esc = "".join([numspc[0] for i in range(numspc[1])])
                                    
                else:
                    kw.esc = '\t'
        
        with open(data['txtfilepath'],'r') as source:
            if skipline1 == True:
                source.readline()
                
            for line in source:
                line = line.strip('\n')
                fields = line.split(kw.esc)
                d.append(fields)  
        if len(d[-1]) < len(d[0]):
            d.pop(-1)
        try:
            float(d[0][1])
            FieldI = 0
            VarI   = 1
        except:
            FieldI = 1
            VarI   = 0
            
        for ent in d:
            ent[VarI] = float(ent[VarI])
            data[ent[FieldI]] = float(ent[VarI])
        cprint(['Loaded auxilary variables from file =',data['txtfilepath'], 'successfully!\n','Added:',str(d)],mt=['note','stat','note','note','stat'])

        
    tranconf = 0
    powconf  = 0 
    
    if 'trans' in FIELDLIST[0].lower():
        cprint('Best guess is that you just loaded the data from a Transfer Box a   nalysis group!', mt = 'curio')
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