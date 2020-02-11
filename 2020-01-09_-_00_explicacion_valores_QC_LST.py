# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 10:37:44 2020

@author: fanr

para la estimacion de valores de calidad ex ante, de los productos
modis, esto se repite en varios productos, la estructura, los valores
binarios varian segun el producto.

=======================================================================================
=======================================================================================

En MOD13xx NDVI e EVI poseen una banda de calidad previamente procesada,
que entrega una escala de 0 a 3, revisar user's guide.

Para MOD11 u otros deben analizar la banda de calidad de estimacion.
Este metodo tambien se encuentra en otros productos satelitales.
Revisar:

- https://lpdaac.usgs.gov/documents/118/MOD11_User_Guide_V6.pdf

- https://stevemosher.wordpress.com/2012/12/05/modis-qc-bits/

- https://github.com/haoliangyu/pymasker

- Getting Started with MODIS Land Surface Temperature Data (Part 3)
  https://www.youtube.com/watch?v=JPjkjjhj5rk

- https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MOD11A1

=======================================================================================
A partir de User's Guide se puede obtener esta tabla.

****************************************************
***** TABLA CALIDAD PARA DATOS DE LST, MOD11A1 *****
****************************************************
bit         Long Name                   Key
=======================================================================================
1 & 00      Mandatory QA flags          00 = LST produced, good quality, not
                                           necessary to examine more detailed QA
                                        01 = LST produced, other quality,
                                           recommend examination of more
                                           detailed QA
                                        10 = LST not produced due to cloud
                                           effects
                                        11 = LST not produced primarily due to
                                           reasons other than cloud

3 & 2      Data quality flag            00 = good data quality
                                        01 = LST affected by thin cirrus and/or sub-pixel clouds
                                        10 = not processed due to missing pixels
                                        11 = not processed due to poor quality

5 & 4       Emis Error flag             00 = average emissivity error <= 0.01
                                        01 = average emissivity error <= 0.02
                                        10 = average emissivity error <= 0.04
                                        11 = average emissivity error >  0.04

7 & 6       LST Error flag              00 = average LST error <= 1K
                                        01 = average LST error <= 2K
                                        10 = average LST error <= 3K
                                        11 = average LST error >  3K

