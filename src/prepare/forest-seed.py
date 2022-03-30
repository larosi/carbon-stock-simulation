# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 17:34:38 2022

@author: Mico
"""

from skimage import io
import os
import numpy as np
from skimage.feature import peak_local_max
from tqdm import tqdm
from skimage.transform import rescale
import plotly.express as px
import pandas as pd
import pathlib
import json


def read_json(json_path):
    f = open(json_path)
    data = json.load(f)
    f.close()
    return data


def find_peaks(image, min_distance=14):
    coordinates = peak_local_max(image, min_distance=min_distance)
    return coordinates


# directories relatives to project root path
THIS_PATH = str(pathlib.Path(__file__).parent.absolute())
THIS_PROJECT = str(pathlib.Path(THIS_PATH.split('src')[0]))
config = read_json(os.path.join(THIS_PROJECT, 'config.json'))

DATA_DIR = os.path.join(THIS_PROJECT, config['data_dir'])

# inputs
chm_folder = os.path.join(THIS_PROJECT, config['input_chm_dir'])
dataset_info_path = os.path.join(THIS_PROJECT, config['dataset_info'])

# outputs
SEEDS_DIR = os.path.join(THIS_PROJECT, config['seeds_dir'])
PLOTS_DIR = os.path.join(DATA_DIR, 'plots')

os.makedirs(SEEDS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

# get raster filenames
df_info = pd.read_csv(dataset_info_path)
chm_filenames = df_info['filename'].values

for chm_base_filename in tqdm(chm_filenames):
    chm_filename = chm_base_filename + '.tif'
    chm_path = os.path.join(chm_folder, chm_filename)

    chm = io.imread(chm_path, as_gray=True)
    image = np.clip(chm, 0, chm.max())

    image_height, image_width = image.shape
    window_step = 500
    window_size = 500
    y_range = range(0, image_height, window_step)
    x_range = range(0, image_width, window_step)

    seed_coords = []
    seed_h = []
    with tqdm(total=len(x_range)*len(y_range)) as pbar:
        for y in y_range:
            for x in x_range:
                window = image[y:y+window_size, x:x+window_size]
                coordinates = peak_local_max(window, min_distance=16)

                tree_height = window[coordinates[:, 0],
                                     coordinates[:, 1]]

                global_coordinates = coordinates + [y, x]
                seed_coords.append(global_coordinates)
                seed_h.append(tree_height)
                pbar.update(1)

    seed_coords = np.concatenate(seed_coords)
    seed_h = np.concatenate(seed_h)

    df = pd.DataFrame()
    df['height'] = pd.Series(seed_h)
    df['x'] = pd.Series(seed_coords[:, 1])
    df['y'] = pd.Series(seed_coords[:, 0])

    output_path = os.path.join(SEEDS_DIR, chm_base_filename + '.csv')
    df.to_csv(output_path, index=False)

    output_html_path = os.path.join(PLOTS_DIR, chm_base_filename + '.html')
    scale_factor = 8
    fig = px.imshow(rescale(image, 1/scale_factor))
    fig.add_scatter(x=seed_coords[:, 1]/scale_factor,
                    y=seed_coords[:, 0]/scale_factor,
                    mode='markers')
    fig.write_html(output_html_path)
