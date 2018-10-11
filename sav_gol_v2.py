# -*- coding: utf-8 -*-
"""

version semi operativa.
limpiar codigo y guardar como tif.. y cambiar nombre en caso de no seguir con savitky

Created on Thu Sep 13 17:36:39 2018
Title: SAvitzky-Golay final final final del fin pre ultimo
la idea es que este script lea las imagenes separadas en base a cada uno de los productos
luego ejecute un filtro en modis eliminando aquellos pixeles con una mala calidad de datos
en aquellos casos donde los datos disponibles sean menos del 80% el pizzel se evalura como un no
data

este proceso esta separado en diferentes etapas, es de tipo experimental, por lo que no 
es optimizado.

existe otras formas de hacer un año tipo de las imagenes.

@author: fanr
"""

import os, errno
from osgeo import gdal
from glob import glob
from scipy.signal import savgol_filter
#from scipy.signal import savgol_coeffs
#from scipy.signal import savgol_coeffs
#import matplotlib.pyplot as plt

import numpy as np
#import pandas as pd

imgMOD = ('MOD13Q1')
entDIR = ('I:\\version00\\MOD13Q1\\subset_00\\')
salDIR = ('I:\\' + 'version01' + '\\' )

try:
    os.makedirs(salDIR)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

#path, dirs, files = next(os.walk("D:\\" + imgMOD))
#fil=pd.DataFrame.from_records(files)
#file_count = len(str(files))
#pd.Series([2, 1, 3, 3], name='A').unique()

# MOD13Q1.A2001017.h11v10.006.2015140091834-sd1.tif
# 'E:\\version00\\MOD13Q1\\subset_00\\MOD13Q1.A????.001.h11v11.006.-sd1.tif'
#HDF = glob(entDIR  + imgMOD +'.A' + '????' + str(1).zfill(3) + '.h11v11.' + '006.' + '*-sd1.tif')
HDF = glob(entDIR  + imgMOD +'.A' + '*' + '.h11v11.' + '006.' + '*-sd1.tif')
count = 1

for hdf in HDF:
    
    tif=gdal.Open(hdf)
    band = tif.GetRasterBand(1)
    bandArray = band.ReadAsArray()[100:200,:]
    #bandArray=bandArray
    # row                    ;    # col
    row = bandArray.shape[0] ; col = bandArray.shape[1]

    b1=np.array(np.reshape(bandArray,col*row, order='C'))

    if count == 1:
        gTifArray = b1
    else:
        gTifArray = np.column_stack((gTifArray, b1))
    
    count=count+1

del (b1, band, bandArray, count) 

#0.0001 ndvi transform value
aa = np.ones(gTifArray.shape)*gTifArray
aa[aa == -3000] = [-99999]
aa=aa*0.0001
aa[aa == -9.9999] = ['NaN']

x1 = np.array(aa[11600]) #; x;x.shape[0]
x2 = np.column_stack( (np.arange(1,391), x1) )
x3 = x2[np.logical_not(np.isnan(x1))]

x2[x2[:,:] != 'NaN']

#y1 = savgol_filter(x, 5, 2, mode='wrap'); print(y1)

from scipy.interpolate import InterpolatedUnivariateSpline

print(range(1,x1.shape[0]))

spl = InterpolatedUnivariateSpline(np.arange(1,391), x1, ext=0)

spl = InterpolatedUnivariateSpline(x3[0:295,0], x3[0:295,1], ext=0)
sav = savgol_filter(x3[0:295,1], 5, 2, mode='nearest')

spl(np.arange(1,391))

a=np.convolve(x1, x2, 'same')


import matplotlib.pyplot as plt
plt.plot(np.arange(1,391), x1, 'ro', ms=5)
plt.plot(np.arange(1,391), spl(np.arange(1,391)), 'g', lw=3, alpha=0.7)
plt.plot( x3[0:295,0], sav, 'b', lw=4, alpha=0.7)
plt.show()

# array vacio que se reemplazaran los valores para mantener el filtro calculado
# por savitzky golay.
#vacio = np.empty((gTifArray.shape[0], gTifArray.shape[1]), dtype = np.int64)
#gTifArray.dtype=np.float64

#x=gTifArray[gTifArray==-3000]=['NaN']

#x=np.array(aa[6772],dtype='float64'); x;x.shape[0]
#x[x==-3000]=['NaN'];x 
#
#for i in range(6772, 6772+100):
#    
#    x = gTifArray[i] #; x
#    r = x[x==-3000]  #; r; r.shape[0]
#    
#    if r.shape[0] > 15:
#        #nada
#        y1 = savgol_filter(x, 5, 2, mode='nearest'); print(y1)
#    else:
#        y2 = savgol_filter(r, 5, 2, mode='nearest'); print(y2)
#        #w2 = savgol_coeffs(5,2)
#    
#    print(i)
#





### anomalia estandirizada.
#def anom(x):
#    (x-np.mean)/np.std(x)
#
##import matplotlib
#np.mean(x)
#np.std(x)

#ts_df = pd.DataFrame(np.random.random(size=(365, 30000)))
#aa=pd.read_hdf(entDIR+'\\MOD11A2.A2001001.h11v10.006.2015111234607.hdf', key=None, mode='r')
