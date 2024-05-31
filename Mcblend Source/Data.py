# Properties
import bpy
import os
import json
import zipfile
import traceback
from bpy.props import (IntProperty, BoolProperty, FloatProperty, EnumProperty, StringProperty, PointerProperty)
from bpy.types import PropertyGroup

main_directory = os.path.dirname(os.path.realpath(__file__))
materials_file_path = os.path.join(main_directory, "Materials", "Materials.blend")
materials_folder = os.path.join(main_directory, "Materials")
optimization_folder = os.path.join(main_directory, "Optimization")
assets_directory = os.path.join(main_directory, "Assets")

clouds_node_tree_name = "Clouds Generator 2"
world_material_name = "Mcblend World"
BATGroup = "Better Animate Texture"

Big_Button_Scale = 1.4

Absolute_Solver_Errors = {

    "001": {
        "Error Name": "Unknown",
        "Description": "An Unknown Error",
    },

    "m002": {
        "Error Name": "Empty Material Slot",
        "Description": "Material doesn't exist on slot {Data}",
    },

    "m003": {
        "Error Name": "Object Has No Materials",
        "Description": 'Object "{Data.name}" has no materials',
    },

    "004": {
        "Error Name": ".blend File Not Found",
        "Description": "{Data}.blend not found",
    },
}

def Absolute_Solver(error_code="None", data=None, err=None, error_name=None, description=None):

    def GetASText(error_code, text, data=None):
        if data != None:
            return Absolute_Solver_Errors[error_code][text].format(Data=data)
        else:
            return Absolute_Solver_Errors[error_code][text]

    if data != None:
        bpy.ops.wm.absolute_solver('INVOKE_DEFAULT', Error_Code = error_code, Error_Name = (error_name if error_code != None else GetASText(error_code, 'Error Name')), Description=(GetASText(error_code, 'Description')) if description == None else description.format(Data=data), Tech_Things = str(err) if err != None else "None")
    else:
        bpy.ops.wm.absolute_solver('INVOKE_DEFAULT', Error_Code = error_code, Error_Name = (error_name if error_code != None else GetASText(error_code, 'Error Name')), Description=(GetASText(error_code, 'Description')) if description == None else description, Tech_Things = str(err) if err != None else "None")
        
def checkconfig(name):
    if "const" in main_directory:
        return Preferences_List["Dev"][name]
    else:
        return Preferences_List["Default"][name]
    
def GetConnectedSocketTo(input, tag, material):
    for node in material.node_tree.nodes:
        if node.type == tag:
            for link in node.inputs[input].links:
                for output in link.from_node.outputs:
                    for link in output.links:
                        if link.to_socket.node.name == node.name:
                            return link.from_socket

def InitOnStart():

    if "resource_packs" not in bpy.context.scene:
        bpy.context.scene["resource_packs"] = {}

    items = bpy.context.scene.assetsproperties.asset_items
    items.clear()
    for category, assets in Assets.items():
        for key in assets.keys():
            item = items.add()
            item.name = key
                        
def blender_version(blender_version, debug=None):
    
    try:
        version_parts = blender_version.lower().split(".")
        major, minor, patch = version_parts

        if major != "x":
            major_c = bpy.app.version[0] == int(major)
        else:
            major_c = True
            
        if minor != "x":
            minor_c = bpy.app.version[1] == int(minor)
        else:
            minor_c = True
            
        if patch != "x":
            patch_c = bpy.app.version[2] == int(patch)
        else:
            patch_c = True

        if debug != None:
            print(f"------\nmajor = {major} \nmajor_c = {major_c} \nminor = {minor} \nminor_c = {minor_c} \npatch = {patch} \npatch_c = {patch_c}\n------")
        
        return major_c and minor_c and patch_c
    
    except:
        version_parts = blender_version.split(" ")
        operator = version_parts[0]
        major, minor, patch = version_parts[1].lower().split(".")
        version = (int(major), int(minor), int(patch))
        
        if debug != None:
            print(f"{bpy.app.version} {operator} {version}")

        if operator == '<':
            return bpy.app.version < version
        elif operator == '<=':
            return bpy.app.version <= version
        elif operator == '>':
            return bpy.app.version > version
        elif operator == '>=':
            return bpy.app.version >= version
        elif operator == '==':
            return bpy.app.version == version
        else:
            return False

def get_resource_packs(scene, debug=None):
    if debug is not None:
        print(f"Resource Packs: {scene['resource_packs']}")

    return scene["resource_packs"]

