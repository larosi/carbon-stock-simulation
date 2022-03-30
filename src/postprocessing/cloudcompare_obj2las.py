# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 17:41:08 2022

@author: Mico
"""

import os
import pathlib
from tqdm import tqdm
import json


def create_flag(output_folder, filename):
    flag_path = os.path.join(output_folder, filename + '.txt')
    if filename + '.txt' in os.listdir(output_folder):
        return True
    f = open(flag_path, 'w')
    f.close()
    return False


def read_json(json_path):
    f = open(json_path)
    data = json.load(f)
    f.close()
    return data


# TODO: use argparse for paths and mesh_density
THIS_PATH = str(pathlib.Path(__file__).parent.absolute())
THIS_PROJECT = str(pathlib.Path(THIS_PATH.split('src')[0]))
config = read_json(os.path.join(THIS_PROJECT, 'config.json'))
export_folder = os.path.join(THIS_PROJECT, config['export_dir'])
input_folder = os.path.join(export_folder, 'obj')
output_folder = os.path.join(export_folder, 'las')
os.makedirs(output_folder, exist_ok=True)

mesh_density = config['mesh_density']

input_filenames = []
for fn in os.listdir(input_folder):
    if'.obj' in fn:
        input_filenames.append(fn)

for input_filename in tqdm(input_filenames):
    input_path = os.path.join(input_folder, input_filename)

    base_filename = input_filename.replace('.obj', '')
    output_filename = base_filename + '.las'
    output_path = os.path.join(output_folder, output_filename)

    if create_flag(output_folder, base_filename):
        pass
    else:
        cmd_str = f'cloudcompare -SILENT -O "{input_path}" -AUTO_SAVE OFF -SAMPLE_MESH DENSITY {mesh_density} -C_EXPORT_FMT LAS -SAVE_CLOUDS FILE "{output_path}"'
        os.system('cmd /k "{}"'.format(cmd_str))
