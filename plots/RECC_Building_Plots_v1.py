# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 13:54:19 2023

@author: spauliuk

This script loads previously compiled results and then compiles selected results 
into different visualisations, like line plots and bar charts.

Works together with control workbook
RECCv2.5_EXPORT_Combine_Select.xlxs

Need to run ODYM_RECC_Export_xlxs_Combine_Select.py first!

Documentation and how to in RECCv2.5_EXPORT_Combine_Select.xlxs

"""
import os
import plotnine
import openpyxl
from plotnine import *
import pandas as pd
import pylab
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.lines as mlines
import numpy as np
import RECC_Paths # Import path file


CP            = os.path.join(RECC_Paths.results_path,'RECCv2.5_EXPORT_Combine_Select.xlsx')   
CF            = openpyxl.load_workbook(CP)
CS            = CF['Cover'].cell(4,4).value
outpath       = CF[CS].cell(1,2).value
fn_add        = CF[CS].cell(1,4).value

r = 1
# Move to parameter list:
while True:
    if CF[CS].cell(r,1).value == 'Define Plots':
        break    
    r += 1
r += 1

ptitles = []
ptypes  = []
pinds   = []
pregs   = []
pscens  = []
prange  = []
pflags  = []
indlab  = [] # indicator short labels for plots
scelab  = [] # scenario  short labels for plots
colors  = [] # List with color strings
while True:
    if CF[CS].cell(r,2).value is None:
        break    
    ptitles.append(CF[CS].cell(r,2).value)
    ptypes.append(CF[CS].cell(r,3).value)
    pinds.append(CF[CS].cell(r,4).value)
    pregs.append(CF[CS].cell(r,5).value)
    pscens.append(CF[CS].cell(r,6).value)
    prange.append(CF[CS].cell(r,7).value)
    pflags.append(CF[CS].cell(r,8).value)
    indlab.append(CF[CS].cell(r,9).value)
    scelab.append(CF[CS].cell(r,10).value)
    colors.append(CF[CS].cell(r,11).value)
    r += 1

# open data file with results
fn = os.path.join(RECC_Paths.export_path,outpath,'Results_Extracted_RECCv2.5_' + fn_add + '_sep.xlsx')
ps = pd.read_excel(fn, sheet_name='Results', index_col=0) # plot sheet
pc = pd.read_excel(fn, sheet_name='Results_Cumulative', index_col=0) # plot sheet cumulative

#regions = ['R5.2ASIA','R5.2SSA','R5.2LAM','R5.2MNF','R5.2REF','R5.2OECD_Other','EU_UK','R32USACAN','Global']
regions = ['R5.2SSA','R5.2LAM','EU_UK','China','India','R5.2ASIA_Other','Global']

for m in range(0,len(ptitles)):
    if ptypes[m] == 'Fig_StockPattern':
        # Custom plot for in-use stock
        if pflags[m] == 'reb':
            inds = 'In-use stock, res. buildings'
            insc = 'final consumption (use phase inflow), all res. building types together'
            ind2 = 'Stock curve of all pre 2021 age-cohorts, res. blds.'
            iflo = 'final consumption (use phase inflow), all res. building types together'
            oflo = 'decommissioned buildings (use phase outflow), all res. building types together'
        if pflags[m] == 'nrb':
            inds = 'In-use stock, nonres. buildings'
            indc = 'final consumption (use phase inflow), all nonres. building types together'
            ind2 = 'Stock curve of all pre 2021 age-cohorts, non-res. blds.'
            iflo = 'final consumption (use phase inflow), all nonres. building types together'
            oflo = 'decommissioned buildings (use phase outflow), all nonres. building types together'
           
        for rr in range(0,len(regions)):
            selectR = regions[rr]
            selectS = pscens[m].split(';')
            stock_data = np.zeros((3,41))
            # For the time series plot
            for sce in range(0,3):
                pst    = ps[ps['Indicator'].isin([inds]) & ps['Region'].isin([selectR]) & ps['Scenario'].isin([selectS[sce]])] # Select the specified data and compile them for plotting        
                pst.set_index('Scenario', inplace=True)
                pst.drop(['Region','Indicator','Sectors','Unit'], axis=1, inplace=True) # Delete labels that are not needed
                stock_data[sce,:] = pst[np.arange(2020,2061)].values
            pst    = ps[ps['Indicator'].isin([ind2]) & ps['Region'].isin([selectR]) & ps['Scenario'].isin([selectS[sce]])] # Select the specified data and compile them for plotting        
            pst.set_index('Scenario', inplace=True)
            pst.drop(['Region','Indicator','Sectors','Unit'], axis=1, inplace=True) # Delete labels that are not needed
            stock_2020 = pst[np.arange(2020,2061)].values     
            # For the cumulative plot
            inflow_d  = np.zeros((3))
            outflow_d = np.zeros((3))
            flowscen  = ['LED_LIGHT','SSP1_LIGHT','SSP2_BASE']
            for fsc in range(0,3):
                pst    = pc[pc['Indicator'].isin([iflo]) & pc['Region'].isin([selectR]) & pc['Scenario'].isin([flowscen[fsc]])] # Select the specified data and compile them for plotting        
                inflow_d[fsc]  = pst.iloc[0]['Cum. 2020-2050 (incl.)'] / 1000 # in bn m²  
                pst    = pc[pc['Indicator'].isin([oflo]) & pc['Region'].isin([selectR]) & pc['Scenario'].isin([flowscen[fsc]])] # Select the specified data and compile them for plotting        
                outflow_d[fsc] = pst.iloc[0]['Cum. 2020-2050 (incl.)'] / 1000 # in bn m²
            
            #c_f = np.array([[112,173,71],[198,224,180]])/255# medium green and light green
            c_f = np.array([[228,211,148],[228,211,148]])/255# light brown
            c_b = np.array([[214,238,252],[214,238,252]])/255# light blue
            fig, axs = plt.subplots(nrows=1, ncols=2 , figsize=(7, 3), gridspec_kw={'width_ratios':[3,1]})        
            fig.tight_layout(rect=[0, 0.03, 1, 0.85])
            fig.suptitle('stock pattern, ' + pflags[m] + ', ' + selectR, fontsize=18)
            ProxyHandlesList  = []   # For legend 
            ProxyHandlesList2 = []   # For legend 
            
            axs[0].fill_between(np.arange(2020,2061), stock_data[0,:]/1000, stock_data[2,:]/1000, facecolor = np.array([252,228,214])/255)
            #axs[0].plot(np.arange(2020,2061), stock_data[0,:]/1000, linewidth = 1.3)
            axs[0].plot(np.arange(2020,2061), stock_data[1,:]/1000, linewidth = 2.3, color = np.array([198,89,17])/255)
            # post 2020 stock
            axs[0].plot(np.arange(2020,2061), stock_2020[0,:]/1000, linewidth = 1.5, color = np.array([140,140,140])/255)
            axs[0].fill_between(np.arange(2020,2061), 0, stock_2020[0,:]/1000, facecolor = np.array([220,220,220])/255)
            #axs[0].plot(np.arange(2020,2061), stock_data[2,:]/1000, linewidth = 1.3)
            axs[0].plot([2020,2060],[stock_data[1,0]/1000,stock_data[1,0]/1000],linestyle = '--', linewidth = 1, color = 'k')
            axs[0].set_ylim(bottom=0)
            axs[0].set_ylabel('Billion m²', fontsize = 12)
            axs[0].set_xlabel('Year', fontsize = 12)
            axs[0].legend(labels = ['LED-SSP1-SSP2 range','SSP1','pre 2020 age-cohorts','pre 2020 age-cohorts','2020 stock level'],shadow = False, prop={'size':7},ncol=1, loc = 'upper left')
            axs[0].set_xlim([2020,2060])
            axs[0].title.set_text('stock over time')
            
            bw = 0.6
            ProxyHandlesList2.append(plt.fill_between([1-bw/2,1+bw/2], [0,0],[inflow_d[1], inflow_d[1]], linestyle = '-', facecolor = c_f[0], linewidth = 0.5, edgecolor = 'k'))            
            ProxyHandlesList2.append(mlines.Line2D([], [],linestyle = '-', linewidth = 0.8, color = 'k'))
            axs[1].fill_between([1-bw/2,1+bw/2], [0,0],[inflow_d[1], inflow_d[1]], linestyle = '-', facecolor = c_f[0], linewidth = 0.5, edgecolor = 'k')
            axs[1].fill_between([2-bw/2,2+bw/2], [0,0],[outflow_d[1],outflow_d[1]],linestyle = '-', facecolor = c_f[0], linewidth = 0.5, edgecolor = 'k')
            axs[1].plot([1-bw/4,1+bw/4],[inflow_d[0], inflow_d[0]],linestyle = '-', linewidth = 0.8, color = 'k')
            axs[1].plot([1-bw/4,1+bw/4],[inflow_d[2], inflow_d[2]],linestyle = '-', linewidth = 0.8, color = 'k')
            axs[1].plot([1,1],[inflow_d[0], inflow_d[2]],linestyle = '-', linewidth = 0.8, color = 'k')
            axs[1].plot([2-bw/4,2+bw/4],[outflow_d[0], outflow_d[0]],linestyle = '-', linewidth = 0.8, color = 'k')
            axs[1].plot([2-bw/4,2+bw/4],[outflow_d[2], outflow_d[2]],linestyle = '-', linewidth = 0.8, color = 'k')
            axs[1].plot([2,2],[outflow_d[0], outflow_d[2]],linestyle = '-', linewidth = 0.8, color = 'k')
            axs[1].set_ylabel('Billion m²', fontsize = 12)
            axs[1].title.set_text('cumulative flows, \n 2020-2050')
            axs[1].legend(handles = ProxyHandlesList2, labels = ['SSP1 base', 'LED-SSP1-\nSSP2 range'],shadow = False, prop={'size':6},ncol=1, loc = 'upper right')
            axs[1].set_xlim([0,3])
            # plot text and labels
            plt.xticks([1,2])
            axs[1].set_xticklabels(['construction','demolition'], rotation =75, fontsize = 8, fontweight = 'normal', rotation_mode="default")
            # Rotate and align bottom ticklabels
            plt.setp([tick.label1 for tick in axs[1].xaxis.get_major_ticks()], rotation=45,
                     ha="right", va="center", rotation_mode="anchor")
            plt.show()
            fig.savefig(os.path.join(os.path.join(RECC_Paths.export_path,outpath), 'stock pattern_' + pflags[m] + '_' + selectR +'.png'), dpi=150, bbox_inches='tight')
     
        
    if ptypes[m] == 'Fig_MaterialProduction':
        # Custom plot for material production
        for rr in range(0,len(regions)):
            selectR = regions[rr]
            selectS = pscens[m].split(';')
            Data_P  = np.zeros((3,12)) # primary material production
            Mats    = ['Cement production','Primary steel production','Construction wood, structural, from industrial roundwood']
            for mat in range(0,3):
                for sce in range(0,12):
                    pst    = pc[pc['Indicator'].isin([Mats[mat]]) & pc['Region'].isin([selectR]) & pc['Scenario'].isin([selectS[sce]])] # Select the specified data and compile them for plotting        
                    unit = pst.iloc[0]['Unit']
                    Data_P[mat,sce] = pst.iloc[0]['Cum. 2020-2050 (incl.)']
            Data_A  = np.zeros((3,12)) # Outflow: material available for recycling
            Mats = ['Outflow of materials from use phase, cement','Outflow of materials from use phase, construction grade steel','Outflow of materials from use phase, wood and wood products']
            for mat in range(0,3):
                for sce in range(0,12):
                    pst    = pc[pc['Indicator'].isin([Mats[mat]]) & pc['Region'].isin([selectR]) & pc['Scenario'].isin([selectS[sce]])] # Select the specified data and compile them for plotting        
                    unit = pst.iloc[0]['Unit']
                    Data_A[mat,sce] = pst.iloc[0]['Cum. 2020-2050 (incl.)']
            Mats = 'Outflow of materials from use phase, concrete'
            for sce in range(0,12):
                pst    = pc[pc['Indicator'].isin([Mats]) & pc['Region'].isin([selectR]) & pc['Scenario'].isin([selectS[sce]])] # Select the specified data and compile them for plotting        
                Data_A[0,sce] += pst.iloc[0]['Cum. 2020-2050 (incl.)']* 0.15 # cement in concrete waste
            Data_S  = np.zeros((3,12)) # Actual re-use and recycling, including wood cascading
            Mats    = ['ReUse of materials in products, concrete','ReUse of materials in products, construction grade steel','ReUse of materials in products, wood and wood products']
            for mat in range(0,3):
                for sce in range(0,12):
                    pst    = pc[pc['Indicator'].isin([Mats[mat]]) & pc['Region'].isin([selectR]) & pc['Scenario'].isin([selectS[sce]])] # Select the specified data and compile them for plotting        
                    unit = pst.iloc[0]['Unit']
                    Data_S[mat,sce] = pst.iloc[0]['Cum. 2020-2050 (incl.)']            
            Data_S[0,:] = Data_S[0,:] * 0.15 # cement in concrete re-use
            Mats = 'Cascading of wood'
            for sce in range(0,12):
                pst    = pc[pc['Indicator'].isin([Mats]) & pc['Region'].isin([selectR]) & pc['Scenario'].isin([selectS[sce]])] # Select the specified data and compile them for plotting        
                Data_S[2,sce] += pst.iloc[0]['Cum. 2020-2050 (incl.)']            
            Mats = 'Secondary construction steel'
            for sce in range(0,12):
                pst    = pc[pc['Indicator'].isin([Mats]) & pc['Region'].isin([selectR]) & pc['Scenario'].isin([selectS[sce]])] # Select the specified data and compile them for plotting        
                Data_S[1,sce] += pst.iloc[0]['Cum. 2020-2050 (incl.)']                            
            
            # Add secondary flows to primary to get total material production for new buildings
            Data_P += Data_S
            
            # Prepare plot
            c_a = np.array([[230,230,230],[207,214,223],[225,219,117]])/255# cement gray, steel blue, and wood brown, very light
            c_s = np.array([[167,167,167],[172,185,202],[191,143,0]])/255# cement gray, steel blue, and wood brown, light
            c_m = np.array([[120,120,120],[73,93,117],[142,105,0]])/255# cement gray, steel blue, and wood brown, dark
            
            # plot results
            bw = 0.35
            
            LLeft   = -0.5
            XTicks  = np.arange(0,6,1)
            lwi      = [0,0,0,0,0,0]
            
            fig  = plt.figure(figsize=(8,5))
            ax1  = plt.axes([0.08,0.08,0.85,0.9])
            plt.xlim([-0.4,5.7])
            ax2  = ax1.twiny()
        
            ProxyHandlesList = []   # For legend     
            ProxyHandlesList.append(plt.fill_between([0,0], [0,0],[0,0],linestyle = '-', facecolor = c_m[0,:], linewidth = 0, edgecolor = 'k'))
            ProxyHandlesList.append(plt.fill_between([0,0], [0,0],[0,0],linestyle = '-', facecolor = c_m[1,:], linewidth = 0, edgecolor = 'k'))
            ProxyHandlesList.append(plt.fill_between([0,0], [0,0],[0,0],linestyle = '-', facecolor = c_m[2,:], linewidth = 0, edgecolor = 'k'))
            
            # plot bars
            for sce in range(0,6):
                for mat in range(0,3):
                    # top row:
                    ax1.fill_between([sce-bw/2,sce+bw/2], [Data_P[0:mat,sce].sum(),Data_P[0:mat,sce].sum()],[Data_P[0:mat+1,sce].sum(),Data_P[0:mat+1,sce].sum()],linestyle = '-', facecolor = c_m[mat,:], linewidth = lwi[sce], edgecolor = 'k')
                    ax1.fill_between([sce+bw/2,sce+1.5*bw],   [Data_P[0:mat,sce].sum(),Data_P[0:mat,sce].sum()],[Data_P[0:mat,sce].sum()+Data_A[mat,sce],Data_P[0:mat,sce].sum()+Data_A[mat,sce]],linestyle = '-', facecolor = c_a[mat,:], linewidth = 0, edgecolor = 'k')
                    ax1.fill_between([sce+bw/2,sce+1.5*bw],   [Data_P[0:mat,sce].sum(),Data_P[0:mat,sce].sum()],[Data_P[0:mat,sce].sum()+Data_S[mat,sce],Data_P[0:mat,sce].sum()+Data_S[mat,sce]],linestyle = '-', facecolor = c_m[mat,:], linewidth = 0, edgecolor = 'k')
                    # bottom row:
                    ax1.fill_between([sce-bw/2,sce+bw/2], [-Data_P[0:mat,sce+6].sum(),-Data_P[0:mat,sce+6].sum()],[-Data_P[0:mat+1,sce+6].sum(),-Data_P[0:mat+1,sce+6].sum()],linestyle = '-', facecolor = c_m[mat,:], linewidth = lwi[sce], edgecolor = 'k')
                    ax1.fill_between([sce+bw/2,sce+1.5*bw],   [-Data_P[0:mat,sce+6].sum(),-Data_P[0:mat,sce+6].sum()],[-Data_P[0:mat,sce+6].sum()-Data_A[mat,sce+6],-Data_P[0:mat,sce+6].sum()-Data_A[mat,sce+6]],linestyle = '-', facecolor = c_a[mat,:], linewidth = 0, edgecolor = 'k')
                    ax1.fill_between([sce+bw/2,sce+1.5*bw],   [-Data_P[0:mat,sce+6].sum(),-Data_P[0:mat,sce+6].sum()],[-Data_P[0:mat,sce+6].sum()-Data_S[mat,sce+6],-Data_P[0:mat,sce+6].sum()-Data_S[mat,sce+6]],linestyle = '-', facecolor = c_m[mat,:], linewidth = 0, edgecolor = 'k')
            # replot BASE scenario frame
            ax1.add_patch(Rectangle((3-bw/2, 0), bw, Data_P[:,3].sum(),  edgecolor = 'k', facecolor = 'blue', fill=False, lw=2))
            ax1.add_patch(Rectangle((3-bw/2, 0), bw, -Data_P[:,3].sum(), edgecolor = 'k', facecolor = 'blue', fill=False, lw=2))
            # horizontal 0 line
            ax1.plot([-0.4,5.7],[-0.4,5.7],linestyle = '-', linewidth = 1, color = 'k')
    
            # plot text and labels
            title_add = '_2020-50'
            title = ptitles[m] + '_' + selectR + title_add
            plt.title(title, fontsize = 18)
            plt.ylabel(unit, fontsize = 18)
            plt.xticks(XTicks)
            ax1.set_xticklabels(selectS[5::], rotation =75, fontsize = 11, fontweight = 'normal', rotation_mode="default")
            ax2.set_xlim(ax1.get_xlim())
            ax2.set_xticklabels(selectS[0:6], rotation =75, fontsize = 11, fontweight = 'normal', rotation_mode="default")
            # Rotate and align bottom ticklabels
            plt.setp([tick.label1 for tick in ax1.xaxis.get_major_ticks()], rotation=45,
                     ha="right", va="center", rotation_mode="anchor")
            # # Rotate and align top ticklabels
            plt.setp([tick.label2 for tick in ax2.xaxis.get_major_ticks()], rotation=45,
                     ha="left", va="center",rotation_mode="anchor")
            ylabels = [item.get_text() for item in ax1.get_yticklabels()]
            for yl in range(0,len(ylabels)):
                if ylabels[yl].find('−') > -1:
                    ylabels[yl] = ylabels[yl][1::]
                if ylabels[yl] == '0':
                    ylabels[yl] = 'Mt   0'
            ax1.set_yticklabels(ylabels)
            plt.text(0.3, Data_P[:,3].sum() *0.08, 'narrow', fontsize=18, fontweight='normal')     
            plt.text(3.4, Data_P[:,3].sum() *0.08, 'wood-intensive', fontsize=18, fontweight='normal')     
            plt.text(0.3, -Data_P[:,3].sum()*0.12, 'slow+close', fontsize=18, fontweight='normal')     
            plt.text(3.4, -Data_P[:,3].sum()*0.12, 'all together', fontsize=18, fontweight='normal')     
            plt.legend(handles = ProxyHandlesList, labels = ['cement','steel','wood'],shadow = False, prop={'size':11},ncol=1, loc = 'upper left') # ,bbox_to_anchor=(2.18, 1)) 
            #plt.legend(handles = ProxyHandlesList,labels = CLabels,shadow = False, prop={'size':12},ncol=1, loc = 'upper right' ,bbox_to_anchor=(2.18, 1)) 
            #plt.axis([-0.2, 7.7, 0.9*Right, 1.02*Left])
            #plt.axis([-0.2, LLeft+bw/2, 0, 1.02*Left])
            
            plt.show()
            fig.savefig(os.path.join(os.path.join(RECC_Paths.export_path,outpath), title +'.png'), dpi=150, bbox_inches='tight')

#
#
#
#
# The end.
#
#    