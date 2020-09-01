# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 13:13:55 2020

@author: vidar
A small example file on what you would need to do to set up a normal setup for analysis
"""


#use this to set current directory without running code: os.chdir(os.path.dirname(sys.argv[0]))

from AuxFunct import (Get_FileList,MatLoader,CUV,jsonhandler,cprint,PathSet,AbsPowIntegrator,DataDir)
# import os
# import sys
# import time
# import h5py
# import hdf5storage
# import matplotlib
# import tkinter as tk
# from tkinter.filedialog import askopenfilename

# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import axes3d #If you want to be able to use projection="3D", then you need this:
# import scipy
# import numpy as np
# from scipy import integrate
# from scipy import interpolate
# import json
# from collections import Counter
# import natsort
# from scipy.constants import e

#run one time (currently missing [textimport])
UV = CUV(act = 'reset')

#every consecutive time, run: 
UV = CUV(act = 'init')

#run one time (when it is done! So, not yet)
#DataDir(act='add')

#run every consective time:
#Ddir = DataDir(act='load',index = 0)
    
#Get data filelist (DList = directories, NList = names of files)
DIR1 = "Directory to your data"; DIRPT = 'abs'
DList,NList = Get_FileList(DIR1,pathtype=DIRPT, ext = (('.mat','.txt')),sorting='numeric')

Dproc = {"data1":[],"data2":[]}
for file in DList['.mat']:
    MDat,MFi = MatLoader(file,txt=UV['txtimport'])  
    MDat['P_abs'] = np.reshape(MDat['Pabs'],[MDat['lambda'].shape[0],MDat['z'].shape[0],MDat['y'].shape[0],MDat['x'].shape[0]])   
    MDat['P_tot'] = AbsPowIntegrator(MDat['P_abs'],MDat['x'],MDat['y'],MDat['z'],MDat['lambda'])