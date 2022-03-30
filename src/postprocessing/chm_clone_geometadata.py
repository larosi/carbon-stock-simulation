# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 14:09:34 2022

@author: Mico
"""

from skimage.transform import resize
from osgeo import gdal
import shutil
import os
from tqdm import tqdm
import pathlib
from skimage import io
import numpy as np
import json


def read_json(json_path):
    f = open(json_path)
    data = json.load(f)
    f.close()
    return data


def read_raster(raster_path):
    ds = gdal.Open(raster_path, 1)
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    return arr


def crop_fake_array(fake_arr, real_arr):
    [fake_h, fake_w] = fake_arr.shape
    [real_h, real_w] = real_arr.shape

    center_h, center_w = int(real_h/2), int(real_w/2)
    mid_h, mid_w = int(fake_h/2), int(fake_w/2)

    delta_up = center_h
    delta_left = center_w
    delta_right = real_w - center_w
    delta_down = real_h - center_h

    return fake_arr[mid_h-delta_up:mid_h+delta_down,
                    mid_w-delta_left:mid_w+delta_right]


def clone_geometadata(reference_raster_path, im_out_path, arr_out, no_data_value=-9999):
    shutil.copy(reference_raster_path, im_out_path)
    outFileName = im_out_path

    # open original raster and get projection and geotransform
    ds = gdal.Open(reference_raster_path, 1)
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    [rows, cols] = arr.shape

    arr_out = crop_fake_array(fake_arr=arr_out, real_arr=arr)
    arr_out = resize(arr_out, (rows, cols))

    driver = gdal.GetDriverByName("GTiff")
    outdata = driver.Create(outFileName, cols, rows, 1, gdal.GDT_Float32)
    outdata.SetGeoTransform(ds.GetGeoTransform())
    outdata.SetProjection(ds.GetProjection())
    outdata.GetRasterBand(1).WriteArray(arr_out)
    outdata.GetRasterBand(1).SetNoDataValue(no_data_value)
    outdata.FlushCache()

    del ds
    del band
    del outdata


def find_first_zero(array, reverse=False):
    if reverse:
        array = array[::-1]
    zero_index = 0
    for index in range(0, len(array)):
        if array[index] != 0:
            zero_index = index
            break
    if reverse:
        zero_index = len(array) - zero_index
    return zero_index


THIS_PATH = str(pathlib.Path(__file__).parent.absolute())
THIS_PROJECT = str(pathlib.Path(THIS_PATH.split('src')[0]))
config = read_json(os.path.join(THIS_PROJECT, 'config.json'))
DATA_EXPORT_DIR = os.path.join(THIS_PROJECT, config['export_dir'])

bounds_folder = os.path.join(DATA_EXPORT_DIR, 'bounds')
fake_folder = os.path.join(DATA_EXPORT_DIR, 'chm')
real_folder = os.path.join(THIS_PROJECT, config['input_chm_dir'])

output_folder = os.path.join(DATA_EXPORT_DIR, 'chm_fixed')
os.makedirs(output_folder, exist_ok=True)
filenames = []
for filename in os.listdir(fake_folder):
    if '.tif' in filename:
        filenames.append(filename)

for filename in tqdm(filenames):
    bounds_path = os.path.join(bounds_folder, filename)
    fake_path = os.path.join(fake_folder, filename)
    real_path = os.path.join(real_folder, filename)
    out_path = os.path.join(output_folder, filename)

    bounds_img = io.imread(bounds_path, as_gray=True)

    sum_horizontal = np.sum(bounds_img, axis=1)
    sum_vertical = np.sum(bounds_img, axis=0)

    ymin = find_first_zero(sum_horizontal)
    ymax = find_first_zero(sum_horizontal, reverse=True)

    xmin = find_first_zero(sum_vertical)
    xmax = find_first_zero(sum_vertical, reverse=True)

    arr_out = read_raster(fake_path)
    arr_out = arr_out[ymin:ymax, xmin:xmax]
    arr_out[arr_out <= 0] = 0

    clone_geometadata(reference_raster_path=real_path,
                      im_out_path=out_path,
                      arr_out=arr_out,
                      no_data_value=0)
