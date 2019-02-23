# -*- coding: utf-8 -*-
#!/usr/bin/python

# LIBRERIAS
import numpy as np
import time
import os
import errno
from glob import glob
from tqdm import tqdm
from osgeo import ogr, gdal, osr
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.signal import savgol_filter
import calendar


# FUNCIONES
# 01. list_datasets genera una lista de todos los datasets en un hdf
def list_hdf_dataset(x):
    """
    esta función toma un sólo archivo hdf, de tal forma que muestra
    una lista de los subdatasubsets presentes y sus respectivos nombres
    """
    lista=[]
    img_dst = gdal.Open(x, gdal.GA_ReadOnly)
    aa = (img_dst.GetSubDatasets())
    for i in range(0, int(np.size(aa)/2)):
        #print(', '.join((str(i), aa[i][-1])))
        #lista.append(aa[i][-1])
        lista.append((', '.join((str(i), aa[i][-1]))))
    return(lista)


# 02. hdf_metada permite obtener metadata para generacion de geotif.
def hdf_metadata(i):
    """
    hdf_metadata, genera un diccionario de variables con parte del metadata de la
    hdf, de forma de acceso rapido.
    """
    hdf = gdal.Open(i, gdal.GA_ReadOnly)
    # selecciona el dataset correspondiente que interesa
    dst = gdal.Open(hdf.GetSubDatasets()[0][0], gdal.GA_ReadOnly)
    # lee la banda correspondiente al dataset
    img = dst.GetRasterBand(1)
    # todos los datos de geotransform de los la banda
    ulx, xres, xskew, uly, yskew, yres  = dst.GetGeoTransform()
    return({
           # todo lo geo transformacion
           'geotransform':dst.GetGeoTransform(),
           # nombre del hdf
           # 'nom_ds':dst,
           # nombre de la banda / banda
           # 'nom_im':img,
           # cordenada x upper left
           #'ulx':ulx,
           # resolucion x
           #'xres':xres,
           # coordenadas y upper left
           #'uly':uly,
           # deformacion / skew
           #'yskew':yskew,
           # resolucion de y
           #'yres':yres,
           #cantidad de x filas
           'xsize':dst.RasterXSize,
           # cantidad de y columnas
           'ysize':dst.RasterYSize,
           # factor de transformacion de los datos a unidades fisicas
           'factor':img.GetScale(),
           # Valor NoData de la capa
           'nodata':img.GetNoDataValue(),
           # unidad de precision del dato float32 / int16 etc
           'producto':img.GetUnitType(),
           # proyeccion original del dato
           'proyeccion':dst.GetProjection(),
           # listado de capas de informacion presentes.
           'list_subset':list_hdf_dataset(i),
           })

# 03. generacion de año decimal para la serie de datos
def decimal_year(HDF):
    """
    estimacion de año decimal, en base a la obtencion de los datos
    """
    # lista de datos
    lista=[]
    for i in HDF:
        fecha =((i.split('\\')[-1]).split('.')[1]).split('A')[-1]
        # estima la division del año decimal en base si es o no
        # un año bisiesto
        if calendar.isleap(np.float(fecha[:4]))=='FALSE':
            decimal = np.float(fecha[:4]) + np.float(fecha[-3:])/365
        else:
            decimal = np.float(fecha[:4]) + np.float(fecha[-3:])/366
        lista.append(decimal)
    # guarda los datos como un arreglo de numpy
    lista=np.stack(lista, axis=0)
    return(lista)


def decimal_year_365(HDF):
    """
    estimacion de año decimal, en base a la obtencion de los datos
    """
    # lista de datos
    lista=[]
    for i in HDF:
        fecha =((i.split('\\')[-1]).split('.')[1]).split('A')[-1]
        # fecha = fecha * 1.0
        # estima la division del año decimal en base si es o no
        # un año bisiesto
        if calendar.isleap(np.float(fecha[:4]))=='FALSE':
            decimal = np.float(fecha[:4]) + np.float(fecha[-3:])/365
        else:
            decimal = np.float(fecha[:4]) + np.float(fecha[-3:])/365
        lista.append(decimal)
    # guarda los datos como un arreglo de numpy
    lista=np.stack(lista, axis=0)
    return(lista)



