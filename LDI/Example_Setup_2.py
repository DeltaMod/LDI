# -*- coding: utf-8 -*-
"""
Lumerical Data Handling
Created on Fri Feb  7 12:14:09 2020
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
from scipy.constants import e

from LDIutils import (DProc_Plot, LDI_Data_Import,txt_dict_loader,Get_FileList,MatLoader,CUV,jsonhandler,cprint,PathSet,AbsPowIntegrator,Rel_Checker,DataDir,Init_LDI,Prog_Dict_Importer,ezplot,MergeList,npy_filehandler)

##setting a default style:
from Graph_Styles import graph_style
graph_style()

#First step is to initialise your DataImportSettings
#Load user settings from a file using CUV
UV = CUV(act = 'init')
#If you have a same named .txt file with single named variables in a tab delimited format, you can set the following line to true
UV['txt_import'] = True

#If you do not want to use the default .json file, then you can run CUV() on its own in the console, and then you can select a new json file using the "ddir" command from the option select..

#Then we want to add folder with your data, and this data can be assorted or not. You do this using DataDir() and then selecting add using 0 in the console

#Once you have added at least one data directory in to your json file, you can now choose a dataset to load.

"""
DEFINING DATA DIRECTORIES AND GETTING THE FILES FROM THE CORRECT ONE
"""
#We get a list of all files in dicts matching the number of extensions we are searching for.
DIR,DIRPT = Rel_Checker(DataDir(act='load')['1'])
#If the LinWin script doesn't work, use this: DIR.replace('\\','/')
FLTuple = DList,NList = Get_FileList(DIR,pathtype=DIRPT, ext = (('mat','txt')),sorting='numeric')

#If you have exported your data as a non matlab file, like e.g. .npy, then you can add this following line
# if len(DList['.mat']) == 0:
#     DList,NList = Get_FileList(DIR,pathtype=DIRPT, ext = ('.npy'),sorting='numeric')


Dproc = LDI_Data_Import(FLTuple,ikey=['Eabs','lambda','P_tot'])

MDat = MatLoader(DList['.mat'][1])[0]
