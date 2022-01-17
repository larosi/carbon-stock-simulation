# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 11:07:06 2022

@author: Mico
"""

import pandas as pd
import os
from skimage import io

df_catalog = pd.read_csv(r'data/catalog.csv')

df_mid = df_catalog[df_catalog.type=='mid'].reset_index(drop=True)
df_low = df_catalog[df_catalog.type=='low'].reset_index(drop=True)
df_mid.to_json(r'data/json/catalog_mid.json')
df_low.to_json(r'data/json/catalog_low.json')

df = pd.read_csv(r'data/dataset_info.csv')
df.to_json(r'data/json/dataset_info.json')

choosen_tile = ['644_5598_1_norm_normalizado_CHM-20210121_S1_ENTREGA_04_LIDAR_CORREGIDO-03_CHM-02_PRODUCTOS_TILE-02_OPTECH-00_PRD-CHILE-2021-lidar-raw.csv']
seed_folder = r'data/seeds'
for csv_filename in os.listdir(seed_folder):
    csv_path = os.path.join(seed_folder, csv_filename) 
    json_path = os.path.join('data','json','seeds', csv_filename.replace('.csv','.json'))
    
    df = pd.read_csv(csv_path)
    if csv_filename in choosen_tile:
        dtm = io.imread(r'C:\Users\Mico\Desktop\gitlab\carbon-stock-simulation\data\export\dtm\dtm.tif')
        zs = []
        for index, row in df.iterrows():
            x, y = int(row['x']), int(row['y'])
            z = dtm[x,y]
            zs.append(z)
        df['z'] = pd.Series(zs)
    df.to_json(json_path)