"""

# %% LIBRERIAS
import numpy as np
import pandas as pd

# variables a usar, generacion series.
# en este caso procese todos  los valores posibles.
# de ahi es cosa de usar "if x in rango_valores_x_posibles"
serie_test = np.arange(0, 256)

qc0, qc1, qc2, qc3, qc4, qc5, qc6, qc7 = None, None, None, None, None, None, None, None
qc0, qc1, qc2, qc3, qc4, qc5, qc6, qc7 = list(), list(), list(), list(), list(), list(), list(), list()
serie_binario = list()
    #serie_binario = np.binary_repr(fila)
    #print(np.binary_repr(fila, 8))
    #print(str((' ').join([str(np.binary_repr(fila, 8))])))
    #print((' ').join([qc0, qc2, qc4, qc6]))

for count, fila in enumerate(serie_test[:]):
    # posicion relativa considerando que python parte desde 0
    qc0.append(np.binary_repr(fila, 8)[-1])
    qc1.append(np.binary_repr(fila, 8)[-2])
    qc2.append(np.binary_repr(fila, 8)[-3])
    qc3.append(np.binary_repr(fila, 8)[-4])
    qc4.append(np.binary_repr(fila, 8)[-5])
    qc5.append(np.binary_repr(fila, 8)[-6])
    qc6.append(np.binary_repr(fila, 8)[-7])
    qc7.append(np.binary_repr(fila, 8)[-8])
    #
    serie_binario.append(('').join([' ', (np.binary_repr(num=fila, width=8)), ' ']))
    # print(serie_binario[count])


eval_df = pd.DataFrame({'n_serie': serie_test,'n_binario':serie_binario,
                  'bit7':qc7, 'bit6':qc6, 'bit5':qc5, 'bit4':qc4,
                  'bit3':qc3, 'bit2':qc2, 'bit1':qc1, 'bit0':qc0,} )
print(eval_df)


# %% analisis valor y tipo de error

# creacion de columnas donde estaran la clasificacion de calidad acorde al bit
eval_df['estado0'], eval_df['estado1'], eval_df['estado2'], eval_df['estado3'] = None, None, None, None

eval_df.shape


for count, binario in enumerate(eval_df.iloc[:,0]):
    # par 01
    if eval_df.bit1[count] == '0' and eval_df.bit0[count] == '0': eval_df.estado0[count] = 'LST GOOD'
    if eval_df.bit1[count] == '0' and eval_df.bit0[count] == '1': eval_df.estado0[count] = 'LST Produced,Other Quality'
    if eval_df.bit1[count] == '1' and eval_df.bit0[count] == '0': eval_df.estado0[count] = 'No Pixel,clouds'
    if eval_df.bit1[count] == '1' and eval_df.bit0[count] == '1': eval_df.estado0[count] = 'No Pixel, Other QA'
    # par 23
    if eval_df.bit3[count] == '0' and eval_df.bit2[count] == '0': eval_df.estado1[count] = 'Good Data'
    if eval_df.bit3[count] == '0' and eval_df.bit2[count] == '1': eval_df.estado1[count] = 'LST affected by thin cirrus and/or sub-pixel clouds'
    if eval_df.bit3[count] == '1' and eval_df.bit2[count] == '0': eval_df.estado1[count] = 'not processed due to missing pixels'
    if eval_df.bit3[count] == '1' and eval_df.bit2[count] == '1': eval_df.estado1[count] = 'not processed due to poor quality'
    # par 45
    if eval_df.bit5[count] == '0' and eval_df.bit4[count] == '0': eval_df.estado2[count] = 'average emissivity error <= 0.01'
    if eval_df.bit5[count] == '0' and eval_df.bit4[count] == '1': eval_df.estado2[count] = 'average emissivity error <= 0.02'
    if eval_df.bit5[count] == '1' and eval_df.bit4[count] == '0': eval_df.estado2[count] = 'average emissivity error <= 0.04'
    if eval_df.bit5[count] == '1' and eval_df.bit4[count] == '1': eval_df.estado2[count] = 'average emissivity error >  0.04'
    # par 67
    if eval_df.bit7[count] == '0' and eval_df.bit6[count] == '0': eval_df.estado3[count] = 'average LST error <= 1K'
    if eval_df.bit7[count] == '0' and eval_df.bit6[count] == '1': eval_df.estado3[count] = 'average LST error <= 2K'
    if eval_df.bit7[count] == '1' and eval_df.bit6[count] == '0': eval_df.estado3[count] = 'average LST error <= 3K'
    if eval_df.bit7[count] == '1' and eval_df.bit6[count] == '1': eval_df.estado3[count] = 'average LST error >  3K'


# %% selección de valores "razonables" para ser usados.
eval_df.to_csv("D:/scripts_01_08_2020/2020-01-09_-_explicacion_valores_QC.csv", index_label='n_serie', index=False)

# creo columna para evaluar
eval_df.usar = None

## finalmente hice la seleccion en un archivo excel. en LST
## segui el criterio, de LST GOOD, Good Data y LST Err >= 1K

# for count, binario in enumerate(eval_df.iloc[:,0]):
#     if eval_df.estado0[count] == 'LST GOOD': eval_df.usar[count] = 'SI'

#     if eval_df.bit1[count] == '0' and eval_df.bit0[count] == '1': eval_df.estado0[count] = 'LST Produced,Other Quality'
#     if eval_df.bit1[count] == '1' and eval_df.bit0[count] == '0': eval_df.estado0[count] = 'No Pixel,clouds'
#     if eval_df.bit1[count] == '1' and eval_df.bit0[count] == '1': eval_df.estado0[count] = 'No Pixel, Other QA'
