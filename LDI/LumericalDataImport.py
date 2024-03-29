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


from LDI import (Get_FileList,MatLoader,CUV,jsonhandler,cprint,PathSet,AbsPowIntegrator,Rel_Checker,DataDir,Init_LDI,Prog_Dict_Importer,ezplot,MergeList,npy_filehandler)

##setting a default style:
from Graph_Styles import graph_style
graph_style()
    
    
#Load user settings from a file using CUV
UV = CUV(act = 'init')
UV['txt_import'] = True
#%%
#We get a list of all files in dicts matching the number of extensions we are searching for.
DIR,DIRPT = Rel_Checker(DataDir(act='load')['7'])
#DIR1 = 'C:\\Users\\vidar\\Desktop\\MD2_Contacts-24-08-2020'; DIRPT = 'abs'
#DIR1 = "Z:\\HDD-PC\\Work\\University Work\\Physics\\PhD Local Storage\\Data\\MD2_NoContacts-24-08-2020"; DIRPT = 'abs'

DList,NList = Get_FileList(DIR,pathtype=DIRPT, ext = (('mat','txt')),sorting='numeric')
if len(DList['.mat']) == 0:
    DList,NList = Get_FileList(DIR,pathtype=DIRPT, ext = ('.npy'),sorting='numeric')
#%%
#We probably only want to only load one matfile at a time, because otherwise we're going to quickly run out of memory!
# Dproc = {'AbsPow':[],'enw_x':[],'enw_y':[],'enw_z':[],'s_d':[],'enw_rot':[],'rel_rot':[],'current':[],'roundingradius dir':[],'GCx_span':[]}
P_out = 8.4e-15

"""
0.1 nA    1 nA     10 nA
0.02 fW     8.4 fW     0.5 pW
"""

"""
New method of importing data that does not require manual assignment of the keys in Dproc!
"""
#Scattering Peak Dictionary
SPD  = {'Abs':[],'Scat':[],'xdim':[],'ydim':[],'zdim':[]}


PlotParam = {'DFT Plot':True,'Cross Section':True,'Save Figure':False}
if UV['Debug'] == False:
    Dproc = {} # Create an empty dictionary to store your data in 
    try:
        for file in DList['.mat']:
            MDat,MFi = MatLoader(file,txt=UV['txt_import'])
    
            if 'lambda' not in MDat.keys():
                MDat['lambda'] = MatLoader("Z:\\HDD-PC\\Work\\University Work\\Physics\\PhD Local Storage\\Data\\Yagi-Uda\\DirectorResonance-18-02-2021\\WAVELENGTH.mat")[0]['lambda']
            
            """
            This was specific to plotting only from 1/3 monitors for the same data series
            if "_b." in MDat['matname']:    
                fig4 = ezplot(fid=4)
                fig4.DFT_Intensity_Plot(MDat['xgrid'],MDat['ygrid'],np.log10(MDat['Eabs_adj']),1e-6)
                colm = plt.cm.get_cmap("jet",1000)
                sm   = plt.cm.ScalarMappable(cmap=colm)
                plt.colorbar(sm,boundaries=np.linspace(0,1000,1000))
            """
            if PlotParam['DFT Plot'] == True:    
                try:
                    #%%
                    MDat['Eabs_adj'] = MDat['Eabs']#/(np.min(MDat['Eabs'])+0.000000001) - 1
                    ## Old Filtering Options 
                    #MDat['Eabs_adj'] = MDat['Eabs_adj']/np.max(MDat['Eabs_adj'])
                    
                    #for i in range(MDat['Eabs_adj'].shape[0]):
                    #    for j in range(MDat['Eabs_adj'].shape[1]):
                    #        if MDat['Eabs_adj'][i,j] >= 0.5*np.max(MDat['Eabs_adj']):
                    #            MDat['Eabs_adj'][i,j] = 0.1*MDat['Eabs_adj'][i,j]
                    
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
            
            if PlotParam['Cross Section'] == True:
                try:
                    SPD = Prog_Dict_Importer(SPD,{'Abs':np.max(MDat['Qabs']),'Scat':np.max(MDat['Qscat']),
                                                  'xdim':MDat['x_span_dir'],'ydim':MDat['y_span_dir'],'zdim':MDat['z_span_dir']})
                except:
                    None
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
                
                #First, add additional variables that need specific calculation manually into MDat (so Prog_Dict_Importer can grab them)
                if UV['txt_import'] == True:
                    if "ENW_x" and "ENW_y" and "ENW_z" in MDat.keys():
                        anw_l = np.array([0,0,MDat['ENW_z']])
                        enw_l = np.array([MDat['ENW_x'],MDat['ENW_y'],MDat['ENW_z']])
                        squared_dist = np.sum((anw_l-enw_l)**2, axis=0)
                    
                    if "ENW_z_rot" in MDat.keys():
                        enw_rot = MDat['ENW_z_rot'] 
                    
                    
                        if MDat['ENW_y'] == 0:
                            atdeg =  0
                        else:
                            atdeg = np.degrees(np.arctan(abs(MDat['ENW_x']/MDat['ENW_y']))) 
                    
                        rel_rot = enw_rot + atdeg
                        
                        if rel_rot>180:
                            rel_rot = atdeg - (180 - enw_rot)  
                        MDat['rel_rot'] = rel_rot
                        
                        MDat['s_d'] = np.sqrt(squared_dist)
                
                #Then do calculations on the longer data sets and store only the specific single data needed in MDat
                if 'Pabs' in MDat.keys():
                    MDat['P_abs'] = np.reshape(MDat['Pabs'],[MDat['lambda'].shape[0],MDat['z'].shape[0],MDat['y'].shape[0],MDat['x'].shape[0]])
                    cprint(['Now processing file: ',str(file)],mt='curio')
                if "Pabs_total" in MDat.keys():
                    MDat['P_tot']  = AbsPowIntegrator(MDat['P_abs'],MDat['x'],MDat['y'],MDat['z'],MDat['lambda'])
                    MDat['AbsPow'] = max(MDat['P_tot'])
            except:
                pass
            try:
                MDat['Pabs'] #this line is used to make sure that the transfer box results do not get placed into the same Dproc. In the future, Dproc will be set up to separate data based on what it thinks it is!
                #Use Prog_Dict_Importer to append remainder data that has a length smaller than ml=int *default 1 to Dproc
                Dproc = Prog_Dict_Importer(Dproc,MDat)
            
            except:
                pass
    
            
            
