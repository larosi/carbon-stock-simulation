# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 17:41:08 2022

@author: Mico
"""

import os
from tqdm import tqdm

def create_flag(output_folder, filename):
    flag_path = os.path.join(output_folder, filename + '.txt')
    if filename + '.txt' in os.listdir(output_folder):
        return True
    f = open(flag_path, 'w')
    f.close()
    return False

input_folder = r'C:\Users\Mico\Desktop\gitlab\carbon-stock-simulation\data\export\obj'

input_filenames = []
for fn in os.listdir(input_folder):
    if'.obj' in fn:
        input_filenames.append(fn)

for input_filename in tqdm(input_filenames):
    input_path = os.path.join(input_folder, input_filename)
    
    output_folder = r'C:\Users\Mico\Desktop\gitlab\carbon-stock-simulation\data\export\las'
    base_filename = input_filename.replace('.obj', '')
    output_filename = base_filename + '.las'
    output_path = os.path.join(output_folder, output_filename)
    
    if create_flag(output_folder, base_filename):
        pass
    else:
        cmd_str = f'cloudcompare -SILENT -O "{input_path}" -AUTO_SAVE OFF -SAMPLE_MESH DENSITY 10 -C_EXPORT_FMT LAS -SAVE_CLOUDS FILE "{output_path}"'
        #print(cmd_str)
        os.system('cmd /k "{}"'.format(cmd_str))