# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 19:40:45 2022

@author: Mico
"""

import pandas as pd
import os
from skimage import io
import json


def read_json(json_path):
    f = open(json_path)
    data = json.load(f)
    f.close()
    return data


THIS_PATH = str(pathlib.Path(__file__).parent.absolute())
THIS_PROJECT = str(pathlib.Path(THIS_PATH.split('src')[0]))
config = read_json(os.path.join(THIS_PROJECT, 'config.json'))
chm_folder = os.path.join(THIS_PROJECT, config['input_chm_dir'])
dataset_info_path = os.path.join(THIS_PROJECT, ['dataset_info'])
chm_filenames = os.listdir(chm_folder)

xtotal = []
ytotal = []
csv_filenames = []
for chm_filename in chm_filenames:
    chm_path = os.path.join(chm_folder, chm_filename)
    chm = io.imread(chm_path, as_gray=True)
    csv_filename = chm_filename.replace('.tif', '')
    csv_filenames.append(csv_filename)
    
    h,w = chm.shape
    
    xtotal.append(w)
    ytotal.append(h)

df = pd.DataFrame()

df['filename'] = pd.Series(csv_filenames)
df['xtotal'] = pd.Series(xtotal)
df['ytotal'] = pd.Series(ytotal)

df.to_csv(dataset_info_path, index = False)