#%%            


# if UV['Debug'] == False:
     
#     for file in DList['.mat']:
#         MDat,MFi = MatLoader(file,txt=UV['txt_import'])    
#         try:
#             MDat['P_abs'] = np.reshape(MDat['Pabs'],[MDat['lambda'].shape[0],MDat['z'].shape[0],MDat['y'].shape[0],MDat['x'].shape[0]])   
#             #plt.imshow(np.rot90(MDat['P_abs'][0,:,:,6])) displays the same (xslice for [y,z]) as in lumerical
#             cprint(['Now processing file: ',str(file)],mt='curio')
            
#             MDat['P_tot'] = AbsPowIntegrator(MDat['P_abs'],MDat['x'],MDat['y'],MDat['z'],MDat['lambda'])
#             Dproc['AbsPow'].append(max(MDat['P_tot']))
#             if UV['txt_import'] == True:
#                 anw_l = np.array([0,0,MDat['ENW_z']])
#                 enw_l = np.array([MDat['ENW_x'],MDat['ENW_y'],MDat['ENW_z']])
#                 squared_dist = np.sum((anw_l-enw_l)**2, axis=0)
#                 enw_rot = MDat['ENW_z_rot'] 
                
                
#                 if MDat['ENW_y'] == 0:
#                     atdeg =  0
#                 else:
#                     atdeg = np.degrees(np.arctan(abs(MDat['ENW_x']/MDat['ENW_y']))) 
                
#                 rel_rot = enw_rot + atdeg
                
#                 if rel_rot>180:
#                     rel_rot = atdeg - (180 - enw_rot)  
                  
#                 #calculating curremt: Assume lambda[0] is max power (it is probably)
#                 Dproc['roundingradius dir'].append(MDat['roundingradius dir'])
#                 Dproc['current'] = Dproc['AbsPow'][-1]/e
#                 Dproc['s_d'].append(np.sqrt(squared_dist))
#                 Dproc['enw_rot'].append(enw_rot)
#                 Dproc['enw_x'].append(MDat['ENW_x'] )
#                 Dproc['enw_y'].append(MDat['ENW_y'] )
#                 Dproc['enw_z'].append(MDat['ENW_z'] )
#                 Dproc['rel_rot'].append(rel_rot)
#                 Dproc['GCx_span'].append(MDat['GCx_span']) 
                
