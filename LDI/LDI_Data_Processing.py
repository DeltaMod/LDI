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
    
    
#Load user settings from a file using CUV
UV = CUV(act = 'init')
UV['txt_import'] = True
#%%
"""
DEFINING DATA DIRECTORIES AND GETTING THE FILES FROM THE CORRECT ONE
"""
#We get a list of all files in dicts matching the number of extensions we are searching for.
#DIR,DIRPT = Rel_Checker(DataDir(act='load')['8'])
DIR,DIRPT = Rel_Checker(DataDir(act='load')['10'])

FLTuple = DList,NList = Get_FileList(DIR,pathtype=DIRPT, ext = (('mat','txt')),sorting='numeric')

if len(DList['.mat']) == 0:
    DList,NList = Get_FileList(DIR,pathtype=DIRPT, ext = ('.npy'),sorting='numeric')
#%%
#We probably only want to only load one matfile at a time, because otherwise we're going to quickly run out of memory!
P_out = 8.4e-15
"""
0.1 nA    1 nA     10 nA
0.02 fW     8.4 fW     0.5 pW
"""
"""
New method of importing data that does not require manual assignment of the keys in Dproc!
"""
PlotParam = {'DFT Plot':True,'Cross Section':True,'Save Figure':False}
#First load any raw data into Dproc

if UV['Debug'] == False:
    Dproc = LDI_Data_Import(FLTuple,ikey=['lambda','P_tot'])
#%%        
    MDat = MatLoader(DList['.mat'][1])[0]
#%%

PlotParam = {'DFT Plot':False,'Cross Section':False,'Save Figure':False}
if PlotParam['DFT Plot'] == True:    
    try:
        #%%
        MDat['Eabs_adj'] = MDat['Eabs']#/(np.min(MDat['Eabs'])+0.000000001) - 1
        fig4 = ezplot(fid=4)
        fig4.DFT_Intensity_Plot(MDat['xgrid'],MDat['ygrid'],np.log10(MDat['Eabs_adj']),1e-6)
        colm = plt.cm.get_cmap("jet",100000)
        sm   = plt.cm.ScalarMappable(cmap=colm)
        plt.colorbar(sm,boundaries=np.linspace(0,100000,100000))
        
        fig4.ax[0].set_title("$\_$".join(MDat['matname'].split('_')),fontsize=11)
        MGMat = [mf for mf in DList['.mat'] if "DFT" in mf][-1]
        mxgrid = MatLoader(MGMat,txt=UV['txt_import'])[0]['xgrid']
        mygrid = MatLoader(MGMat,txt=UV['txt_import'])[0]['ygrid']
        fig4.ax[0].set_xlim(min(mxgrid)*1e-6, max(mxgrid)*1e-6)
        fig4.ax[0].set_ylim(min(mygrid)*1e-6, max(mygrid)*1e-6)
        #%%
        if PlotParam['Save Figure'] == True:
            fig4.fig.savefig(MDat['matfilepath'].split('.')[0]+'_FI.png',dpi=250)
    except:
        
       None
#%%
if PlotParam['Cross Section'] == True:
    try:
        fig5 = ezplot(fid=5)
        fig5.ax[0].plot(MDat['lambda'],MDat['Qabs'],'b',label='absorption cs')
        fig5.ax[0].plot(MDat['lambda'],MDat['Qscat'],'r',label='Scattering cs')
        fig5.ax[0].set_xlabel('Wavelength [m]')
        fig5.ax[0].set_ylabel('Mie Efficiency')
        fig5.ax[0].set_title("$\_$".join(MDat['matname'].split('_')),fontsize=11)
        fig5.ax[0].set_ylim(0,100)
        fig5.ax[0].annotate(s='[dx,dy,dz] = \n'+'['+str(float('%.3g'%MDat['x_span_dir']))+','+str(float('%.3g'%MDat['y_span_dir']))+','+str(float('%.3g'%MDat['z_span_dir']))+']',xy=(0.125,0.85),xycoords='figure fraction')
        fig5.ax[0].legend()
        if PlotParam['Save Figure'] == True:
            fig5.fig.savefig(MDat['matfilepath'].split('.')[0]+'_CS.png',dpi=250)
    except:
        None        
                    
    
try:
    fig = DProc_Plot(Dproc,None)
except:
    None       
            