def set_resource_packs(scene, resource_packs, debug=None):
    scene["resource_packs"] = resource_packs

    if debug is not None:
        print(f"Resource Packs: {scene['resource_packs']}")

def update_default_pack(scene, debug=None):
    resource_packs = scene["resource_packs"]

    default_pack = "Minecraft 1.20.1"
    default_path = r"C:\Users\const\OneDrive\Документы\GitHub\Mcblend\Minecraft Assets"
    resource_packs[default_pack] = {"path": default_path, "enabled": True}
    
    if debug is not None:
        print(f"Default Pack: {resource_packs[default_pack]}")

def find_image(image_name, root_folder):
        # Check in the directory
        for dirpath, _, filenames in os.walk(root_folder):
            if image_name in filenames:
                return os.path.join(dirpath, image_name)
        
        # Check in zip files within the directory
        for root, _, files in os.walk(root_folder):
            for file in files:
                if file.endswith('.zip'):
                    with zipfile.ZipFile(os.path.join(root, file), 'r') as zip_ref:
                        for zip_info in zip_ref.infolist():
                            if os.path.basename(zip_info.filename) == image_name:
                                return zip_ref.extract(zip_info, os.path.join(root_folder, 'temp'))
        
        # Check if root folder is a zip file
        if root_folder.endswith('.zip'):
            with zipfile.ZipFile(root_folder, 'r') as zip_ref:
                for zip_info in zip_ref.infolist():
                    if os.path.basename(zip_info.filename) == image_name:
                        return zip_ref.extract(zip_info, os.path.join(os.path.dirname(root_folder), 'temp'))

        return None

Preferences_List = {
    "Dev": {
        "transparent_ui": True,
        "enable_warnings": False,
    },

    "Default": {
        "transparent_ui": False,
        "enable_warnings": True,
    }
}

Render_Settings = {
    
    "Aspirata Cycles": {
        "cycles.use_preview_adaptive_sampling": False,
        "cycles.preview_samples": 128,
        "cycles.use_preview_denoising": True,
        "cycles.preview_denoiser": 'OPENIMAGEDENOISE',
        "cycles.preview_denoising_input_passes": 'RGB_ALBEDO_NORMAL',
        "cycles.preview_denoising_prefilter": 'ACCURATE',
        "cycles.preview_denoising_use_gpu": True,
        "cycles.use_adaptive_sampling": True,
        "cycles.adaptive_threshold": 0.01,
        "cycles.samples": 128,
        "cycles.adaptive_min_samples": 40,
        "cycles.use_denoising": True,
        "cycles.denoiser": 'OPENIMAGEDENOISE',
        "cycles.denoising_input_passes": 'RGB_ALBEDO_NORMAL',
        "cycles.denoising_prefilter": 'ACCURATE',
        "cycles.denoising_quality": 'HIGH',
        "cycles.denoising_use_gpu": True,
        "render.use_persistent_data": True,
        "cycles.max_bounces": 12,
        "cycles.diffuse_bounces": 8,
        "cycles.glossy_bounces": 8,
        "cycles.volume_bounces": 4,
        "cycles.transparent_max_bounces": 1024,
        "render.preview_pixel_size": '2'
    },

    "Aspirata Eevee (Legacy)": {
        "eevee.use_gtao": True,
        "eevee.use_bloom": True,
        "eevee.bloom_radius": 4.0,
        "eevee.sss_samples": 16,
        "eevee.sss_jitter_threshold": 1.0,
        "eevee.use_ssr": True,
        "eevee.use_ssr_refraction": True,
        "eevee.use_ssr_halfres": True,
        "eevee.use_volumetric_shadows": True,
        "eevee.use_shadow_high_bitdepth": True,
        "eevee.shadow_cube_size": '2048',
        "eevee.shadow_cascade_size": '2048',
        "eevee.use_overscan": True,
        "eevee.overscan_size": 10.0
    },

    "Aspirata Eevee":{
        "eevee.eevee.use_shadow_jitter_viewport": True,
        "eevee.shadow_ray_count": 2,
        "eevee.shadow_step_count": 16,
        "eevee.use_volumetric_shadows": True,
        "eevee.use_raytracing": True,
        "eevee.ray_tracing_options.resolution_scale": '4',
        "eevee.ray_tracing_options.trace_max_roughness": 0,
        "eevee.fast_gi_resolution": '4',
        "eevee.use_overscan": True,
        "eevee.overscan_size": 10.0,
    }

}

