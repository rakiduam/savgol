# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 17:36:39 2018
Title: Analisis / Relleno NDVI MODIS. Savitzky-Golay 

la idea, leer imagenes de NDVI (series de tiempo). Luego analizar a nivel de pixel,
y generar un analisis de calidad y relleno de datos mediante algún algoritmo.

- Lee imagenes HDF / TIF (en este caso se esta trabajando en TIF, 
    pero puede funcionar en con HDF)
- Separa en subsets de datos, en series de tiempo por pixel
- "Relleno" de datos faltantes. (actualmente en spline, comparar otros metodos)

FALTA:
- mejorar convenciones del codigo para "lectura"
- optimizar el codigo
- probar otros metodos de datos
- "chequear uso de anomalia"
- comparar resultados

es que este script lea las imagenes separadas en base a cada uno de los productos
luego ejecute un filtro en modis eliminando aquellos pixeles con una 
mala calidad de datos en aquellos casos donde los datos disponibles sean menos 
del 80% el pizzel se evalura como un no data

este proceso esta separado en diferentes etapas, es de tipo experimental, por lo que no 
es optimizado.

existe otras formas de hacer un año tipo de las imagenes.

@author: fanr / rakiduam
"""


################################################
## librerias
################################################
import multiprocessing
import numpy as np
import os

from tqdm import tqdm

from glob import glob

from osgeo import gdal

from scipy.signal import savgol_filter

from scipy.interpolate import InterpolatedUnivariateSpline



################################################
## SUBRUTINA 00: SUBFUNCIONES CORTAS DEL CODIGO
################################################

## A. SPLINE, RELLENO DATOS FALTANTES
def spl(x):
    corte=39
    if sum(np.isnan(x)) == 0:
        #print( '=0 ' + str(sum(~np.isnan(x)) ) )
        im = x
    elif sum(np.isnan(x)) < corte:
        #print( '+0 < 22 ' + str(sum(~np.isnan(x)) ) )
        
        n1 = np.column_stack((np.arange(0, x.size,dtype=x.dtype), x) )
        
        spline = InterpolatedUnivariateSpline(n1[np.logical_not(np.isnan(x))][:,0],
                                              n1[np.logical_not(np.isnan(x))][:,1],
                                              ext=0)
        n2 = spline(range(x.size))
        
        n1[np.argwhere(np.isnan(x)),1] = n2[np.argwhere(np.isnan(x))]
        
        im = n1[:,1]
        
    elif sum(np.isnan(x)) > corte:
        #print( '22> infinito ' + str(sum(~np.isnan(x)) ) )
        im = np.full(np.size(x), np.nan)
    
    return (im);


################################################
## DIRECTORIOS
################################################
imgMOD='MOD13A2'
#entDIR=('/home/'+ str(os.environ.get('USER')) +'/disco2/version00/'+imgMOD+'/')
entDIR=('/home/'+ str(os.environ.get('USER')) +'/disco2/'+imgMOD+'/Subset1/')
salDIR=('/home/'+ str(os.environ.get('USER')) +'/disco2/' + 'version01' + '/' )



################################################
## SUBRUTINA 01: SERIES DE TIEMPO DESDE IMAGENES
################################################

#lista imagenes datos
TIFS=glob(entDIR + '/????/'+imgMOD+'_???????.tif')
#TIFS=glob(entDIR +imgMOD+'.A???????.h11v10.006.*-sd1.tif')

for img in tqdm(TIFS):
  #print(img)
  tif = gdal.Open(img)
  band=tif.GetRasterBand(1)
  bandArray=band.ReadAsArray()
  #bandArray=bandArray
  # row                    ;    # col
  row=bandArray.shape[0] ; col=bandArray.shape[1]
  
  # la forma en que se reordena los datos, de matriz a vector. de forma explicita.
  b1=np.array(np.reshape(bandArray,col*row, order='C'))
  
  # generacion de nuevo array "temporal", para serie de tiempo
  if img==TIFS[0]:
    gtARRAY=b1
  else:
    gtARRAY=np.column_stack((gtARRAY, b1))
    
    


gtARRAY[gtARRAY<=-3.4e+37]=['NaN']



################################################
## SUBRUTINA 02: RELLENO DE SERIES DE TIEMPO
################################################

# aplica una funcion a todos los elementos, dentro del array
# la funcion "spline", previamente definida, al eje vertical

bb=np.apply_along_axis(spl, -1, gtARRAY)


# a=0
# for i in tqdm(gtARRAY[:,]):
#   if a==0:
#     sal_im = spl(i)
#     a=a+1
#   else:
#     sal_im = np.vstack((sal_im, spl(i)))



################################################
## SUBRUTINA 03: ESCRITURA DATOS A DE GEOTIF 
################################################

## OJO que aun se mantiene el ultimo objeto tif en memoria
## de ahi planeo extraer la infomracion de salida.

count = 0 # debido a que es una suerte de contador recurrente, lo reseteo a 0
for img in tqdm(TIFS):
  print img



  # tif.RasterXSize; tif.RasterYSize
  b0=bb[:,count].reshape(( tif.RasterXSize, tif.RasterYSize))
  
  nombre=salDIR+imgMOD+'/'+(img.split('/')[-1]).split('.')[-2]+'_v'+str(1).zfill(2)+'.tif'
  
  out_ds = gdal.GetDriverByName('GTiff').Create(nombre, # filename salida
                                                tif.RasterXSize, # dim lon
                                                tif.RasterYSize, # dim lat
                                                1, # numero de bandas
                                                gdal.GDT_Float32, # dato salida
                                                ['COMPRESS=LZW', # tipo de compresion
                                                'TILED=YES'])
  out_ds.SetGeoTransform(tif.GetGeoTransform())
  out_ds.SetProjection(tif.GetProjection())
  out_ds.GetRasterBand(1).WriteArray(b0) # dato que debe escribir. debe ser caso es dinamico.
  out_ds.GetRasterBand(1).SetNoDataValue('NaN')
  out_ds = None
  
  count=1+count







###############################################################################
###############################################################################
###############################################################################
### OLD CODE
###############################################################################
###############################################################################
###############################################################################
# # paquetes necesarios de python
# import os, errno
# from osgeo import gdal
# from glob import glob
# from scipy.signal import savgol_filter
# #from scipy.signal import savgol_coeffs
# import matplotlib.pyplot as plt

# import numpy as np
# #import pandas as pd

# # directorios de trabajo de los datos
# imgMOD = ('MOD13Q1')
# entDIR = ('I:\\version00\\MOD13Q1\\subset_00\\')
# salDIR = ('I:\\' + 'version01' + '\\' )

# # chequea si existe el directorio de salida y sino, lo crea.
# try:
#     os.makedirs(salDIR)
# except OSError as e:
#     if e.errno != errno.EEXIST:
#         raise

# # MOD13Q1.A2001017.h11v10.006.2015140091834-sd1.tif
# # 'E:\\version00\\MOD13Q1\\subset_00\\MOD13Q1.A????.001.h11v11.006.-sd1.tif'
# #HDF = glob(entDIR  + imgMOD +'.A' + '????' + str(1).zfill(3) + '.h11v11.' + '006.' + '*-sd1.tif')
# HDF = glob(entDIR  + imgMOD +'.A' + '*' + '.h11v11.' + '006.' + '*-sd1.tif')
# count = 1

# # generacion de la serie de tiempo a partir de las imagenes disponibles
# # reshape de la imagen a un vector y en un subset de pixeles (por memoria)
# for hdf in HDF:
#     tif=gdal.Open(hdf)
#     band = tif.GetRasterBand(1)
#     # subset de pixeles. Esto eventualmente debe hacerse hasta que se complete la imagen
#     bandArray = band.ReadAsArray()[100:200,:]
#     #bandArray=bandArray
#     # row                    ;    # col
#     row = bandArray.shape[0] ; col = bandArray.shape[1]
#     # la forma en que se reordena los datos, de matriz a vector. de forma explicita.
#     b1=np.array(np.reshape(bandArray,col*row, order='C'))
    
#     # generacion de nuevo array "temporal"
#     if count == 1:
#         gTifArray = b1
#     else:
#         gTifArray = np.column_stack((gTifArray, b1))
    
#     count=count+1

# # sanidad de variables. aunque podria ser "recurrente"
# del (b1, band, bandArray, count) 

# # pseudo tranformacion de enteros 16bit a valores de ndvi ( 0.0001 )
# # esto hace que el arreglo original de 16 bit, se transforme a 64bit
# # lo que hace que la memoria ram usada aumente.
# aa = np.ones(gTifArray.shape)*gTifArray

# # debido a que el NoData original, en el TIF se representa como -3000
# # se corrige el valores a un -99999, para luego transformar a
# # NaN. Este paso podria simplificarse y ser más directo.
# aa[aa == -3000] = [-99999]
# aa=aa*0.0001
# aa[aa == -9.9999] = ['NaN']

# # este paso es para generar un relleno de datos mediantel el uso de una 
# # funcion tipo spline. En este caso debido a que los valores no son se 
# x1 = np.array(aa[11600]) #; x;x.shape[0]
# x2 = np.column_stack( (np.arange(1,391), x1) )
# x3 = x2[np.logical_not(np.isnan(x1))]

# #filtrado de la serie se eliminan aquellos datos tipo NaN
# x2[x2[:,:] != 'NaN']

# #y1 = savgol_filter(x, 5, 2, mode='wrap'); print(y1)

# from scipy.interpolate import InterpolatedUnivariateSpline

# print(range(1,x1.shape[0]))

# spl = InterpolatedUnivariateSpline(np.arange(1,391), x1, ext=0)

# spl = InterpolatedUnivariateSpline(x3[0:295,0], x3[0:295,1], ext=0)
# sav = savgol_filter(x3[0:295,1], 5, 2, mode='nearest')

# spl(np.arange(1,391))

# a=np.convolve(x1, x2, 'same')

# import matplotlib.pyplot as plt
# plt.plot(np.arange(1,391), x1, 'ro', ms=5)
# plt.plot(np.arange(1,391), spl(np.arange(1,391)), 'g', lw=3, alpha=0.7)
# plt.plot( x3[0:295,0], sav, 'b', lw=4, alpha=0.7)
# plt.show()

# # array vacio que se reemplazaran los valores para mantener el filtro calculado
# # por savitzky golay.
# #vacio = np.empty((gTifArray.shape[0], gTifArray.shape[1]), dtype = np.int64)
# #gTifArray.dtype=np.float64

# ### anomalia estandirizada.
# #def anom(x):
# #    (x-np.mean)/np.std(x)
# #
# ##import matplotlib
# #np.mean(x)
# #np.std(x)

# #ts_df = pd.DataFrame(np.random.random(size=(365, 30000)))
# #aa=pd.read_hdf(entDIR+'\\MOD11A2.A2001001.h11v10.006.2015111234607.hdf', key=None, mode='r')
