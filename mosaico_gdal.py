#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on Mon Feb 17 12:50:48 2019

@author: fanr

NOTAS:
  - Proceso, "lento", lectura/escritura mosaico virtual de gdal (*.VRT),
   reproyección a WGS84 (EPGS:4326) y recorte "grueso" a limites de chile
   continental, en geotif (*.tif)
  - Se corrige el problema que tenía de "desviacion" de medio grado en la
   proyeccion WGS84
  - Datos de salida en valores de origen, es decir, se hace necesaria la
   transformacion, de los datos a sus unidades según producto MODIS;
   0.0001 en MOD13xx y 0.02 MOD11xx, verificar.
  - Proceso total, en mi computador, toma aprox. 30 minutos para la serie de un
   producto-proceso

IMPORTANTE:
    - revisar carpeta de salida
    - revisar nombres de salida
    -
"""


# importar librerias necesarias para procesamiento
from osgeo import gdal
import glob
import os

# directorio de trabajo
os.chdir("D:/version01/MOD13A2/ndvi/03.savgol/")
os.getcwd()

# producto modis a procesar, solo por referencia de nombre
imgMOOD = 'MOD13A2'
# periocidad temporal del producto MO13A2 16días, MOD13Q1 8 días
step = 16  ## eventualmente se puede dejar en 1, solo tomara mas tiempo proceso.

# sistema de coordenadas del proceso, son constantes.
coordENT = "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs"
coordSAL = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
limites = (-76.5, -68.0, -56.0, -16.8)  ## en sistema salida

# ciclo lectura / escritura mosaicos y generacion datos salida
for year in range(2001, 2018):
    year = str(year)
    for day in range(1, 366, step):
        day = str('%0.3d' % day)  ## genera dia con pad de 0, ej; 001, 017, etc.
        # nombre archivo de salida, corregir acorde idea.
        outfile = imgMOOD + ".A" + year + day + ".savgol."
        # generacion de mosaico en formato virtual gdal, liviano, no mas de 4 mb
        gdal.BuildVRT(outfile + "VRT",
                      ## aquí genera lista de archivos por día
                      glob.glob(imgMOOD + ".A" + year + day + "*.savgol.tif"))

        # generación de reproyeccion de los datos, se define formato,
        # coordenadas entrada, coordenadas salida, limites proceso
        ds = gdal.Warp(('D:/mosaico/' + outfile + "tif"),
                       (outfile + "VRT"),
                       srcSRS = coordENT,
                       dstSRS = coordSAL,
                       outputBounds = limites,  ## outputBounds = (minX, minY, maxX, maxY)
                       )
        ds = None  ## se libera memoria / cierra archivo














# importar librerias necesarias para procesamiento
from osgeo import gdal
import glob
import os

# directorio de trabajo
# cd '/home/lares01/disco2/version01_ene-2019/MOD11A2/TILES/lst-day/03.savgol/2001'
os.chdir('/home/lares01/disco2/version01_ene-2019/MOD11A2/TILES/lst-day/03.savgol/')
os.getcwd()  ## directorio actual

# producto modis a procesar, solo por referencia de nombre
imgMOD = 'MOD11A2'
# periocidad temporal del producto MO13A2 16días, MOD13Q1 8 días
step = 8  ## eventualmente se puede dejar en 1, solo tomara mas tiempo proceso.

# sistema de coordenadas del proceso, son constantes.
# http://spatialreference.org
# SR-ORG:6842
coordENT = "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs"
# EPGS:4326
coordSAL = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
limites = (-76.5, -68.0, -56.0, -16.8)  ## en sistema coordenadas de salida

# ciclo lectura / escritura mosaicos y generacion datos salida
for year in range(2001, 2018):
    year = str(year)
    for day in range(1, 366, step):
        day = str('%0.3d' % day)  ## genera dia con pad de 0, ej; 001, 017, etc.
        # nombre archivo de salida, corregir acorde idea.
        outfile = imgMOD + ".A" + year + day + ".mosaic.savgol."
        # lista de archivos a generar en mosaico
        mosaico_lista = glob.glob(year +'/'+ imgMOD + ".A" + year + day + "*.savgol.tif")
        # test de si existen las imagenes
        if not mosaico_lista:
            print(('').join(['     sin imagenes ', day]))
        elif mosaico_lista:
            # genera mosaico formato virtual gdal, liviano, no mas de 4 mb
            gdal.BuildVRT(year + '/' + outfile + "VRT", mosaico_lista)

# aqui solo elimino las variables que no se usaran más adelante.
del mosaico_lista, outfile, year, day

# ciclo de mosaico reproyectado.
for year in range(2001, 2018):
    year = str(year)
    patron_file = imgMOD + ".A" + year + "*.mosaic.savgol."
    mosaico_lista_tif = glob.glob(year + '/' + patron_file + "VRT")
    # ciclo de reproyeccion / escritura mosaico GEOTIF
    for mosaico_vrt in mosaico_lista_tif:
        ds = gdal.Warp(('MOSAIC/' + mosaico_vrt[5:-3] + "tif"),
                       mosaico_vrt,
                       srcSRS = coordENT,
                       dstSRS = coordSAL,
                       ## outputBounds = (minX, minY, maxX, maxY)
                       outputBounds = limites,
                       )
        ds = None  ## se libera memoria / cierra archivo


















