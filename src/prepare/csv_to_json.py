# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 11:07:06 2022

@author: Mico
"""

import pandas as pd
import os
import pathlib
import json


def read_json(json_path):
    f = open(json_path)
    data = json.load(f)
    f.close()
    return data


def csvs_to_json(filenames, input_dir, output_dir):
    for filename in filenames:
        json_filename = filename.replace('.csv', '.json')
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, json_filename)
        df = pd.read_csv(input_path)
        df.to_json(output_path)


# directories relatives to project root path
THIS_PATH = str(pathlib.Path(__file__).parent.absolute())
THIS_PROJECT = str(pathlib.Path(THIS_PATH.split('src')[0]))
config = read_json(os.path.join(THIS_PROJECT, 'config.json'))
DATA_DIR = os.path.join(THIS_PROJECT, config['data_dir'])

# inputs
SEEDS_DIR = os.path.join(THIS_PROJECT, config['seeds_dir'])
CSV_FILENAMES = config['csvs_filenames']

# outputs
JSON_DIR = os.path.join(THIS_PROJECT, config['json_dir'])
os.makedirs(JSON_DIR, exist_ok=True)

# catalog and dataset info to json
csvs_to_json(filenames=CSV_FILENAMES,
             input_dir=DATA_DIR,
             output_dir=JSON_DIR)

# seeds .csv to .json
csvs_to_json(filenames=os.listdir(SEEDS_DIR),
             input_dir=SEEDS_DIR,
             output_dir=JSON_DIR)