#         except:
#             None
            
    #%%
        try: 
            if MDat['note'] == 'Director Rounding':
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
            elif MDat['note'] == 'Multi Dipole Director Rounding':
                fig1 = plt.figure(1) # This ensures you can plot over the old figure
                fig1.clf()           # This clears the old figure
                
                #2D plot
                ax1 = fig1.gca()
                ax1.set_title('Absorbed Power')
                ax1.set_xlabel('Director Rounding radius [m]')
                ax1.set_ylabel('Power Fraction: '+r'${P_{abs}}/{P_{tot}}$')
                ax1.grid(True)
                sca1 = ax1.scatter(Dproc['roundingradius dir'],Dproc['AbsPow'])
                
            elif MDat['note'] in ['Variable Contacts ', "pabs variable contacts"]:
                fig1 = plt.figure(1) # This ensures you can plot over the old figure
                fig1.clf()           # This clears the old figure
                
                #2D plot
                ax1 = fig1.gca()
                ax1.set_title('Absorbed Power')
                ax1.set_xlabel('Gold Contact span [m]')
                ax1.set_ylabel('Power Fraction: '+r'${P_{abs}}/{P_{tot}}$')
                ax1.grid(True)
                sca1 = ax1.scatter(Dproc['GCx_span'],Dproc['AbsPow'])
        
            
            elif MDat['note'] == "Director Separation":
                fig1 = plt.figure(1) # This ensures you can plot over the old figure
                fig1.clf()           # This clears the old figure
                
                
                NWuniq = list(np.unique(Dproc['NW_sep_dir']))
                Dproc['dir_sep_p.NW'] = [[] for n in range(len(NWuniq))]
                Dproc['abspow p.NW']     = [[] for n in range(len(NWuniq))]
                
                for i in range(0,len(Dproc['dir_sep'])-1):
                    NWind = NWuniq.index(Dproc['NW_sep_dir'][i])
                    Dproc['dir_sep_p.NW'][NWind].append(Dproc['dir_sep'][i])
                    Dproc['abspow p.NW'][NWind].append(Dproc['AbsPow'][i])
                    
                #2D plot
                ax1 = fig1.gca()
                ax1.set_title('Absorbed Power')
                ax1.set_xlabel('Director Separation [m]')
                ax1.set_ylabel('Power Fraction: '+r'${P_{abs}}/{P_{tot}}$')
                ax1.grid(True)
                for i in range(len(NWuniq)):
                    sca1 = ax1.scatter(Dproc['dir_sep_p.NW'][i],Dproc['abspow p.NW'][i])
                lgnd1 = ['NW sep = ' + str(nq) +'m' for nq in NWuniq]
                
                
                lmbd = [910e-9*1/n for n in range(2,6)]
                for i in range(len(lmbd)):    
                    ax1.plot([lmbd[i],lmbd[i]],[min(min(Dproc['abspow p.NW'])),max(max(Dproc['abspow p.NW']))])
                
                ax1.plot([min(Dproc['dir_sep']),max(Dproc['dir_sep'])],[Dproc['AbsPow'][-1],Dproc['AbsPow'][-1]])
                lgnd2 = ['$\lambda/$'+str(n) for n in range(2,6)]
                
                ax1.legend(lgnd2+lgnd1)
            else:
                
                
                if "no contacts" in MDat['note']:
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
                
                #for n in range(0,125,5*5):
                #    plt.plot(Dproc['s_d'][n],Dproc['AbsPow'][n],'+g')
                
               # for n in range(0,125,5):
                #    plt.plot(Dproc['s_d'][n],Dproc['AbsPow'][n],'*r')
                    
                
                
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
    except:
        None
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
            
    
if len(SPD['Abs'])>1 or ".npy" in DList.keys():
    
    plt.ion()  
    fig9 = ezplot(fid=9,projection='3d')
    plt.ion()  
    fig10 = ezplot(fid=10,projection='3d')    
    plt.ion()  
    fig11 = ezplot(fid=11,gspec=[1,2])
    if ".npy" not in DList.keys():
        gsz = Determine_Gridsize(SPD['xdim'],SPD['ydim'])
        XZ    = np.linspace(SPD['xdim'][0],SPD['xdim'][-1],gsz['xg'])
        Y     = np.linspace(SPD['ydim'][0],SPD['ydim'][-1],gsz['yg'])
        Iabs   = np.zeros([gsz['xg'],gsz['yg']]) 
        Isct  = np.zeros([gsz['xg'],gsz['yg']])
        m = 0
        
        
        for i in range(gsz['xg']):
            for j in range(gsz['yg']):
                Iabs[i,j] = np.max(SPD['Abs'][m])
                Isct[i,j] = np.max(SPD['Scat'][m])
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
    
