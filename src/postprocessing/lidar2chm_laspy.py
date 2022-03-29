# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 15:20:19 2022

@author: Mico
"""

import laspy
from osgeo import gdal
import os
import numpy as np
from tqdm import tqdm
import pathlib
from skimage import io


""" https://gdal.org/tutorials/geotransforms_tut.html 
GT(0) x-coordinate of the upper-left corner of the upper-left pixel.
GT(1) w-e pixel resolution / pixel width.
GT(2) row rotation (typically zero).
GT(3) y-coordinate of the upper-left corner of the upper-left pixel.
GT(4) column rotation (typically zero).
GT(5) n-s pixel resolution / pixel height (negative value for a north-up image).
"""


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

    geotransform = (min_x, resolution, 0.0,  min_y, 0.0,  -resolution)
    n_rows = int((max_y - min_y)*factor)
    n_columns = int((max_x - min_x)*factor)
    yi = (factor*(max_y - y)).astype(np.int32)
    xi = (factor*(x - min_x)).astype(np.int32)

    """ create a list of lidar point indices of each raster pixel """
    n_points = len(y)
    pixel_indices = [[] for _ in range(0, n_rows*n_columns + 1)]

    for i in range(n_points):
        pixel_idx = (yi[i]-1)*n_columns + xi[i]
        pixel_indices[pixel_idx].append(i)
    raster_im = np.full((n_rows, n_columns), nodata, dtype=np.float32)
    raster_bounds = np.full((n_rows, n_columns), False, dtype=np.bool)
    pixel_indices = np.asarray(pixel_indices)
    for raster_i in range(0, n_rows-1):
        for raster_j in range(0, n_columns-1):
            pixel_idx = raster_i*n_columns + raster_j
            indices = pixel_indices[pixel_idx]
            pixel_points = z[indices]

            if len(pixel_points) > 0:
                pixel_max = np.max(pixel_points)
                pixel_min = np.min(pixel_points)
                raster_im[raster_i, raster_j] = pixel_max
                if pixel_min < 0:
                    raster_bounds[raster_i, raster_j] = True

    return raster_im, raster_bounds, geotransform

ref_raster = gdal.Open(r'C:\Users\Mico\Desktop\gitlab\carbon-stock\data\raw\laz\chm\640_5600_3_norm_normalizado_CHM-20210121_S1_ENTREGA_04_LIDAR_CORREGIDO-03_CHM-02_PRODUCTOS_TILE-02_OPTECH-00_PRD-CHILE-2021-lidar-raw.tif')
projection = ref_raster.GetProjection()
del ref_raster

THIS_PATH = str(pathlib.Path(__file__).parent.absolute())
THIS_PROJECT = str(pathlib.Path(THIS_PATH.split('src')[0]))
DATA_EXPORT_DIR = os.path.join(THIS_PROJECT, 'data', 'export')

INPUT = os.path.join(DATA_EXPORT_DIR, 'las')
OUTPUT = os.path.join(DATA_EXPORT_DIR, 'chm')
OUTPUT_BOUNDS = os.path.join(DATA_EXPORT_DIR, 'bounds')

os.makedirs(OUTPUT, exist_ok=True)
os.makedirs(OUTPUT_BOUNDS, exist_ok=True)

color_th = 0.25
resolution = 0.12
nodata = 0

laz_filenames = os.listdir(INPUT)

for laz_filename in laz_filenames:
    if laz_filename.split('.')[-1] in ['las', 'laz']:
        input_path = os.path.join(INPUT, laz_filename)
        output_filename = laz_filename.replace('.las', '.tif')
        output_path = os.path.join(OUTPUT, output_filename)
        infile = laspy.file.File(input_path, mode='r')

        """ guardar puntos lidar y su color """
        color = np.vstack((infile.red, infile.green, infile.blue)).transpose()
        color = np.mean(color, axis=1)
        color = color/color.max()
        color = color > color_th
        x, y, z = infile.x[color], infile.y[color], infile.z[color]
        infile.close()
        del color

        raster_im, raster_bounds, geotransform = compute_chm(x, y, z,
                                                             resolution)

        save_raster(raster_im, output_path, projection, geotransform)
        io.imsave(os.path.join(OUTPUT_BOUNDS, output_filename), raster_bounds)