# 04. imagen raster a un arreglo de python
def rst_2_arr(x):
    """
    rst_2_arr: como su nombre indica, transforma una lista de ubicaciones
    de imágenes tipo raster, que leer y agrupa de manera ordenada, en
    formato array. columna imagen, fila pixel
    """
    lista = []
    for i in tqdm(x):
        # lee todos los archivos / raster.
        img_dst = gdal.Open(i, gdal.GA_ReadOnly)
        bnd_dst = img_dst.GetRasterBand(1)
        # data_type = gdal.GetDataTypeName(bnd_ds.DataType)
        bnd_mat = bnd_dst.ReadAsArray()
        # atriz a vector, usando orden 'C'
        img_vec = bnd_mat.flatten('C')
        # array_ = bnd_ar.flatten('C').astype(np.float16)
        lista.append(img_vec)
        # arroja array como resultado, y se eliminan variables
        # temporales de memoria
    img_ts = np.stack(lista, axis=0)
    img_ts = np.transpose(img_ts)
    return(img_ts)


# 05. HDF A ARRAY
def hdf_2_arr(hdf, sd):
    """
    hdf_2_arr: como su nombre indica, transforma una lista de ubicaciones
    de archivos HDF, seleccionando UN determinado subdataset, y agrupa
    los datos asociados de manera ordenada, en formato array:
    columna imagen, fila pixel
    """
    lista = []
    for i in tqdm(hdf):
        # lee los archivos HDF
        hdf_ds = gdal.Open(i, gdal.GA_ReadOnly)
        # selecciona el dataset correspondiente que interesa
        img_ds = gdal.Open(hdf_ds.GetSubDatasets()[sd][0], gdal.GA_ReadOnly)
        # lee la banda correspondiente al dataset
        bnd_ds = img_ds.GetRasterBand(1)
        # transforma el dataset a un numpy array
        bnd_ar = bnd_ds.ReadAsArray()
        # transforma el array a un vector correspondiente a la imagen
        vector = bnd_ar.flatten('C')
        # toma la lista y agrega los vectores entorno al eje 0
        lista.append(vector)
    # transforma la lista en un numpy array de tiempo
    img_ts = np.stack(lista, axis=0)
    # arroja array como resultado, y se eliminan variables
    # temporales de memoria
    img_ts = np.transpose(img_ts)
    return(img_ts)


# 06. spline_ts relleno de serie de datos mediante spline
def spline_ts(SerieTiempo, NoData):
    """
    """
    nsize = np.size(SerieTiempo)
    tipo = SerieTiempo.dtype
    #
    if sum(np.equal(SerieTiempo, NoData)) == 0:
        SerieTiempo_relleno = SerieTiempo
    elif sum(np.equal(SerieTiempo, NoData)) >= (nsize / 2.0) :
        SerieTiempo_relleno = np.full(nsize, NoData)
    elif sum(np.equal(SerieTiempo, NoData)) < (nsize / 2.0) :
        # generar una serie de datos ordinales, para armar spline
        ordX = np.column_stack((np.arange(0, SerieTiempo.size, dtype=tipo), SerieTiempo))
        # se crea la funcion spline de los datos con información valida
        spl = InterpolatedUnivariateSpline(
                ordX[np.logical_not(np.equal(SerieTiempo, NoData))][:, 0],
                (ordX[np.logical_not(np.equal(SerieTiempo, NoData))][:, 1]))
        # genera datos interpolados por spline
        n2 = np.asarray((spl(range(SerieTiempo.size))), dtype=tipo)# * 1000
        # busca los indices para reemplazar los valores dentro de la serie
        idx = np.argwhere(np.equal(SerieTiempo, NoData))
        # reemplaza solo aquellos valores no existentes en la serie original
        ordX[idx, 1] = n2[idx]
        n3 = signal.savgol_filter(ordX[:, 1], 11, 2, mode='wrap')
        ordX[idx, 1] = n3[idx]
        # salida final de datos
        SerieTiempo_relleno = ordX[:, 1]
    return(SerieTiempo_relleno)

def sav_gol(serie_tiempo_rellenada):
    lista = []
    for i in tqdm(np.arange(0, serie_tiempo_rellenada.shape[0])):
        filled = savgol_filter(serie_tiempo_rellenada[i, :], 11, 2,
                               mode='wrap')
        filled = np.array(filled, dtype = np.int16)
        lista.append(filled)
    return(np.stack(lista, axis=0))

