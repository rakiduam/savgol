# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 18:14:39 2018
from: https://gis.stackexchange.com/questions/174017/extract-scientific-layers-from-modis-hdf-dataeset-using-python-gdal/174018
other: https://gis.stackexchange.com/questions/141776/read-hdf4-data-using-python
@author: Kersten
"""

#%reset -f

# Doc gdal
# https://gdal.org/python/

from osgeo import gdal
import numpy as np
import os, errno          # necesario para el directorio de salida
#import os
from glob import glob
import time
t0 = time.time()


# function
def hdf_subdataset_extraction(hdf_file, dst_dir, subdataset):
    """unpack a single subdataset from a HDF5 container and write to GeoTiff"""
    # open the dataset
    hdf_ds = gdal.Open(hdf_file, gdal.GA_ReadOnly)
    band_ds = gdal.Open(hdf_ds.GetSubDatasets()[subdataset][0], gdal.GA_ReadOnly)

    # read into numpy array
    band_array = band_ds.ReadAsArray().astype(np.int16)

    # convert no_data values
    band_array[band_array == -28672] = -32768

    # build output path
    band_path = os.path.join(dst_dir, os.path.basename(os.path.splitext(hdf_file)[0]) + "-sd" + str(subdataset+1) + ".tif")

    # write raster
    out_ds = gdal.GetDriverByName('GTiff').Create(band_path,
                                                  band_ds.RasterXSize,
                                                  band_ds.RasterYSize,
                                                  1,  #Number of bands
                                                  gdal.GDT_Int16,
                                                  ['COMPRESS=LZW', 'TILED=YES'])
    out_ds.SetGeoTransform(band_ds.GetGeoTransform())
    out_ds.SetProjection(band_ds.GetProjection())
    out_ds.GetRasterBand(1).WriteArray(band_array)
    out_ds.GetRasterBand(1).SetNoDataValue(-32768)

    out_ds = None  #close dataset to write to disc

################################################################################

# image directory
entDIR = 'E:\\MOD13Q1\\'
imgMOD = 'MOD13Q1'
sub = 2
salDIR = ('E:\\version00\\' + imgMOD + '\\subset_'+str(sub).zfill(2)+'\\')

try:
    os.makedirs(salDIR)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

#try:
#    os.makedirs(tmpDIR)
#except OSError as e:
#    if e.errno != errno.EEXIST:
#        raise

for y in range(1999,2019):
    print(y)
    for d in range(1,367):
        #print(d)
        HDF =  (glob(entDIR + '\\' + imgMOD +'.A' + str(y) + str(d).zfill(3) + '.??????.' + '006.' + '*.hdf'))
        if HDF != []:
            print('....    ' + str(d).zfill(3))
            for hdf in HDF:
                hdf_subdataset_extraction(hdf, salDIR, sub)
        else:
            print('.')

        

t1 = time.time()
total_n = t1-t0
print('tiempo total de ejecucion:' + str(total_n))
