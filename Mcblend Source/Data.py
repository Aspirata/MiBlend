# Properties
import bpy
import os
from bpy.props import (IntProperty, BoolProperty, FloatProperty, EnumProperty, StringProperty)
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
        raise ValueError(f"Material doesn't exist on one of the slots. Error code: {Error_Code}")
    
    if Error_Code == 'm003':
        raise ValueError(f"Object: {Data.name} has no materials. Error code: {Error_Code}")

    if Error_Code == '004':
        raise ValueError(f"{os.path.basename(os.path.dirname(os.path.realpath(__file__)))}.blend not found. Error code: {Error_Code}")
    
    if Error_Code == 'm005':
        raise ValueError(f"Mcblend Sky node not found, maybe you should reappend sky material ? Error code: {Error_Code}")
    
    if Error_Code == '006':
        raise ValueError(f"There is no camera in the scene. Error code: {Error_Code}")

Emissive_Materials = {

    "Default": {
        "From Min": 0,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
        "Exclude": "None"
    },

    "lantern": {
        "From Min": 0,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
        "Middle Value": 0.4,
        9: 1,
        10: 1.5,
        "Adder": 0.1,
        "Divider": 80,
        "Exclude": "sea_lantern"
    },

    "glow_lichen": {
        "From Min": 0.18,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
        "Middle Value": 0.4,
        9: 0,
        10: 1,
        "Adder": 0.2,
        "Divider": 50,
        "Exclude": "None"
    },

    "torch": {
        "From Min": 0,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
        "Middle Value": 0.4,
        9: 0,
        10: 1,
        "Adder": 0.2,
        "Divider": 50,
        "Exclude": "None"
    },

    "lava": {
        "From Min": 0,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
        "Exclude": "None"
    },

    "cave_vines_lit": {
        "From Min": 0,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
        "Exclude": "None"
    },

    "sculk_sensor": {
        "From Min": 0,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
        "Exclude": "None"
    },

    "glowstone": {
        "From Min": 0,
        "From Max": 2,
        "To Min": 0,
        "To Max": 1,
        "Exclude": "None"
    },

    "sculk": {
        "From Min": 0,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
        "Middle Value": 0.4,
        9: 0,
        10: 1,
        "Adder": 0.2,
        "Divider": 50,
        "Exclude": "sculk_catalyst, sculk_sensor, sculk_shrieker, sculk_vein"
    },

    "end_rod": {
        "From Min": 0.5,
        "From Max": 0.6,
        "To Min": 0,
        "To Max": 1,
        "Middle Value": 0.4,
        9: 0.7,
        10: 1,
        "Adder": 0.2,
        "Divider": 80,
        "Exclude": "None"
    }

}

Backface_Culling_Materials = [
    "glass",
    "door"
]

Alpha_Blend_Materials = [
    "water",
    "ice"
]

SSS_Materials = [
    "leaves",
    "grass",
    "tulip"
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
    "spyglass"
]

Reflective = [
    "glass",
    "ender",
    "amethyst",
    "water"
]

Materials_Array = {
    "Bricks": {
        "Original Material": "bricks",
        "Upgraded Material": "Upgraded Bricks",
        "Exclude": "stone_bricks, nether_bricks, prismarine_bricks, deepslate_bricks, tuff_bricks, mud_bricks"
    },

    "Diamond Ore": {
        "Original Material": "diamond_ore",
        "Upgraded Material": "Upgraded Diamond Ore",
        "Exclude": "deepslate_diamond_ore"
    },

    "Glow Lichen": {
        "Original Material": "glow_lichen",
        "Upgraded Material": "Upgraded Glow Lichen",
        "Exclude": "None"
    },

    "Gold Block": {
        "Original Material": "gold_block",
        "Upgraded Material": "Upgraded Gold Block",
        "Exclude": "None"
    },

    "Iron Block": {
        "Original Material": "iron_block",
        "Upgraded Material": "Upgraded Iron Block",
        "Exclude": "None"
    },

    "Lantern": {
        "Original Material": "lantern",
        "Upgraded Material": "Upgraded Lantern",
        "Exclude": "soul_lantern, redstone_lamp"
    },

    "Obsidian": {
        "Original Material": "obsidian",
        "Upgraded Material": "Upgraded Obsidian",
        "Exclude": "crying_obsidian"
    },

    "Sand": {
        "Original Material": "sand",
        "Upgraded Material": "Upgraded Sand",
        "Exclude": "red_sand, sandstone, soul_sand"
    },

    "Sculk": {
        "Original Material": "sculk",
        "Upgraded Material": "Upgraded Sculk",
        "Exclude": "sculk_catalyst, sculk_sensor, sculk_shrieker, sculk_vein"
    },

    "Soul Lantern": {
        "Original Material": "soul_lantern",
        "Upgraded Material": "Upgraded Soul Lantern",
        "Exclude": "redstone_lamp"
    },

    "Stone": {
        "Original Material": "stone",
        "Upgraded Material": "Upgraded Stone",
        "Exclude": "cobblestone. smooth_stone, redstone, blackstone, glowstone, end_stone"
    },

    "Water Flow": {
        "Original Material": "water_flow",
        "Upgraded Material": "Upgraded Water Flow",
        "Exclude": "None"
    }
}

Assets = {
    "SRE": {
        "Name": "Simple Player Rig",
        "Type": "Rigs",
        ".blend_name": "Simple_edit_V2.0.blend",
        "Collection_name": "SRE rig"
    },

    "Creeper": {
        "Name": "Creeper",
        "Type": "Rigs",
        ".blend_name": "Creeper.blend",
        "Collection_name": "Creeper"
    },

    "Allay": {
        "Name": "Allay Rig",
        "Type": "Rigs",
        ".blend_name": "Allay.blend",
        "Collection_name": "Simple Allay"
    },

    "Axolotl": {
        "Name": "Axolotl Rig",
        "Type": "Rigs",
        ".blend_name": "Axolotl.blend",
        "Collection_name": "Axolotl"
    },

    "Warden": {
        "Name": "Warden",
        "Type": "Rigs",
        ".blend_name": "Warden.blend",
        "Collection_name": "Warden"
    }
}