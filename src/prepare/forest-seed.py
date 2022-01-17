# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 17:34:38 2022

@author: Mico
"""

from skimage import io
import os
import numpy as np
from skimage.feature import peak_local_max
import matplotlib.pyplot as plt
from tqdm import tqdm
from skimage.transform import rescale
import plotly.express as px
import pandas as pd

#HT = 1/(0.0361354 + 0.723695/DAP)
"""https://www.conaf.cl/wp-content/files_mf/1381956486Informeroble.pdf"""
def dap_from_height(HT, hmax=45):
    HT =np.clip(HT*0.8, 0, hmax)
    #DAP = 0.723695/(1/HT - 0.0361354) #ligue
    DAP = 0.794063/(1/HT - 0.0217326) #roble
    #DAP = 0.270668/(1/HT - 0.016801) #Araucaria
    return DAP

def find_peaks(image, min_distance=14):
    #data_max = filters.maximum_filter(image, neighborhood_size, mode='constant')
    coordinates = peak_local_max(image, min_distance=min_distance)
    return coordinates

chm_folder = r'C:\Users\Mico\Desktop\gitlab\carbon-stock\data\raw\laz\chm'
chm_filenames = os.listdir(chm_folder)
#chm_filename = random.choice(chm_filenames)
for chm_filename in tqdm(chm_filenames):
    #chm_filename = '648_5602_4_norm_normalizado_CHM-20210121_S1_ENTREGA_04_LIDAR_CORREGIDO-03_CHM-02_PRODUCTOS_TILE-02_OPTECH-00_PRD-CHILE-2021-lidar-raw.tif'
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
                tree_height = window[coordinates[:,0], coordinates[:, 1]]
                global_coordinates = coordinates + [y, x]
                seed_coords.append(global_coordinates)
                seed_h.append(tree_height)
                pbar.update(1)
    
    seed_coords = np.concatenate(seed_coords)
    seed_h = np.concatenate(seed_h)
    seed_dap = dap_from_height(seed_h)
    
    
    
    df = pd.DataFrame()
    df['height'] = pd.Series(seed_h)
    df['area'] = pd.Series(seed_dap)
    df['x'] = pd.Series(seed_coords[:,1])
    df['y'] = pd.Series(seed_coords[:,0])
    
    output_path = os.path.join('data', 'seeds', chm_filename.replace('.tif', '.csv'))
    df.to_csv(output_path, index=False)
    """
    plt.scatter(seed_dap, seed_h)
    plt.xlabel('dap')
    plt.ylabel('altura')
    plt.show()
    
    plt.imshow(window)
    plt.plot(coordinates[:, 1], coordinates[:, 0], 'r.')
    plt.show()
    """
    output_html_path = os.path.join('data', 'plots', chm_filename.replace('.tif', '.html'))
    scale_factor = 8
    fig = px.imshow(rescale(image, 1/scale_factor))
    fig.add_scatter(x=seed_coords[:, 1]/scale_factor, y=seed_coords[:, 0]/scale_factor, mode='markers')
    fig.write_html(output_html_path)