# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 11:34:50 2022

@author: Mico
"""

import os
import pathlib
import pandas as pd
import laspy
import numpy as np
from skimage import io
from skimage import morphology as morph
from skimage.util import img_as_ubyte
from scipy.ndimage import binary_fill_holes
import json


def read_json(json_path):
    f = open(json_path)
    data = json.load(f)
    f.close()
    return data


THIS_PATH = str(pathlib.Path(__file__).parent.absolute())
THIS_PROJECT = str(pathlib.Path(THIS_PATH.split('src')[0]))
config = read_json(os.path.join(THIS_PROJECT, 'config.json'))
DATA_DIR = os.path.join(THIS_PROJECT, config['data_dir'])
EXPORT_DIR = os.path.join(THIS_PROJECT, config['export_dir'])

# input folders
LAS_DIR = os.path.join(EXPORT_DIR, 'trees_las')
CATALOG_PATH = os.path.join(THIS_PROJECT, config['catalog'])

# output folders
OUTPUT_DIR = os.path.join(EXPORT_DIR, 'trees_mask')
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(CATALOG_PATH)

tree_names = df['name'].values
resolution = config['tree_mask_resolution']  # pixel in meters
color_th = config['color_th']
for index, row in df.iterrows():
    tree_name = row['name']
    tree_h = row['height']

    las_file_path = os.path.join(LAS_DIR, tree_name + '.las')
    infile = laspy.file.File(las_file_path, mode='r')
    """ guardar puntos lidar y su color """
    x, y, z = infile.x, infile.y, infile.z
    rgb = np.vstack((infile.red, infile.green, infile.blue)).transpose()

    """ pasar de color escala de grises """
    gray = np.mean(rgb, axis=1)
    gray = gray/gray.max()

    infile.close()

    min_z, min_y, min_x = np.min(z), np.min(y), np.min(x)
    max_z, max_y, max_x = np.max(z), np.max(y), np.max(x)

    # move points to origin (0, 0, 0)
    x = x-min_x
    y = y-min_y
    z = z-min_z

    delta_x = max_x - min_x
    delta_y = max_y - min_y
    delta_z = max_z - min_z

    scale_factor = tree_h/delta_z
    n_rows = int(delta_x * scale_factor * (1/resolution))
    n_columns = int(delta_y * scale_factor * (1/resolution))

    xi = (x * scale_factor * (1/resolution)+1).astype(np.int32)
    yi = (y * scale_factor * (1/resolution)+1).astype(np.int32)

    """ almacenar puntos claros (gray>0.25) en una imagen"""
    n_points = len(y)
    im = np.zeros((n_rows, n_columns))
    for i in range(n_points):
        if gray[i] > color_th:
            im[xi[i], yi[i]] = gray[i]

    """ obtener mascara binaria de la imagen """
    io.imshow(im)
    io.show()

    im = im > 0
    im = morph.binary_closing(im, morph.disk(radius=5))
    im = morph.binary_opening(im, morph.disk(radius=3))
    im = binary_fill_holes(im)

    io.imshow(im)
    io.show()

    im = img_as_ubyte(im)
    output_filename = tree_name + '.png'
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    io.imsave(output_path, im)
