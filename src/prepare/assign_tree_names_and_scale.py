# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 13:16:36 2022

@author: Mico
"""
import os
import pathlib
import pandas as pd


def dap_from_height(HT, hmax=45):
    """ compute dap using inverse alometrics functions """
    HT = np.clip(HT*0.8, 0, hmax)  # limit to avoid too big diameters
    DAP = 0.794063/(1/HT - 0.0217326)  # roble

    return DAP


# directories relatives to project root path
THIS_PATH = str(pathlib.Path(__file__).parent.absolute())
PROJECT_ROOT = str(pathlib.Path(THIS_PATH.split('src')[0]))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

# inputs
DATASET_INFO_PATH = os.path.join(DATA_DIR, 'dataset_info.csv')
CATALOG_PATH = os.path.join(DATA_DIR, 'catalog.csv')

# output
SEEDS_DIR = os.path.join(DATA_DIR, 'seeds')

# params
hmax = 45  # tree max h in meters
sotobosque_th = 2.5  # below this th in meters are small trees

df_info = pd.read_csv(DATASET_INFO_PATH)
df_catalog = pd.read_csv(CATALOG_PATH)
df_low = df_catalog[df_catalog['type'] == 'low']
df_mid = df_catalog[df_catalog['type'] == 'mid']

for _, row_info in df_info.iterrows():
    base_filename = row_info['filename']

    df_filename = base_filename + '.csv'
    df_path = os.path.join(SEEDS_DIR, df_filename)
    df = pd.read_csv(df_path)

    df['dap'] = dap_from_height(HT=df['height'].values, hmax=hmax)

    tree_names = []
    asset_h = []
    for index, row in df.iterrows():
        if row['height'] < sotobosque_th:
            sample = df_low.sample(n=1)
        else:
            sample = df_mid.sample(n=1)
        sample = sample.iloc[0]
        tree_names.append(sample['name'])
        asset_h.append(sample['height'])

    df['tree_name'] = pd.Series(tree_names)
    df['height_asset'] = pd.Series(asset_h)

    df['scale_z'] = df['height'] / df['height_asset']
    df['scale_x'] = df['scale_z']
    df['scale_y'] = df['scale_z']

    df.to_csv(df_path, index=False)
