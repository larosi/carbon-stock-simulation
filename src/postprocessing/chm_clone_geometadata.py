# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 14:09:34 2022

@author: Mico
"""

from skimage.transform import resize
from osgeo import gdal
import shutil
import os
import random
from tqdm import tqdm

def read_raster(raster_path):
    ds = gdal.Open(raster_path, 1)
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    return arr

def crop_fake_array(fake_arr, real_arr):
    [fake_h, fake_w] = fake_arr.shape
    [real_h, real_w] = real_arr.shape
    
    # crop
    mid_h, mid_w = int(fake_h/2), int(fake_w/2)
    half_h, half_w = real_h - mid_h, real_w-mid_w
    
    return fake_arr[mid_h-half_h:mid_h+half_h, mid_w-half_w:mid_w+half_w]  

def clone_geometadata(reference_raster_path, im_out_path, arr_out, no_data_value = -9999):
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
    outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
    outdata.SetProjection(ds.GetProjection())##sets same projection as input
    outdata.GetRasterBand(1).WriteArray(arr_out)
    outdata.GetRasterBand(1).SetNoDataValue(no_data_value)##if you want these values transparent
    outdata.FlushCache() ##saves to disk!!
    
    del ds
    del band
    del outdata
    
fake_folder = r'C:\Users\Mico\Desktop\gitlab\carbon-stock-simulation\data\export\chm' 
real_folder = r'C:\Users\Mico\Desktop\gitlab\carbon-stock\data\raw\laz\chm'
output_folder = r'C:\Users\Mico\Desktop\gitlab\carbon-stock-simulation\data\export\chm_fixed' 
filenames = []
for filename in os.listdir(fake_folder):
    if '.tif' in filename:
        filenames.append(filename)

for filename in tqdm(filenames):#= random.choice(filenames)
    fake_path = os.path.join(fake_folder, filename)
    real_path = os.path.join(real_folder, filename)
    out_path = os.path.join(output_folder, filename)
    
    arr_out = read_raster(fake_path)
    arr_out[arr_out<=0] = 0
    clone_geometadata(reference_raster_path=real_path,
                      im_out_path=out_path,
                      arr_out=arr_out,
                      no_data_value = 0)

        
    