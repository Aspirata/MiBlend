# Properties
import bpy
import os
from bpy.props import (IntProperty, BoolProperty, FloatProperty, EnumProperty, StringProperty)

main_directory = os.path.dirname(os.path.realpath(__file__))
materials_file_path = os.path.join(main_directory, "Materials", "Materials.blend")

clouds_node_tree_name = "Clouds Generator 2"
world_material_name = "Mcblend World"
node_tree_name = "Procedural Animation V1.1"

Big_Button_Scale = 1.4

def CEH(Error_Code, Data=None):

    if  Error_Code == 'm002':
        raise ValueError(f"Material doesn't exist on one of the slots, error code: {Error_Code}")
    
    if Error_Code == 'm003':
        raise ValueError(f"Object: {Data.name} has no materials, error code: {Error_Code}")

    if  Error_Code == '004':
        raise ValueError(f"{os.path.basename(os.path.dirname(os.path.realpath(__file__)))}.blend not found, error code: {Error_Code}")
    
    if  Error_Code == 'm005':
        raise ValueError(f"Mcblend Sky node not found, maybe you should recreate sky ? Error code: {Error_Code}")

Emissive_Materials = {
    "lantern": {
        "Interpolation Type": "SMOOTHSTEP",
        1: 0, # From Min
        2: 0.6, # From Max
        3: 0, # To Min
        4: 2, # To Max
        "Animate": True,
        "Multiplier": 1,
        "Middle Value": 0.4,
        "To Min": 1,
        "To Max": 1.5,
        "Adder": 0.1,
        "Divider": 80,
        "Exclude": "None"
    },

    "glow_lichen": {
        "Interpolation Type": "SMOOTHSTEP",
        1: 0, # From Min
        2: 0.6, # From Max
        3: 0, # To Min
        4: 2, # To Max
        "Animate": True,
        "Multiplier": 1,
        "Middle Value": 0.4,
        "To Min": 0,
        "To Max": 1,
        "Adder": 0.2,
        "Divider": 50,
        "Exclude": "None"
    },

    "torch": {
        "Interpolation Type": "SMOOTHSTEP",
        1: 0, # From Min
        2: 0.6, # From Max
        3: 0, # To Min
        4: 2, # To Max
        "Animate": True,
        "Multiplier": 1,
        "Middle Value": 0.4,
        "To Min": 0,
        "To Max": 1,
        "Adder": 0.2,
        "Divider": 50,
        "Exclude": "None"
    },

    "lava": {
        "Interpolation Type": "SMOOTHSTEP",
        1: 0, # From Min
        2: 0.6, # From Max
        3: 0, # To Min
        4: 2, # To Max
        "Animate": False,
        "Exclude": "None"
    },

    "cave_vines_lit": {
        "Interpolation Type": "SMOOTHSTEP",
        1: 0, # From Min
        2: 0.6, # From Max
        3: 0, # To Min
        4: 2, # To Max
        "Animate": False,
        "Exclude": "None"
    },

    "sculk_sensor": {
        "Interpolation Type": "SMOOTHSTEP",
        1: 0, # From Min
        2: 0.6, # From Max
        3: 0, # To Min
        4: 2, # To Max
        "Animate": False,
        "Exclude": "None"
    },

    "glowstone": {
        "Interpolation Type": "SMOOTHSTEP",
        1: 0, # From Min
        2: 2, # From Max
        3: 0, # To Min
        4: 2, # To Max
        "Animate": False,
        "Exclude": "None"
    },

    "sculk": {
        "Interpolation Type": "SMOOTHSTEP",
        1: 0, # From Min
        2: 0.6, # From Max
        3: 0, # To Min
        4: 2, # To Max
        "Animate": True,
        "Multiplier": 1,
        "Middle Value": 0.4,
        "To Min": 0,
        "To Max": 1,
        "Adder": 0.2,
        "Divider": 50,
        "Exclude": "sculk_catalyst, sculk_sensor, sculk_shrieker, sculk_vein"
    },

    "end_rod": {
        "Interpolation Type": "SMOOTHSTEP",
        1: 0.5, # From Min
        2: 0.6, # From Max
        3: 0, # To Min
        4: 2, # To Max
        "Animate": True,
        "Multiplier": 1,
        "Middle Value": 0.4,
        "To Min": 0.7,
        "To Max": 1,
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
    "glass",
    "ice"
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
        "Exclude": "soul_lantern, redstone_lamp, sea_lantern"
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
        "Exclude": "cobblestone. smooth_stone, redstone, blackstone, glowstone"
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