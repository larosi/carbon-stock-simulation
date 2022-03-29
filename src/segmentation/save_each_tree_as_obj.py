# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 09:48:59 2022

@author: Mico
"""

import bpy
import json
import os
import pathlib

def read_json(json_path):
    f = open(json_path)
    data = json.load(f)
    f.close()
    return data


def export_selected_obj(output_folder, filename):
    obj_path = os.path.join(output_folder, filename + '.obj')
    bpy.ops.export_scene.obj(filepath=obj_path,
                             use_selection=True,
                             group_by_object=True,
                             group_by_material=True,
                             use_mesh_modifiers=True,
                             use_edges=True,
                             use_normals=True,
                             use_uvs=True,
                             use_materials=True,
                             use_vertex_groups=True,
                             path_mode='COPY',
                             axis_up='Z',
                             axis_forward='Y')


# FIXME: change for your PC path
PROJECT_NAME = 'carbon-stock-simulation'
THIS_PATH = str(pathlib.Path(__file__).parent.absolute())
THIS_PROJECT = str(pathlib.Path(THIS_PATH.split(PROJECT_NAME)[0]))
THIS_PROJECT = os.path.join(THIS_PROJECT, PROJECT_NAME)

DATA_DIR = os.path.join(THIS_PROJECT, 'data', 'json')
OUTPUT_DIR = os.path.join(THIS_PROJECT, 'data', 'export', 'trees_obj')
os.makedirs(OUTPUT_DIR, exist_ok=True)

catalog_low_path = os.path.join(DATA_DIR, 'catalog_low.json')
catalog_mid_path = os.path.join(DATA_DIR, 'catalog_mid.json')

df_low = read_json(catalog_low_path)
df_mid = read_json(catalog_mid_path)

tree_names = list(df_low['name'].values()) + list(df_mid['name'].values())

for tree_name in tree_names:
    # deselect all objs in the scene
    bpy.ops.object.select_all(action='DESELECT')

    # select an obj by the name
    bpy.data.objects[tree_name].select_set(True)

    # scale to 1:1
    bpy.data.objects[tree_name].scale = (1, 1, 1)

    # export it as .obj and .mtl
    export_selected_obj(output_folder=OUTPUT_DIR, filename=tree_name)

    # TODO: copy the textures files to OUTPUT_DIR too
