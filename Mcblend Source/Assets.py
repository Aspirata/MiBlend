from .Data import *
from .MCB_API import *
import sys
from .Utils.Absolute_Solver import Absolute_Solver

def get_asset_path(category, asset_name):

    try:
        asset_data = Assets[category][asset_name]
        asset_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Assets", category, asset_data["File_name"])
        return asset_path, asset_data
    except KeyError:
        print(f"Asset '{asset_name}' in category '{category}' not found.")
        return None, None
    
def append_asset(asset_name, asset_category):
    asset_path, asset_data = get_asset_path(asset_category, asset_name)
    if asset_path is None:
        return
    
    try:
        if asset_category == "Rigs":
            collection_name = asset_data["Collection_name"]

            with bpy.data.libraries.load(asset_path, link=False) as (data_from, data_to):
                data_to.collections = [collection_name]

            for collection in data_to.collections:
                bpy.context.collection.children.link(collection)

        elif asset_category == "Scripts":
            run_python_script(asset_path)
        
    except:
        Absolute_Solver(tech_things=traceback.print_exc(), data=asset_name, error_name="Bad Asset Import", description="Can't Import {Data} Asset")

def update_assets():

    # Assets

    items = bpy.context.scene.assetsproperties.asset_items
    items.clear()

    dprint(sorted(Assets.keys()))
    for key in sorted(Assets.keys()):
        dprint(key)
        item = items.add()
        item.name = key

    # Tags

    tags = bpy.context.scene.assetsproperties.tags
    tags.clear()
    unique_tags = set()

    for asset_data in Assets.values():
        asset_tags = asset_data.get("Tags", [])
        unique_tags.update(asset_tags)

    unique_tags.add("All")
    unique_tags = sorted(unique_tags)

    for tag in unique_tags:
        item = tags.add()
        item.name = tag
        if tag == "All":
            item.enabled = True
    
def run_python_script(file_path):

    def import_all_from_module(module_name, module_path=None):
        if module_path:
            if module_path not in sys.path:
                sys.path.append(module_path)
        module = __import__(module_name, fromlist=['*'])
        return {name: getattr(module, name) for name in dir(module) if not name.startswith('__')}

    try:
        global_context = {'__name__': '__main__'}
        additional_globals = import_all_from_module('Data', os.path.join(os.path.dirname(__file__)))
        
        if additional_globals:
            global_context.update(additional_globals)
        
        with open(file_path, 'r') as file:
            exec(file.read(), global_context)
    except:
        Absolute_Solver(tech_things=traceback.print_exc(), data=file_path, error_name="Bad Script Execution", description="Can't Execute Script from {Data}")

Assets = {
    "SRE V2.0": {
        "Blender_version": "4.x.x",
        "File_name": "Simple_edit_V2.0.blend",
        "Collection_name": "SRE rig",
        "Tags": ["Rig", "Vanilla"]
    },

    "SRE V2.0b732": {
        "Blender_version": "3.6.x",
        "File_name": "Simple_edit_V2.0b732.blend",
        "Collection_name": "SRE rig",
        "Tags": ["Rig", "Vanilla"]
    },

    "Creeper": {
        "Blender_version": "4.x.x",
        "File_name": "Creeper.blend",
        "Collection_name": "Creeper",
        "Tags": ["Rig", "Vanilla"]
    },

    "Allay": {
        "Blender_version": "4.x.x",
        "File_name": "Allay.blend",
        "Collection_name": "Simple Allay",
        "Tags": ["Rig", "Vanilla"]
    },

    "Axolotl": {
        "Blender_version": "4.x.x",
        "File_name": "Axolotl.blend",
        "Collection_name": "Axolotl",
        "Tags": ["Rig", "Vanilla"]
    },

    "Warden": {
        "Blender_version": "4.x.x",
        "File_name": "Warden.blend",
        "Collection_name": "Warden",
        "Tags": ["Rig", "Vanilla"]
    },

    "Sleep After Render": {
        "File_name": "Sleep After Render.py",
        "Tags": ["Script"]
    },

    "Convert DBSDF 2 PBSDF": {
        "File_name": "Convert DBSDF 2 PBSDF.py",
        "Tags": ["Script"]
    },

    "Fix Shade Auto Smooth": {
        "Blender_version": "< 4.1.0",
        "File_name": "Fix Shade Auto Smooth.py",
        "Tags": ["Script"]
    },

    "Enable Jittered Shadows": {
        "Blender_version": ">= 4.2.0",
        "File_name": "Jittered Shadows.py",
        "Tags": ["Script"]
    },

    "Enable Contact Shadows": {
        "Blender_version": "< 4.2.0",
        "File_name": "Contact Shadows.py",
        "Tags": ["Script"]
    },

    "ACES Textures Fix": {
        "File_name": "ACES Textures Fix.py",
        "Tags": ["Script"]
    },
}
