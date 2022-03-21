# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 15:22:14 2022

@author: Mico
"""

import os
import pandas as pd
import rasterio
import numpy as np
from skimage.measure import block_reduce
from tqdm import tqdm

PROJECT_ROOT = os.path.join('..', '..')
DATA_PATH = os.path.join(PROJECT_ROOT, 'data')
DATASET_INFO_PATH = os.path.join(DATA_PATH, 'dataset_info.csv')
SEEDS_DIR = os.path.join(DATA_PATH, 'seeds')
OUTPUT_FOLDER = os.path.join(DATA_PATH, 'export', 'carbon')

CHM_DIR = r'..\..\..\carbon-stock\data\raw\laz\chm'  # FIXME
df_info = pd.read_csv(DATASET_INFO_PATH)

for index, row in tqdm(df_info.iterrows(), total=df_info.shape[0]):

    df_seed_filename = row['filename'] + '.csv'
    df_seed_path = os.path.join(SEEDS_DIR, df_seed_filename)
    df_seed = pd.read_csv(df_seed_path)

    chm_filename = row['filename'] + '.tif'
    chm_path = os.path.join(CHM_DIR, chm_filename)
    chm_raster = rasterio.open(chm_path)
    chm = chm_raster.read(1)
    chm_shape = chm.shape
    t = chm_raster.transform
    out_meta = chm_raster.meta
    chm_raster.close()

    output_raster = np.zeros(chm_shape)

    # drop outliers
    df_seed = df_seed[df_seed['carbon'] < 50*df_seed['carbon'].median()]

    # pixel_value = (df_seed['dap'].values/200)**2 * np.pi
    pixel_value = df_seed['carbon'].values

    xs, ys = df_seed['x'].values, df_seed['y'].values

    if len(xs) > 0:
        output_raster[ys, xs] = pixel_value

    out_image = block_reduce(output_raster, (83, 83), func=np.sum)

    new_scale_x = out_image.shape[0]/chm_shape[0]
    new_scale_y = out_image.shape[1]/chm_shape[1]

    # convert to 1/ha format from meters
    pixel_area = ((t.a / new_scale_y)*(t.e / new_scale_x))
    pixel_area = abs(pixel_area)/10000

    out_image = out_image*pixel_area

    out_transform = rasterio.Affine(t.a / new_scale_y,
                                    t.b, t.c, t.d,
                                    t.e / new_scale_x,
                                    t.f)
    out_image = np.expand_dims(out_image, axis=0)
    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})

    output_path = os.path.join(OUTPUT_FOLDER, chm_filename)
    with rasterio.open(output_path, "w", **out_meta) as dst:
        dst.write(out_image)
