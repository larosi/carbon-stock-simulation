# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 15:20:19 2022

@author: Mico
"""

import laspy
from osgeo import gdal #,osr
import os
import numpy as np
from tqdm import tqdm


""" https://gdal.org/tutorials/geotransforms_tut.html 
GT(0) x-coordinate of the upper-left corner of the upper-left pixel.
GT(1) w-e pixel resolution / pixel width.
GT(2) row rotation (typically zero).
GT(3) y-coordinate of the upper-left corner of the upper-left pixel.
GT(4) column rotation (typically zero).
GT(5) n-s pixel resolution / pixel height (negative value for a north-up image).
"""
def get_geotransform_from_lidar(min_x, min_y, resolution):
    geotransform = (min_x, resolution, 0.0,  min_y, 0.0,  -resolution)
    return geotransform

def save_raster(npArray, dstFilePath, projection, geotransform):
    dshape = npArray.shape
    bandnum = 1
    format = "ENVI"
    driver = gdal.GetDriverByName(format)
    dst_ds = driver.Create(dstFilePath, dshape[1], dshape[0], bandnum, gdal.GDT_Float32)

    dst_ds.SetGeoTransform(geotransform)
    #srs = osr.SpatialReference()
    #srs.ImportFromEPSG(32619)
    #dst_ds.SetProjection(srs.ExportToWkt())
    dst_ds.SetProjection(projection)
    dst_ds.GetRasterBand(1).WriteArray(npArray)
    dst_ds = None

def compute_chm(x, y, z, resolution):
    factor = 1/resolution

    min_y, min_x = np.min(y), np.min(x)
    max_y, max_x = np.max(y), np.max(x)
    
    #geotransform = get_geotransform_from_lidar(min_x, min_y, resolution)
    geotransform = (min_x, resolution, 0.0,  min_y, 0.0,  -resolution)
    n_rows, n_columns = int((max_y - min_y)*factor), int((max_x - min_x)*factor)
    yi, xi = (factor*(max_y -y)).astype(np.int32), (factor*(x - min_x)).astype(np.int32)

    """ create a list of lidar point indices of each raster pixel """
    n_points = len(y)
    pixel_indices = [[] for _ in range(0, n_rows*n_columns + 1)]
    
    for i in range(n_points):
        pixel_idx = (yi[i]-1)*n_columns + xi[i]
        pixel_indices[pixel_idx].append(i)
    raster_im = np.full((n_rows, n_columns), nodata, dtype=np.float32)
    pixel_indices = np.asarray(pixel_indices)    
    for raster_i in range(0, n_rows-1):
        for raster_j in range(0, n_columns-1):
            pixel_idx = raster_i*n_columns + raster_j
            indices = pixel_indices[pixel_idx]
            pixel_points = z[indices]

            if len(pixel_points)>0:
                raster_im[raster_i, raster_j] = np.max(pixel_points)

    return raster_im, geotransform

ref_raster = gdal.Open(r'C:\Users\Mico\Desktop\gitlab\carbon-stock\data\raw\laz\chm\640_5600_3_norm_normalizado_CHM-20210121_S1_ENTREGA_04_LIDAR_CORREGIDO-03_CHM-02_PRODUCTOS_TILE-02_OPTECH-00_PRD-CHILE-2021-lidar-raw.tif')
projection = ref_raster.GetProjection()

INPUT = r'C:\Users\Mico\Desktop\gitlab\carbon-stock\data\raw\laz\raw'
OUTPUT = r'C:\Users\Mico\Desktop\gitlab\carbon-stock-simulation\data\export\dsm'
resolution = 0.12
nodata = 0#-9999

#laz_filenames = os.listdir(INPUT)
laz_filenames = ['644_5598_1-20210121_S1_ENTREGA_04_LIDAR_CORREGIDO-01_LAZ-00_INPUT-02_OPTECH-00_PRD-CHILE-2021-lidar-raw.laz']

for laz_filename in laz_filenames:
    input_path = os.path.join(INPUT, laz_filename)  
    output_path = os.path.join(OUTPUT, laz_filename.replace('.laz', '.tif'))
    infile = laspy.file.File(input_path, mode='r')
    x,y,z = infile.x, infile.y, infile.z
    raster_im, geotransform = compute_chm(x, y, z, resolution)
    infile.close()
    save_raster(raster_im, output_path, projection, geotransform)
    
