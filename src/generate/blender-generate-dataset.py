# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 22:20:00 2022

@author: Mico
"""

import bpy
import json
import os
import random

def place_tree(asset_name, scale, position):
    sx, sy, sz = scale
    x, y, z = position
    src_obj = bpy.data.objects[asset_name]
    
    new_obj = src_obj.copy()
    new_obj.data = src_obj.data.copy()
    new_obj.animation_data_clear()
    new_obj.location = (x, y, z)
    new_obj.scale = (sx, sy, sz)
    bpy.context.collection.objects.link(new_obj)
    
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

def clean_scene(assets_to_keep):
    bpy.ops.object.select_all(action='SELECT')
    for obj_name in assets_to_keep:
        bpy.data.objects[obj_name].select_set(False)
    bpy.ops.object.delete()

def export_scene(output_folder, filename):
    obj_path = os.path.join(output_folder, filename +'.obj')
    bpy.ops.export_scene.obj(filepath=obj_path,
                             group_by_object=True,
                             group_by_material=True,
                             use_mesh_modifiers=True,
                             use_edges=True,
                             use_normals=True,
                             use_uvs=True,
                             use_materials=True,
                             use_vertex_groups=True,
                             axis_up='Z',
                             axis_forward='Y'
                             )
    
data_folder = r'C:\Users\Mico\Desktop\gitlab\carbon-stock-simulation\data\json'
output_folder = r'C:\Users\Mico\Desktop\gitlab\carbon-stock-simulation\data\export\obj'

info_path = os.path.join(data_folder, 'dataset_info.json') 
catalog_low_path = os.path.join(data_folder, 'catalog_low.json')
catalog_mid_path = os.path.join(data_folder, 'catalog_mid.json')
 
df_info = read_json(info_path)
df_low = read_json(catalog_low_path)
df_mid = read_json(catalog_mid_path)

mid_assets_names = [df_mid['name'][key] for key in df_mid['name'].keys()]
low_assets_names = [df_low['name'][key] for key in df_low['name'].keys()]
assets_to_keep = low_assets_names + mid_assets_names
sotobosque_th = 2.5
resolution = 0.12
"""
for filename in os.listdir(output_folder):
    if '.obj' in filename:
        print(filename)
        create_flag(output_folder, filename.replace('.obj', ''))
"""
for info_index in df_info['filename'].keys():
    filename = df_info['filename'][info_index]
    if create_flag(output_folder, filename): #filename+'.obj' in os.listdir(output_folder):
        pass
    else:
        ytotal = df_info['ytotal'][info_index]
        df_seed_path = os.path.join(data_folder, 'seeds', filename + '.json')
        df_seed = read_json(df_seed_path)
        
        for seed_index in df_seed['height'].keys():
            seed_h = df_seed['height'][seed_index]
            if seed_h < sotobosque_th:
                asset_index = random.choice(list(df_low['name'].keys()))
                asset_name = df_low['name'][asset_index]
                asset_h = df_low['height'][asset_index]
            else:
                asset_index = random.choice(list(df_mid['name'].keys()))
                asset_name = df_mid['name'][asset_index]
                asset_h = df_mid['height'][asset_index]
                
            z_scale = seed_h/asset_h
            x_scale = z_scale #random.uniform(0.9, 1.1)
            y_scale = z_scale #random.uniform(0.9, 1.1)
    
            x_pos = df_seed['x'][seed_index]*resolution
            y_pos = (ytotal-df_seed['y'][seed_index])*resolution
            z_pos = 0 # TODO: use DEM
            
            place_tree(asset_name = asset_name,
                       scale = (x_scale, y_scale, z_scale),
                       position = (x_pos, y_pos, z_pos))
        # TODO: export obj
        export_scene(output_folder, filename)
        # TODO: clean scene
        #clean_scene(assets_to_keep)
        break