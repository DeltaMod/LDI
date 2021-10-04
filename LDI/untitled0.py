# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 14:42:44 2021

@author: vidar
"""

#use this to set current directory without running code: os.chdir(os.path.dirname(sys.argv[0]))
import matplotlib.pyplot as plt
import scipy
import numpy as np
from scipy.constants import e
import pandas as pd
import matplotlib as mpl


from LDI import (Get_FileList,MatLoader,CUV,jsonhandler,cprint,PathSet,AbsPowIntegrator,Rel_Checker,DataDir,Init_LDI,Prog_Dict_Importer,ezplot,MergeList,npy_filehandler)


#setting a default style:
#from Graph_Styles import graph_style
#graph_style()



DIR,DIRPT = Rel_Checker("Example_Data")
DList,NList = Get_FileList(DIR,pathtype=DIRPT, ext = (('txt','dat')),sorting='numeric')

data = pd.read_table(DList['.dat'][2    ])


Bias = np.array(data[data.keys()[0]][35:])
I_fwd = np.array(data[data.keys()[1]][35:])
I_rev = np.array(data[data.keys()[2]][35:])
Bias = [float(i) for i in Bias]
I_fwd = [float(i) for i in I_fwd]
I_rev = [float(i) for i in I_rev]

fig = plt.figure(1)
fig.clf()
ax = fig.gca()
ax.plot(Bias,I_fwd,'r')
ax.plot(Bias,I_rev,'b')
ax.legend(['forward bias','reverse bias'])
ax.set_xlabel("Voltage [V]")
ax.set_ylabel("Current [A]")
plt.show()