#DP = "Z:\\HDD-PC\\Work\\University Work\\Physics\\PhD Local Storage\\Data\\DirectorResonance-18-2021-02"   
#MergeList(DP,'.png',c='_FI')

CUV(act = 'session',data=UV) #Saves user settings after each complete run!
#%%
"""
comp = [
7e-07, 0.00377263,
6.89447e-07, 0.00414069,
6.79208e-07, 0.00454842,
6.69268e-07, 0.00500499,
6.59615e-07, 0.00552264,
6.50237e-07, 0.00611169,
6.41121e-07, 0.00677529,
6.32258e-07, 0.00750842,
6.23636e-07, 0.00830372,
6.15247e-07, 0.00916187,
6.0708e-07, 0.0101,
5.99127e-07, 0.0111512,
5.91379e-07, 0.0123539,
5.8383e-07, 0.0137344,
5.76471e-07, 0.0152941,
5.69295e-07, 0.0170086,
5.62295e-07, 0.0188412,
5.55466e-07, 0.0207647,
5.488e-07, 0.0227782,
5.42292e-07, 0.0249087,
5.35938e-07, 0.0271938,
5.2973e-07, 0.0296524,
5.23664e-07, 0.0322573,
5.17736e-07, 0.0349238,
5.1194e-07, 0.0375188,
5.06273e-07, 0.0398887,
5.0073e-07, 0.0418913,
4.95307e-07, 0.0434199,
4.9e-07, 0.0444096,
4.84806e-07, 0.0448272,
4.7972e-07, 0.0446535,
4.7474e-07, 0.0438686,
4.69863e-07, 0.0424506,
4.65085e-07, 0.0403883,
4.60403e-07, 0.0377021,
4.55814e-07, 0.0344635,
4.51316e-07, 0.0308022,
4.46906e-07, 0.0268972,
4.42581e-07, 0.0229533,
4.38339e-07, 0.0191696,
4.34177e-07, 0.0157105,
4.30094e-07, 0.0126855,
4.26087e-07, 0.0101426,
4.22154e-07, 0.0080744,
4.18293e-07, 0.00643309,
4.14502e-07, 0.00514865,
4.10778e-07, 0.00414585,
4.07122e-07, 0.00335692,
4.03529e-07, 0.00272837,
4e-07, 0.00222265]
lambda2 = [comp[2*m] for m in range(int(len(comp)/2))]
int2 = [comp[2*m+1] for m in range(int(len(comp)/2))]
plt.plot(lambda2,int2)
plt.legend(['python interpolation','lumerical integration'])
plt.xlabel(r'$\lambda$ [m]')
plt.ylabel(r'$\frac{P_abs}{P_tot}$')
plt.grid(True)
"""


