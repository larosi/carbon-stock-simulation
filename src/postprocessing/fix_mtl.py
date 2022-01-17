# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 18:01:09 2022

@author: Mico
"""

import os

input_folder = r'C:\Users\Mico\Desktop\gitlab\carbon-stock-simulation\data\export\obj'
str_to_remove = 'C:\\\\Users\\\\Mico\\\\Desktop\\\\gitlab\\\\carbon-stock-simulation\\\\data\\\\textures\\\\'
input_filenames = []
for fn in os.listdir(input_folder):
    if'.mtl' in fn:
        input_filenames.append(fn)

for input_filename in input_filenames:
    file_path = os.path.join(input_folder, input_filename)
    f = open(file_path, 'r')
    new_lines = []
    for line in f.readlines():
        if 'map_Kd' in line or 'map_d' in line:
            line = line.replace(str_to_remove, '')
        new_lines.append(line)
    f.close()
    new_data = ''.join(new_lines)
    f = open(file_path, 'w')
    f.write(new_data)
    f.close()
    
