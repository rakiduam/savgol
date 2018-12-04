# -*- coding: utf-8 -*-
#!/usr/bin/python

# LIBRERIAS
from glob import glob
from osgeo import gdal
from tqdm import tqdm
import numpy as np
import time
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy import signal


# DEFINICION DE FUNCIONES #############################
# funcion, obtener metadata de los datos.
def metadata(i):
    hdf = gdal.Open(i, gdal.GA_ReadOnly)
    # selecciona el dataset correspondiente que interesa
    dst = gdal.Open(hdf.GetSubDatasets()[0][0], gdal.GA_ReadOnly)
    # lee la banda correspondiente al dataset
    im = dst.GetRasterBand(1)
    # todos los datos de geotransform de los la banda
    ulx, xres, xskew, uly, yskew, yres  = dst.GetGeoTransform()
    return({
           # todo lo geo transformacion
           'geotransform':dst.GetGeoTransform(),
           # todo los datos del hdf
           'dst_ori':dst,
           # nombre de la banda / banda
           'bnd_ori':im,
           # cordenada x upper left
           'ulx':ulx,
           # resolucion x
           'xres':xres,
           # coordenadas y upper left
           'uly':uly,
           # deformacion
           'yskew':yskew,
           # resolucion de y
           'yres':yres,
           #cantidad de x
           'xsize':dst.RasterXSize,
           # cantidad de y
           'ysize':dst.RasterYSize,
           # valor de transformacion de los datos
           'transform':im.GetScale(),
           # valor de los no data de la capa
           'nodata':im.GetNoDataValue(),
           # tipo de dato float int etc
           'tipo':im.GetUnitType(),
           })

# 2. imprimir el listado de hdf_ds
def mod_hdf_ds(x):
    """
    esta función toma un sólo archivo hdf, de tal forma que muestra
    una lista de los subdatasubsets presentes y sus respectivos nombres
    """
    im_dst = gdal.Open(x, gdal.GA_ReadOnly)
    aa = (im_dst.GetSubDatasets())
    for i in range(0, int(np.size(aa)/2)):
        print(', '.join((str(i), aa[i][-1])))


# 1. GEOTIF A ARRAY
def rst_2_arr(x):
    """
    rst_2_arr: como su nombre indica, transforma una lista de ubicaciones 
    de imágenes tipo raster, que leer y agrupa de manera ordenada, en 
    formato array. columna imagen, fila pixel
    """
    lista = []
    for i in tqdm(x):
        # lee todos los archivos / raster.
        im_dst = gdal.Open(i, gdal.GA_ReadOnly)
        bn_dst = im_dst.GetRasterBand(1)
        # data_type = gdal.GetDataTypeName(bnd_ds.DataType)
        bn_mat = bn_dst.ReadAsArray()
        # atriz a vector, usando orden 'C'
        im_vec = bn_mat.flatten('C')
        # array_ = bnd_ar.flatten('C').astype(np.float16)
        lista.append(im_vec)
        # arroja array como resultado, y se eliminan variables
        # temporales de memoria
    img_ts = np.stack(lista, axis=0)
    img_ts = np.transpose(img_ts)
    return(img_ts)


# 2. HDF A ARRAY
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