#%%
"""
The commented text here is old code - I'm actively working on renewing it to be more self-expandable.'

Mat = []
for i in DList['.mat']:
    Matfile = hdf5storage.loadmat(i)
    Matfile['name'] = i.split("\\")[-1]
    Mat.append(Matfile)
    
fid = 1    
Xdim,Ydim = Mat[fid]['Ex'][:,:,0,0].shape
def MatLoader(fid,MATF):
    x  = MATF[fid]['x'] #xaxis
    y  = MATF[fid]['y'] #yaxis
    z  = MATF[fid]['z'] #zaxis
    f  = MATF[fid]['f'] #frequency of the light probed
    if 'Px' in MATF[fid].keys():
        Px = MATF[fid]['Px']
        Py = MATF[fid]['Py']
        Pz = MATF[fid]['Pz']
        fn = 0
        mod = 1e-08
    
        Pv = {'x':[],'y':[],'z':[],'xc':[],'yc':[],'zc':[],'Px':[],'Py':[],'Pz':[],'L':[],'norm':[],'f':[]}
        Pv['x'] = x
        Pv['y'] = y
        Pv['z'] = z
        Pv['f'] = f
        for xn in range(len(x)):
            for yn in range(len(y)):
                for zn in range(len(z)):
                    Pv['Px'].append(np.real(MATF[fid]['Px'][xn,yn,zn,fn]))
                    Pv['Py'].append(np.real(MATF[fid]['Py'][xn,yn,zn,fn]))
                    Pv['Pz'].append(np.real(MATF[fid]['Pz'][xn,yn,zn,fn]))
                    Pv['xc'].append(x[xn])
                    Pv['yc'].append(y[yn])
                    Pv['zc'].append(y[zn])
                    Pv['L'].append( np.sqrt(Pv['Px'][-1]**2+Pv['Py'][-1]**2+Pv['Pz'][-1]**2))
                    Pv['norm'].append(mod/(Pv['L'][-1]))
        Pv['pPx'] = Px
        Pv['pPy'] = Py
        Pv['pPz'] = Pz
    return(Pv)

P_in  = MatLoader(4,Mat)
P_out = MatLoader(5,Mat)

def QuivPlot(figID,Pwr,ADD,SubSmple):
    fig = plt.figure(figID)
    if ADD == False:
        fig.clf()           # This clears the old figure
        ax = fig.add_subplot(projection='3d',proj_type='persp') # Makes a graph that covers a 2x2 size and has 3D projection
        
    cmap = plt.get_cmap('jet')
    #3D plot
    for name in Pwr.keys():
        Pwr[name] = np.asarray(Pwr[name])
    for n in range(0,len(Pwr['xc']),SubSmple):
        ax.quiver(Pwr['xc'][n],Pwr['yc'][n],Pwr['zc'][n],Pwr['norm'][n]*Pwr['Px'][n],Pwr['norm'][n]*Pwr['Py'][n],Pwr['norm'][n]*Pwr['Pz'][n],color=cmap(Pwr['L'][n]/np.max(Pwr['L'])))
    
QuivPlot(1,P_in,False,1)
QuivPlot(2,P_out,False,1)







def TotalPow(self):
    self['P_xp'] = [np.sum(np.real(self['pPx'][x,:,:,:])) for x in range(len(self['x'])) ]
  
    self['P_yp'] = [np.sum(np.real(self['pPy'][:,y,:,:])) for y in range(len(self['y'])) ]

    self['P_zp'] = [np.sum(np.real(self['pPz'][:,:,z,:])) for z in range(len(self['z'])) ]
TotalPow(P_in)
TotalPow(P_out)

#Surface Plots
#%%
fig = plt.figure(4)
fig.clf()           # This clears the old figure
ax = fig.add_subplot(projection='3d') # Makes a graph that covers a 2x2 size and has 3D projection
plt.ion()

Pow_l = []

for lambd in range(len(P_out['f'])):
    tempsum = 0
    for x in [0,-1]:
        A = sum(sum(np.real(P_out['pPx'][x,:,:,lambd])))
        B = sum(sum(np.real(P_out['pPy'][:,x,:,lambd])))
        C = sum(sum(np.real(P_out['pPz'][:,:,x,lambd])))
        tempsum = tempsum + abs(A)+abs(B)+abs(C)  
    Pow_l.append(tempsum)
# for x in [0,-1]:
#     for lambd in range(len(P_out['f'])):
        
        # Z,Y = np.meshgrid(P_out['z'],P_out['y'])
        # Pxsurf = P_out['pPx'][x,:,:,lambd]
        # ax.plot_surface(Y,Z,np.real(Pxsurf))

"""
 
"""
The data format used for all monitors has the following principle:
    Mat[file ID]['key'][xaxis,yaxis,zaxis,lambda]
If you want to slice through the x axis, showing the real valued intensity plotted in y/z, then you use:
for fn in range(len(Mat[fid]['f'])):
    for xn in range(len(x)):
        

im = plt.imshow(np.real(Mat[fid]['Py'][:,0,:,0]),cmap='jet')
for fn in range(len(Mat[fid]['f'])):
    for zn in range(len(z)):
        im.set_data(np.real(Mat[fid]['Pz'][:,:,zn,fn]))
        plt.draw()
        plt.pause(0.2)
        



""" 
    


