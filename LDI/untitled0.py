# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 17:13:37 2021

@author: vidar
"""
import numpy as np
yorig = -100
yend = 0
y = 5
rad = 5
while yorig<y<yend and rad>0.01: 
    y+=1
    print(y)

testarray = np.array([[0,1],[1,1],[2,2]])