"""
try: 
    if Dproc['note'][0] == 'Director Rounding':
        fig1 = plt.figure(1) # This ensures you can plot over the old figure
        fig1.clf()           # This clears the old figure
        
        #2D plot
        ax1 = fig1.gca()
        ax1.set_title('Absorbed Power')
        ax1.set_xlabel('Director Rounding radius [m]')
        ax1.set_ylabel('Power Fraction: '+r'${P_{abs}}/{P_{tot}}$')
        ax1.grid(True)
        sca1 = ax1.scatter(Dproc['roundingradius dir'],Dproc['AbsPow'])
        ax1.legend(['Multi-Dipole'])
    elif Dproc['note'][0] == 'Multi Dipole Director Rounding':
        fig1 = plt.figure(1) # This ensures you can plot over the old figure
        fig1.clf()           # This clears the old figure
        
        #2D plot
        ax1 = fig1.gca()
        ax1.set_title('Absorbed Power')
        ax1.set_xlabel('Director Rounding radius [m]')
        ax1.set_ylabel('Power Fraction: '+r'${P_{abs}}/{P_{tot}}$')
        ax1.grid(True)
        sca1 = ax1.scatter(Dproc['roundingradius dir'],Dproc['AbsPow'])
        
    elif Dproc['note'][0] in ['Variable Contacts ', "pabs variable contacts"]:
        fig1 = plt.figure(1) # This ensures you can plot over the old figure
        fig1.clf()           # This clears the old figure
        
        #2D plot
        ax1 = fig1.gca()
        ax1.set_title('Absorbed Power')
        ax1.set_xlabel('Gold Contact span [m]')
        ax1.set_ylabel('Power Fraction: '+r'${P_{abs}}/{P_{tot}}$')
        ax1.grid(True)
        sca1 = ax1.scatter(Dproc['GCx_span'],Dproc['AbsPow'])

    
    elif Dproc['note'][0] == "Director Separation":
        fig1 = plt.figure(1) # This ensures you can plot over the old figure
        fig1.clf()           # This clears the old figure
        
        
        NWuniq = list(np.unique(Dproc['NW_sep_dir']))
        Dproc['dir_sep_p.NW'] = [[] for n in range(len(NWuniq))]
        Dproc['abspow p.NW']     = [[] for n in range(len(NWuniq))]
        
        for i in range(0,len(Dproc['dir_sep'])):
            NWind = NWuniq.index(Dproc['NW_sep_dir'][i])
            Dproc['dir_sep_p.NW'][NWind].append(Dproc['dir_sep'][i])
            Dproc['abspow p.NW'][NWind].append(Dproc['AbsPow'][i])
            
        #2D plot
        ax1 = fig1.gca()
        ax1.set_title('Absorbed Power')
        ax1.set_xlabel('Director Separation [m]')
        ax1.set_ylabel('Power Fraction: '+r'${P_{abs}}/{P_{tot}}$')
        ax1.grid(True)
        for i,nuq in enumerate(NWuniq):
            if nuq != 0:
                sca1 = ax1.scatter(Dproc['dir_sep_p.NW'][i],Dproc['abspow p.NW'][i],label='NW sep = ' + str(NWuniq[i]) +'m')
            elif nuq == 0:
                ax1.plot([min(x for x in Dproc['dir_sep'] if x !=0),max(Dproc['dir_sep'])],[Dproc['abspow p.NW'][i][0],Dproc['abspow p.NW'][i][0]],label='no antenna')
                ax1.plot([min(x for x in Dproc['dir_sep'] if x !=0),max(Dproc['dir_sep'])],[Dproc['abspow p.NW'][i][1],Dproc['abspow p.NW'][i][1]],label='reflector only')
        
        lmbd = [910e-9*1/n for n in range(2,6)]
        for i in range(len(lmbd)):    
            ax1.plot([lmbd[i],lmbd[i]],[min(min(Dproc['abspow p.NW'])),max(max(Dproc['abspow p.NW']))],label='$\lambda/$'+str(i+2))
        
        ax1.set_xlim([1.6e-7,max(Dproc['dir_sep'])])
        ax1.legend()
    else:
        
        
        if "no contacts" in Dproc['note']:
            title = "Absorbed Power without Gold Contacts"
        else:
            title = "Absorbed Power with Gold Contacts"
            
        fig1 = plt.figure(1) # This ensures you can plot over the old figure
        fig1.clf()           # This clears the old figure
        
        #2D plot
        ax1 = fig1.gca()
        ax1.set_title(title)
        ax1.set_xlabel('distance from source [m]')
        ax1.set_ylabel('Power Fraction: '+r'${P_{abs}}/{P_{tot}}$')
        ax1.grid(True)
        sca1 = ax1.scatter(Dproc['s_d'],Dproc['AbsPow'],c=Dproc['rel_rot'],cmap='gnuplot')
        cb1 = fig1.colorbar(sca1)
        cb1.set_label('Relative Rotation '+r'$[\theta$]')

        
        LComp,LCompFi = MatLoader(DList['.mat'][0])
        LComp['P_abs'] = np.reshape(LComp['Pabs'],[LComp['lambda'].shape[0],LComp['z'].shape[0],LComp['y'].shape[0],LComp['x'].shape[0]])   
        #plt.imshow(np.rot90(LComp['P_abs'][0,:,:,6])) displays the same (xslice for [y,z]) as in lumerical
        
        LComp['P_tot'] = AbsPowIntegrator(LComp['P_abs'],LComp['x'],LComp['y'],LComp['z'],LComp['lambda'])
        plt.figure(2)
        plt.plot(LComp['lambda'],LComp['P_tot'])
    
        
    
    
        
        PDP = []
        PDR = []
        PDL = []
        PLP = []
        PLR = []
        PLL = []
        TPDP = []
        TPDL = []
        TPDR = []
        
        for i in range(len(Dproc['AbsPow'])):
            if Dproc['rel_rot'][i] < 60 or Dproc['rel_rot'][i] > 120:
                PDP.append(Dproc['AbsPow'][i])
                PDR.append(Dproc['rel_rot'][i])
                PDL.append(Dproc['s_d'][i])
            else:
                PLP.append(Dproc['AbsPow'][i])
                PLR.append(Dproc['rel_rot'][i])
                PLL.append(Dproc['s_d'][i])
            if Dproc['rel_rot'][i] < 10 or Dproc['rel_rot'][i] > 170:
                if Dproc['ENW_x'][i] == 0:
                     TPDP.append(Dproc['AbsPow'][i])
                     TPDR.append(Dproc['rel_rot'][i])
                     TPDL.append(Dproc['s_d'][i])
        
            
        fig3 = plt.figure(3) # This ensures you can plot over the old figure
        fig3.clf()           # This clears the old figure
        
        
        #2D plot
        ax3 = fig3.gca()
        ax3.set_title(title)
        ax3.set_xlabel('distance from source [m]')
        ax3.set_ylabel('Power Fraction: '+r'${P_{abs}}/{P_{tot}}$')
        ax3.grid(True)
        ax3.scatter(PDL,PDP,c='cyan')
        sca3 = ax3.scatter(PLL,PLP,c=PLR ,cmap='gnuplot')
        ax3.scatter(TPDL,TPDP,c='green')
        cb3 = fig3.colorbar(sca3)
        cb3.set_label('Relative Rotation '+r'$[\theta$]')
except:
    CFUNC = 'Nope'
    if CFUNC == 'E PLOT':
        
        # Import data from Lumerical data files
        # Portion of the system to be plotted in linear scale
        
        #We might want to remove peak intensities:
        MDat['Eabs_adj'] = MDat['Eabs']
        
        #for i in range(MDat['Eabs_adj'].shape[0]):
        #    for j in range(MDat['Eabs_adj'].shape[1]):
        #        if MDat['Eabs_adj'][i,j] >= 0.5*np.max(MDat['Eabs_adj']):
        #            MDat['Eabs_adj'][i,j] = 0.1*MDat['Eabs_adj'][i,j]
        
        fig4 = ezplot(fid=4)
        fig4.DFT_Intensity_Plot(MDat['xgrid'],MDat['ygrid'],np.log10(MDat['Eabs']),1e-6,ax_id=0)
        fig4.ax[0].set_title("$\_$".join(MDat['matname'].split('_')),fontsize=11)
        fig4.fig.savefig(MDat['matfilepath'].split('.')[0]+'.png')

#%%
def Determine_Gridsize(xgrid,ygrid):
    def Count_Repeated(grid):
        num = 0
        orig = grid[0]
        for p in grid:
            if p != orig:
                break
            num += 1
        return(num)
    
    def Count_Until_Repeat(grid):
        num = 1
        orig = grid[0]
        for p in grid[1:]:
            if p == orig:
                break
            num += 1
        return(num)
    xnum = [Count_Repeated(xgrid),Count_Until_Repeat(xgrid)] 
    ynum = [Count_Repeated(ygrid),Count_Until_Repeat(ygrid)] 
    return({'xg':max(xnum),'yg':max(ynum)})
"""            
    