# 3. RELLENO CON SPLINE
def spline_ts(TimeSeries, NoDataVal=None):
    #t1 = time.time()
    """
    al usar directamente con archivos HDF, en LST el NoDataVal es 0.
    y debido a que el uso de la funcion apply_along_axis no permite
    saber el valor del dato, deberia agregar esa funcion dentro de este
    codigo
    """
    if NoDataVal is None:
        NoDataVal = -3000
    else:
        NoDataVal = NoDataVal
    # reemplaza el NoDataVal por NaN, me facilita la vida
    # TimeSeries[TimeSeries <= NoDataVal] = ['NaN']
    # si no existe no data, mantiene los datos
    if sum(np.equal(TimeSeries, NoDataVal)) == 0:
        ts_relleno = TimeSeries
    # chequea no data, si existe genera un spline y reemplaza no data
    elif sum(np.equal(TimeSeries, NoDataVal)) >= 1:
        # generar una serie de datos ordinales, para armar spline
        ordX = np.column_stack((np.arange(0,
                                          TimeSeries.size,
                                          dtype=TimeSeries.dtype),
                                TimeSeries))
        # se crea la funcion spline de los datos con información valida
        spl = InterpolatedUnivariateSpline(
                ordX[np.logical_not(np.equal(TimeSeries, NoDataVal))][:, 0],
                (ordX[np.logical_not(np.equal(TimeSeries, NoDataVal))][:, 1]))#/10000)#,ext=0)
        # genera datos interpolados por spline
        n2 = np.asarray((spl(range(TimeSeries.size))),dtype=TimeSeries.dtype)# * 1000
        # indices a reemplazar
        idx = np.argwhere(np.equal(TimeSeries, NoDataVal))
        # reemplaza solo aquellos valores no existentes en la serie original
        ordX[idx, 1] = n2[idx]
        # salida final de datos
        ts_relleno = ordX[:, 1]
    # si solo es "NoDataVal", reemplaza por una serie NaN
    elif sum(np.equal(TimeSeries, NoDataVal)) == np.size(TimeSeries):
        ts_relleno = np.full(np.size(TimeSeries), np.nan)
    #
    #t2 = time.time()
    #print(' '.join(('       ','tiempo:  ',time.strftime("%H:%M:%S", time.gmtime(t2-t1)))))
    #ts_relleno = signal.savgol_filter(ts_relleno, 11, 2)
    return (ts_relleno)



# # 4. RELLENO CON SPLINE
# def spline_ts(x, NonData=None):
#     def spl_axis(TimeSeries, NoDataVal=None):
#       # al usar directamente con archivos HDF, en LST el NoDataVal es 0.
#       # y debido a que el uso de la funcion apply_along_axis no permite
#       # saber el valor del dato, deberia agregar esa funcion dentro de este
#       # codigo
#       if NoDataVal is None:
#           NoDataVal = 0
#       else:
#           NoDataVal=NoDataVal
#       # reemplaza el NoDataVal por NaN, me facilita la vida
#       # TimeSeries[TimeSeries <= NoDataVal] = ['NaN']
#       # si no existe no data, mantiene los datos
#       if sum(np.equal(TimeSeries, NoDataVal)) == 0:
#           ts_relleno = TimeSeries
#       # chequea no data, si existe genera un spline y reemplaza no data
#       elif sum(np.equal(TimeSeries, NoDataVal)) >= 1:
#           # generar una serie de datos ordinales, para armar spline
#           ordX = np.column_stack((np.arange(0,
#                                             TimeSeries.size,
#                                             dtype=TimeSeries.dtype),
#                                   TimeSeries))
#           # se crea la funcion spline de los datos con información valida
#           spl = InterpolatedUnivariateSpline(
#                   ordX[np.logical_not(np.equal(TimeSeries, NoDataVal))][:, 0],
#                   (ordX[np.logical_not(np.equal(TimeSeries, NoDataVal))][:, 1])/10000,
#                   ext=0)
#           # genera datos interpolados por spline
#           n2 = np.asarray((spl(range(TimeSeries.size))) * 1000,
#                           dtype = TimeSeries.dtype)
#           # indices a reemplazar
#           idx = np.argwhere(np.equal(TimeSeries, NoDataVal))
#           # reemplaza solo aquellos valores no existentes en la serie original
#           ordX[idx, 1] = n2[idx]
#           # salida final de datos
#           ts_relleno = ordX[:, 1]
#       # si solo es "NoDataVal", reemplaza por una serie NaN
#       elif sum(np.equal(TimeSeries, NoDataVal)) == np.size(TimeSeries):
#           ts_relleno = np.full(np.size(TimeSeries), np.nan)
#       return (ts_relleno)
#       # ap
#       np.apply_along_axis




# 5. GEOTIF, escritura de imagenes geotif