Emissive_Materials = {

    "Default": {
        "From Min": 0,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
    },

    "sea_lantern": {
        "From Min": 0,
        "From Max": 1,
        "To Min": 0,
        "To Max": 1,
        "Middle Value": 0.4,
        11: 1,
        12: 1.5,
        "Adder": 0.1,
        "Divider": 80,
    },

    "lantern": {
        "From Min": 0,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
        "Middle Value": 0.4,
        11: 1,
        12: 1.5,
        "Adder": 0.1,
        "Divider": 80,
    },

    "glow_lichen": {
        "From Min": 0.18,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
        "Middle Value": 0.4,
        11: 0,
        12: 1,
        "Adder": 0.2,
        "Divider": 50,
    },

    "torch": {
        "From Min": 0,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
        "Middle Value": 0.4,
        11: 0,
        12: 1,
        "Adder": 0.2,
        "Divider": 50,
    },

    "lava": {
        "From Min": 0,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
    },

    "cave_vines_lit": {
        "From Min": 0,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
    },

    "sculk_sensor": {
        "From Min": 0,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
    },

    "glowstone": {
        "From Min": 0,
        "From Max": 2,
        "To Min": 0,
        "To Max": 1,
    },

    "sculk": {
        "From Min": 0,
        "From Max": 0.4,
        "To Min": 0,
        "To Max": 20,
        "Middle Value": 0.4,
        11: 0,
        12: 1,
        "Adder": 0.2,
        "Divider": 50,
    },

    "sculk_vein": {
        "From Min": 0,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
        "Middle Value": 0.4,
        11: -0.5,
        12: 1,
        "Adder": 0.2,
        "Divider": 50,
    },

    "end_rod": {
        "From Min": 0.5,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
        "Middle Value": 0.4,
        11: 0.7,
        12: 1,
        "Adder": 0.2,
        "Divider": 80,
    }

}

# Materials Categories
Backface_Culling_Materials = ["glass", "door", "nether_portal"]

Alpha_Blend_Materials = ["water"]

SSS_Materials = ["leaves", "grass", "tulip", "oxeye_daisy", "dandelion", "poppy", "blue_orchid", "torchflower", "lily_of_the_valley", "cornflower", "allium", "azure bluet"]

Metal = ["iron", "gold", "copper", "diamond", "netherite", "minecart", "lantern", "chain", "anvil", "clock", "cauldron", "spyglass", "rail"]

Reflective = ["glass", "ender", "amethyst", "water", "emerald"]


Materials_Array = {
    
    "bricks": "Upgraded Bricks",

    "diamond_ore": "Upgraded Diamond Ore",

    "glow_lichen": "Upgraded Glow Lichen",

    "gold_block": "Upgraded Gold Block",

    "iron_block": "Upgraded Iron Block",

    "lantern": "Upgraded Lantern",

    "obsidian": "Upgraded Obsidian",

    "sand": "Upgraded Sand",

    "sculk": "Upgraded Sculk",

    "soul_lantern": "Upgraded Soul Lantern",

    "stone": "Upgraded Stone",

    "water_flow": "Upgraded Water Flow"
}

Assets = {
    "Rigs": {
        "SRE V2.0": {
            "Blender_version": "4.x.x",
            "File_name": "Simple_edit_V2.0.blend",
            "Collection_name": "SRE rig"
        },

        "SRE V2.0b732": {
            "Blender_version": "3.6.x",
            "File_name": "Simple_edit_V2.0b732.blend",
            "Collection_name": "SRE rig"
        },

        "Creeper": {
            "Blender_version": "4.x.x",
            "File_name": "Creeper.blend",
            "Collection_name": "Creeper"
        },

        "Allay": {
            "Blender_version": "4.x.x",
            "File_name": "Allay.blend",
            "Collection_name": "Simple Allay"
        },

        "Axolotl": {
            "Blender_version": "4.x.x",
            "File_name": "Axolotl.blend",
            "Collection_name": "Axolotl"
        },

        "Warden": {
            "Blender_version": "4.x.x",
            "File_name": "Warden.blend",
            "Collection_name": "Warden"
        },
    },

    "Scripts": {

        "Sleep After Render": {
            "File_name": "Sleep After Render.py",
        },

        "Convert DBSDF 2 PBSDF": {
            "File_name": "Convert DBSDF 2 PBSDF.py",
        },

        "Fix Shade Auto Smooth": {
            "Blender_version": "< 4.1.0",
            "File_name": "Fix Shade Auto Smooth.py",
        }
    },
}
