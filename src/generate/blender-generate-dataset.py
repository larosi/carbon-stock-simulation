# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 22:20:00 2022

@author: Mico
"""

import bpy
import json
import os
import pathlib


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


def set_boundary_plane(xtotal, ytotal, ztotal=-10):
    print('create_boundary_plane')
    src_obj = bpy.data.objects['Plane']
    src_obj.location = (xtotal/2,  ytotal/2, ztotal)
    src_obj.scale = (xtotal/2, ytotal/2, 1)
    print('create_boundary_plane done.')


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
    obj_path = os.path.join(output_folder, filename + '.obj')
    bpy.ops.export_scene.obj(filepath=obj_path,
                             use_selection=False,
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


PROJECT_NAME = 'carbon-stock-simulation'
THIS_PATH = str(pathlib.Path(__file__).parent.absolute())
PROJECT_ROOT = str(pathlib.Path(THIS_PATH.split(PROJECT_NAME)[0]))
PROJECT_ROOT = os.path.join(PROJECT_ROOT, PROJECT_NAME)

DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

input_folder = os.path.join(DATA_DIR, 'json')
output_folder = os.path.join(DATA_DIR, 'export', 'obj')

os.makedirs(output_folder, exist_ok=True)

info_path = os.path.join(input_folder, 'dataset_info.json')
df_info = read_json(info_path)
resolution = 0.12

for info_index in df_info['filename'].keys():
    filename = df_info['filename'][info_index]
    if create_flag(output_folder, filename):
        pass
    else:
        xtotal = df_info['xtotal'][info_index]
        ytotal = df_info['ytotal'][info_index]

        set_boundary_plane(xtotal*resolution, ytotal*resolution)

        df_seed_path = os.path.join(input_folder, filename + '.json')
        df_seed = read_json(df_seed_path)

        for seed_index in df_seed['height'].keys():
            seed_h = df_seed['height'][seed_index]
            asset_name = df_seed['tree_name'][seed_index]

            z_scale = df_seed['scale_z'][seed_index]
            x_scale = df_seed['scale_x'][seed_index]
            y_scale = df_seed['scale_y'][seed_index]

            x_pos = df_seed['x'][seed_index]*resolution
            y_pos = (ytotal-df_seed['y'][seed_index])*resolution
            z_pos = 0

            place_tree(asset_name=asset_name,
                       scale=(x_scale, y_scale, z_scale),
                       position=(x_pos, y_pos, z_pos))

        export_scene(output_folder, filename)
        # TODO: clean scene
        break