def array2raster(newRasterfn, dataset, array, dtype):
    """
    save GTiff file from numpy.array
    input:
        newRasterfn: save file name
        dataset : original tif file
        array : numpy.array
        dtype: Byte or Float32.
    """
    cols = array.shape[1]
    rows = array.shape[0]
    originX, pixelWidth, b, originY, d, pixelHeight = dataset.GetGeoTransform()
    #
    driver = gdal.GetDriverByName('GTiff')
    #
    # set data type to save.
    GDT_dtype = gdal.GDT_Unknown
    if dtype == "Byte":
        GDT_dtype = gdal.GDT_Byte
    elif dtype == '16bit':
        GDT_dtype = gdal.GDT_Int16
    elif dtype == "Float32":
        GDT_dtype = gdal.GDT_Float32
    else:
        print("Not supported data type.")
    # set number of band.
    if array.ndim == 2:
        band_num = 1
    else:
        band_num = array.shape[2]
    #
    outRaster = driver.Create(newRasterfn, cols, rows, band_num, GDT_dtype)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    #
    # Loop over all bands.
    for b in range(band_num):
        outband = outRaster.GetRasterBand(b + 1)
        # Read in the band's data into the third dimension of our array
        if band_num == 1:
            outband.WriteArray(array)
        else:
            outband.WriteArray(array[:,:,b])
    #
    # setteing srs from input tif file.
    prj=dataset.GetProjection()
    outRasterSRS = osr.SpatialReference(wkt=prj)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()



# fuente: https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html?highlight=setgeotransform
# falta retocar, y ver si la salida tiene sentido.
# def arr_2_rst(newRasterfn, rasterOrigin, pixelWidth, pixelHeight, array):
#     """
#     tranformar array a geotiff, dato rellenado
#     """
#     cols = array.shape[1]
#     rows = array.shape[0]
#     originX = rasterOrigin[0]
#     originY = rasterOrigin[1]

#     driver = gdal.GetDriverByName('GTiff')
#     outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Float32) #,['COMPRESS=LZW'])
#     #outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte) #,['COMPRESS=LZW'])
#     outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
#     outband = outRaster.GetRasterBand(1)
#     outband.WriteArray(array)
#     outRasterSRS = osr.SpatialReference()
#     outRasterSRS.ImportFromEPSG(4326)
#     #outRaster.SetProjection(outRasterSRS.ExportToWkt())
#     outRasterSRS.SetProjection(('GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]'))
#     outband.FlushCache()

# # copia HDF to geotif
# def hdf_subdataset_extraction(hdf_file, dst_dir, subdataset, ds_array):
#     """unpack a single subdataset from a HDF5 container and write to GeoTiff"""
#     # open the dataset
#     hdf_ds = gdal.Open(hdf_file, gdal.GA_ReadOnly)
#     band_ds = gdal.Open(hdf_ds.GetSubDatasets()[subdataset][0], gdal.GA_ReadOnly)

#     # read into numpy array
#     band_array = band_ds.ReadAsArray().astype(np.int16)

#     # convert no_data values
#     band_array[band_array == -28672] = -32768

#     # build output path
#     band_path = os.path.join(dst_dir, os.path.basename(os.path.splitext(hdf_file)[0]) + "-sd" + str(subdataset+1) + ".tif")

#     # write raster
#     out_ds = gdal.GetDriverByName('GTiff').Create(band_path,
#                                                   band_ds.RasterXSize,
#                                                   band_ds.RasterYSize,
#                                                   1,  #Number of bands
#                                                   gdal.GDT_Int16,
#                                                   ['COMPRESS=LZW', 'TILED=YES'])
#     out_ds.SetGeoTransform(band_ds.GetGeoTransform())
#     out_ds.SetProjection(band_ds.GetProjection())
#     out_ds.GetRasterBand(1).WriteArray(band_array)
#     out_ds.GetRasterBand(1).SetNoDataValue(-32768)
#     out_ds = None  #close dataset to write to disc1


# 

# ## YVES
# function idr, series, threshold

#   serie = series
#   nc = 1000000.
#   while (nc ne 0) do begin
#     test = convol(serie,[1,0,1],/edge_wrap,/center,/normalize)
#     cloud = where((test-serie) gt threshold, nc)
#     if (nc ne 0) then serie[cloud] = test[cloud]
#   end
#   return, serie
 
# end






# sum(np.isnan(x1))
