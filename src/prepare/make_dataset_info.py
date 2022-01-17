# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 19:40:45 2022

@author: Mico
"""

import pandas as pd
import os
from skimage import io

chm_folder = r'C:\Users\Mico\Desktop\gitlab\carbon-stock\data\raw\laz\chm'

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

df.to_csv(r'data/dataset_info.csv', index = False)