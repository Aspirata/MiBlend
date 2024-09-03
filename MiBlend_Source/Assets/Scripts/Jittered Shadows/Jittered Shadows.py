import bpy
import os
import json

addon_dir = os.path.dirname(os.path.abspath(__file__))

current_index = bpy.context.scene.assetsproperties.asset_index
items = bpy.context.scene.assetsproperties.asset_items

current_asset = items[current_index]

json_file_path = os.path.join(addon_dir, "Assets", os.path.splitext(current_asset.get("File_path", ""))[0] + ".json")

with open(json_file_path, 'r') as json_file:
    asset_data = json.load(json_file)

properties = {key.replace('_property', ''): value for key, value in current_asset.items() if 'property' in key.lower()}

mode = properties.get("Mode", asset_data["Mode_property"])
overblur = properties.get("Overblur", asset_data["Overblur_property"])
world_jitter = properties.get("World Jitter", asset_data["World Jitter_property"])

if mode == 0:
    for obj in bpy.context.selected_objects:
        try:
            obj.data.use_shadow_jitter = True
            obj.data.shadow_jitter_overblur = overblur
        except:
            pass
else:
    for obj in bpy.context.scene.objects:
        try:
            obj.data.use_shadow_jitter = True
            obj.data.shadow_jitter_overblur = overblur
        except:
            pass
    

if bpy.context.scene.world != None and world_jitter:
    bpy.context.scene.world.use_sun_shadow_jitter = True
    bpy.context.scene.world.sun_shadow_jitter_overblur = overblur