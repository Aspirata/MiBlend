# Properties
from unittest.mock import patch
import bpy
import os
from bpy.props import (IntProperty, BoolProperty, FloatProperty, EnumProperty, StringProperty, PointerProperty)
from bpy.types import PropertyGroup

main_directory = os.path.dirname(os.path.realpath(__file__))
materials_file_path = os.path.join(main_directory, "Materials", "Materials.blend")
materials_folder = os.path.join(main_directory, "Materials")
optimization_folder = os.path.join(main_directory, "Optimization")

clouds_node_tree_name = "Clouds Generator 2"
world_material_name = "Mcblend World"
BATGroup = "Better Animate Texture"

Big_Button_Scale = 1.4

def CEH(Error_Code, Data=None):

    if Error_Code == 'm002':
        raise ValueError(f"Material doesn't exist on slot {Data}. Error code: {Error_Code} DO NOT REPORT")
    
    if Error_Code == 'm003':
        raise ValueError(f"Object: {Data.name} has no materials. Error code: {Error_Code} DO NOT REPORT")

    if Error_Code == '004':
        raise ValueError(f"{os.path.basename(os.path.dirname(os.path.realpath(__file__)))}.blend not found. Error code: {Error_Code} DO NOT REPORT")
    
    if Error_Code == 'm005':
        raise ValueError(f"Mcblend Sky node not found, maybe you should reappend sky material ? Error code: {Error_Code} DO NOT REPORT")
    
    if Error_Code == '006':
        raise ValueError(f"There is no camera in the scene. Error code: {Error_Code} DO NOT REPORT")
    
    if Error_Code == '007':
        raise ValueError(f"Object {Data.name} has type {Data.type}, this type has no vertex groups. Error code: {Error_Code} DO NOT REPORT")

def checkconfig(name):
    if "const" in main_directory:
        return Preferences_List["Dev"][name]
    else:
        return Preferences_List["Default"][name]
    
def blender_version(blender_version, debug=None):
    major, minor, patch = blender_version.lower().split(".")

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
        print(f"----\nmajor = {major} \nmajor_c = {major_c} \nminor = {minor} \nminor_c = {minor_c} \npatch = {patch} \npatch_c = {patch_c}\n-----")
    return major_c and minor_c and patch_c

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
        "cycles.preview_denoising_input_passes": 'RGB_ALBEDO_NORMAL',
        "cycles.preview_denoising_prefilter": 'ACCURATE',
        "cycles.denoising_use_gpu": True,
        "render.use_persistent_data": True,
        "cycles.max_bounces": 12,
        "cycles.diffuse_bounces": 8,
        "cycles.glossy_bounces": 8,
        "cycles.volume_bounces": 4,
        "cycles.transparent_max_bounces": 1024,
        "render.preview_pixel_size": '2'
    },

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

Backface_Culling_Materials = [
    "glass",
    "door",
    "nether_portal",
]

Alpha_Blend_Materials = [
    "water"
]

SSS_Materials = [
    "leaves",
    "grass",
    "tulip",
    "oxeye_daisy",
    "dandelion",
    "poppy",
    "blue_orchid",
    "torchflower",
    "lily_of_the_valley",
    "cornflower",
    "allium",
    "azure bluet",
]

Metal = [
    "iron",
    "gold",
    "copper",
    "diamond",
    "netherite",
    "minecart",
    "lantern",
    "chain",
    "anvil",
    "clock",
    "cauldron",
    "spyglass",
    "rail",
]

Reflective = [
    "glass",
    "ender",
    "amethyst",
    "water",
    "emerald",
]

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
    "SRE V2.0": {
        "Name": "SRE V2.0",
        "Type": "Rigs",
        "Blender Version": "4.x.x",
        ".blend_name": "Simple_edit_V2.0.blend",
        "Collection_name": "SRE rig"
    },

    "SRE V2.0b732": {
        "Name": "SRE V2.0b732",
        "Type": "Rigs",
        "Blender Version": "3.6.x",
        ".blend_name": "Simple_edit_V2.0b732.blend",
        "Collection_name": "SRE rig"
    },

    "Creeper": {
        "Name": "Creeper",
        "Type": "Rigs",
        "Blender Version": "4.x.x",
        ".blend_name": "Creeper.blend",
        "Collection_name": "Creeper"
    },

    "Allay": {
        "Name": "Allay Rig",
        "Type": "Rigs",
        "Blender Version": "4.x.x",
        ".blend_name": "Allay.blend",
        "Collection_name": "Simple Allay"
    },

    "Axolotl": {
        "Name": "Axolotl Rig",
        "Type": "Rigs",
        "Blender Version": "4.x.x",
        ".blend_name": "Axolotl.blend",
        "Collection_name": "Axolotl"
    },

    "Warden": {
        "Name": "Warden",
        "Type": "Rigs",
        "Blender Version": "4.x.x",
        ".blend_name": "Warden.blend",
        "Collection_name": "Warden"
    }
}