try:
    if len(Dproc['Q_Abs'])>1 or ".npy" in DList.keys():
        
        plt.ion()  
        fig9 = ezplot(fid=9,projection='3d')
        plt.ion()  
        fig10 = ezplot(fid=10,projection='3d')    
        plt.ion()  
        fig11 = ezplot(fid=11,gspec=[1,2])
        if ".npy" not in DList.keys():
            gsz = Determine_Gridsize(Dproc['x_span_dir'],Dproc['y_span_dir'])
            XZ    = np.linspace(Dproc['x_span_dir'][0],Dproc['x_span_dir'][-1],gsz['xg'])
            Y     = np.linspace(Dproc['y_span_dir'][0],Dproc['y_span_dir'][-1],gsz['yg'])
            Iabs   = np.zeros([gsz['xg'],gsz['yg']]) 
            Isct  = np.zeros([gsz['xg'],gsz['yg']])
            m = 0
            
            
            for i in range(gsz['xg']):
                for j in range(gsz['yg']):
                    Iabs[i,j] = np.max(Dproc['Q_Abs'][m])
                    Isct[i,j] = np.max(Dproc['Q_Scat'][m])
                    m += 1
                    
            fig9.ax[0].plot_surface(np.meshgrid(XZ,Y)[0],np.meshgrid(XZ,Y)[1],Iabs)
            fig10.ax[0].plot_surface(np.meshgrid(XZ,Y)[0],np.meshgrid(XZ,Y)[1],Isct)
            fig11.ax[0].pcolormesh(np.meshgrid(XZ,Y)[0],np.meshgrid(XZ,Y)[1],Isct,cmap="plasma")
            fig11.ax[1].pcolormesh(np.meshgrid(XZ,Y)[0],np.meshgrid(XZ,Y)[1],Iabs,cmap="plasma")
            Results_Dict = {'gsz':gsz,'XZ':XZ,'Y':Y,'Iabs':Iabs,'Isct':Isct}
            #npy_filehandler(f = "\\".join(MDat['matfilepath'].split('\\')[0:-1])+'\\Abs_Scat_Maxima' ,d=Results_Dict,pt='abs', a='s')
        else:
            IDAT = [npy_filehandler(f = file ,pt='abs', a='l') for file in DList['.npy']]
            i = 0
            for dd in IDAT:
                if i != 1125125152:
                    Iabs,Isct,XZ,Y = [dd['Iabs'],dd['Isct'],dd['XZ'],dd['Y']]
                    fig9.ax[0].plot_surface(np.meshgrid(XZ,Y)[1],np.meshgrid(XZ,Y)[0],Iabs)
                    fig10.ax[0].plot_surface(np.meshgrid(XZ,Y)[1],np.meshgrid(XZ,Y)[0],Isct)
                    fig11.ax[0].pcolormesh(np.meshgrid(Y,XZ)[0],np.meshgrid(Y,XZ)[1],Isct,cmap="plasma")
                    fig11.ax[1].pcolormesh(np.meshgrid(Y,XZ)[0],np.meshgrid(Y,XZ)[1],Iabs,cmap="plasma")
                i +=1
        
        
        fig9.ax[0].set_ylabel('Director short diameter')
        fig9.ax[0].set_xlabel('Director Length')
        fig9.ax[0].set_zlabel('Absorption')
         
        
        fig10.ax[0].set_ylabel('Director short diameter')
        fig10.ax[0].set_xlabel('Director Length')
        fig10.ax[0].set_zlabel('Absorption')
    
    
        fig11.ax[0].set_ylabel('Director short diameter')
        fig11.ax[0].set_xlabel('Director Length')
        fig11.ax[0].set_title('Scattering Cross Section')
        fig11.ax[1].set_ylabel('Director short diameter')
        fig11.ax[1].set_xlabel('Director Length')
        fig11.ax[1].set_title('Absorption Cross Section')
except:
    None

CUV(act = 'session',data=UV) #Saves user settings after each complete run!


