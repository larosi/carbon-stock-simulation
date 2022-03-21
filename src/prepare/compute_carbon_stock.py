# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 18:04:29 2022

@author: Mico
"""

import pandas as pd
import os
import numpy as np


def compute_carbon_eacd(area, height, density=0.5):
    """ compute the estimated average carbon density """
    a = 3.8358
    b1 = 0.2807
    b2 = 0.9721
    b3 = 1.3763
    eacd = a*(height**b1) * (area**b2) * (density**b3)
    return eacd


def compute_carbon(area, height, density=0.5):
    """ compute the estimated average carbon density """
    eacd = area * height * density
    return eacd


seed_folder = os.path.join('..', '..', 'data', 'seeds')

filenames = os.listdir(seed_folder)

superficie_oncol = 2509.9
total_carbon = 0
for filename in filenames:
    df_path = os.path.join(seed_folder, filename)
    df = pd.read_csv(df_path)

    height = df['height'].values
    dap = df['dap'].values
    area = np.pi*(dap/200)**2

    carbon = compute_carbon(area, height, density=0.5)
    total_carbon = total_carbon + np.sum(carbon)

    df['carbon'] = pd.Series(carbon)
    df.to_csv(df_path, index=False)
carbon_density = total_carbon/superficie_oncol
print(carbon_density)
