import bpy
import os
import json

addon_dir = os.path.dirname(os.path.abspath(__file__))

current_index = bpy.context.scene.assetsproperties.asset_index
items = bpy.context.scene.assetsproperties.asset_items

current_asset = items[current_index]

json_file_path = current_asset.get("File_path", "").replace(".py", ".json")

with open(json_file_path, 'r') as json_file:
    asset_data = json.load(json_file)

properties = {key.replace('_property', ''): value for key, value in current_asset.items() if 'property' in key.lower()}

mode = properties.get("Mode", asset_data["Mode_property"])
distance = properties.get("Distance", asset_data["Distance_property"])
bias = properties.get("Bias", asset_data["Bias_property"])
thickness = properties.get("Thickness", asset_data["Thickness_property"])

if mode == 0:
    for obj in bpy.context.selected_objects:
        try:
            obj.data.use_contact_shadow = True
            obj.data.contact_shadow_distance = distance
            obj.data.contact_shadow_bias = bias
            obj.data.contact_shadow_thickness = thickness
        except:
            pass
else:
    for obj in bpy.context.scene.objects:
        try:
            obj.data.use_contact_shadow = True
            obj.data.contact_shadow_distance = distance
            obj.data.contact_shadow_bias = bias
            obj.data.contact_shadow_thickness = thickness
        except:
            pass