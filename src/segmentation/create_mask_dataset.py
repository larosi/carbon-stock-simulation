# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 15:28:32 2022

@author: Mico
"""


from skimage import io
import os
import pathlib
import pandas as pd
import numpy as np
from skimage.transform import resize
from tqdm import tqdm
import rasterio
import json


def read_json(json_path):
    f = open(json_path)
    data = json.load(f)
    f.close()
    return data


def save_raster(output_path, out_image, reference_path):
    """ create a raster using a referece one """
    ref_raster = rasterio.open(reference_path)
    out_meta = ref_raster.meta
    t = ref_raster.transform
    ref_raster.close()

    out_transform = rasterio.Affine(t.a, t.b, t.c, t.d, t.e, t.f)

    out_image = np.expand_dims(out_image, axis=0)
    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})

    with rasterio.open(output_path, "w", **out_meta) as dst:
        dst.write(out_image)


THIS_PATH = str(pathlib.Path(__file__).parent.absolute())
THIS_PROJECT  = str(pathlib.Path(THIS_PATH.split('src')[0]))
config = read_json(os.path.join(THIS_PROJECT, 'config.json'))

DATA_DIR = os.path.join(PROJECT_ROOT, config['data_dir'])
EXPORT_DIR = os.path.join(PROJECT_ROOT, config['export_dir'])

# input folders
CHM_DIR = os.path.join(THIS_PROJECT, config['input_chm_dir'])

MASK_DIR = os.path.join(EXPORT_DIR, 'trees_mask')
SEEDS_DIR = os.path.join(THIS_PROJECT, 'seeds')

# output_folder
CHM_MASK_DIR = os.path.join(EXPORT_DIR, 'chm_mask')
os.makedirs(CHM_MASK_DIR, exist_ok=True)

CATALOG_PATH = os.path.join(THIS_PROJECT, config['catalog'])
DATASET_INFO_PATH = os.path.join(THIS_PROJECT, config['dataset_info'])
df_catalog = pd.read_csv(CATALOG_PATH)
df_info = pd.read_csv(DATASET_INFO_PATH)

chm_resolution = config['resolution']
mask_resolution = config['tree_mask_resolution']

""" load tree masks """
tree_masks = {}
for tree_name in df_catalog['name'].values:
    tree_mask_path = os.path.join(MASK_DIR, tree_name + '.png')
    tree_mask = io.imread(tree_mask_path, as_gray=True) > 0.5
    # FIXME: trees in blender are rotated 90°
    tree_mask = np.rot90(tree_mask)
    tree_masks[tree_name] = tree_mask

""" create a mask dataset for each CHM tile """

for _, info_row in tqdm(df_info.iterrows(), total=df_info.shape[0]):
    chm_filename = info_row['filename']
    xtotal, ytotal = info_row['xtotal'], info_row['ytotal']
    mask_accumulator = np.zeros((ytotal, xtotal), dtype=np.uint16)

    chm_path = os.path.join(CHM_DIR, chm_filename + '.tif')
    chm = io.imread(chm_path, as_gray=True)

    df_seed_path = os.path.join(SEEDS_DIR, chm_filename + '.csv')
    df = pd.read_csv(df_seed_path)
    # draw mask from bottom to top height (Painter's algorithm)
    df.sort_values(by='height', ascending=True, inplace=True)
    for index, row in tqdm(df.iterrows(), total=df.shape[0], leave=False):
        x, y = int(row['x']), int(row['y'])
        h = row['height']
        seed_h = row['height_asset']
        tree_mask = tree_masks[row['tree_name']]

        mask_shape_meters = np.array(tree_mask.shape) * mask_resolution
        mask_shape_meters = mask_shape_meters * h/seed_h

        mask_shape_pix = (mask_shape_meters / chm_resolution).astype(np.int32)
        mask_h, mask_w = mask_shape_pix
        if mask_h > 0 and mask_w > 0:
            mask = resize(tree_mask, (mask_h, mask_w)) > 0

            xmin = int(x - mask_w/2)
            ymin = int(y - mask_h/2)

            """ check edge cases and fix it"""
            if xmin < 0:
                mask = mask[:, abs(xmin):]
                xmin = 0
            if ymin < 0:
                mask = mask[abs(ymin):, :]
                ymin = 0
            delta_y = ytotal - (ymin + mask.shape[0])
            if delta_y < 0:
                mask = mask[0:mask.shape[0]+delta_y, :]
            delta_x = xtotal - (xmin + mask.shape[1])
            if delta_x < 0:
                mask = mask[:, 0:mask.shape[1]+delta_x]

            """ create a raster size boolean mask and update accumulator"""
            big_mask = np.zeros((ytotal, xtotal), dtype=bool)
            big_mask[ymin:ymin+mask.shape[0], xmin:xmin+mask.shape[1]] = mask

            mask_id = index+1
            mask_accumulator[big_mask] = mask_id

    output_path = os.path.join(CHM_MASK_DIR, chm_filename + '.tif')
    save_raster(output_path=output_path,
                out_image=mask_accumulator,
                reference_path=chm_path)
