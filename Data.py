# Properties
import bpy
import os
from bpy.props import (IntProperty, BoolProperty, FloatProperty, EnumProperty, StringProperty)
node_tree_name = "Clouds Generator 2"
world_material_name = "Mcblend World"
node_tree_name = "Procedural Animation V1.1"

Big_Button_Scale = 1.4

Emissive_Materials = {
    "lantern": {
        "Interpolation Type": "SMOOTHSTEP",
        1: 0, # From Min
        2: 0.6, # From Max
        3: 0, # To Min
        4: 2, # To Max
    },

    "glow_lichen": {
        "Interpolation Type": "SMOOTHSTEP",
        1: 0, # From Min
        2: 0.6, # From Max
        3: 0, # To Min
        4: 2, # To Max
    },

    "torch": {
        "Interpolation Type": "SMOOTHSTEP",
        1: 0, # From Min
        2: 0.6, # From Max
        3: 0, # To Min
        4: 2, # To Max
    },

    "lava": {
        "Interpolation Type": "SMOOTHSTEP",
        1: 0, # From Min
        2: 0.6, # From Max
        3: 0, # To Min
        4: 2, # To Max
    },

    "cave_vines_lit": {
        "Interpolation Type": "SMOOTHSTEP",
        1: 0, # From Min
        2: 0.6, # From Max
        3: 0, # To Min
        4: 2, # To Max
    },

    "sculk_catalyst": {
        "Interpolation Type": "SMOOTHSTEP",
        1: 0, # From Min
        2: 0.6, # From Max
        3: 0, # To Min
        4: 2, # To Max
    },

    "sculk_sensor": {
        "Interpolation Type": "SMOOTHSTEP",
        1: 0, # From Min
        2: 0.6, # From Max
        3: 0, # To Min
        4: 2, # To Max
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

Animatable_Materials = {
    "sculk": {
        "Multiplier": 1,
        "Middle Value": 0.4,
        "To Min": 0,
        "To Max": 1,
        "Adder": 0.2,
        "Divider": 50,
    },

    "glow_lichen": {
        "Multiplier": 1,
        "Middle Value": 0.4,
        "To Min": 0,
        "To Max": 1,
        "Adder": 0.2,
        "Divider": 50,
    },

    "lantern": {
        "Multiplier": 1,
        "Middle Value": 0.4,
        "To Min": 1,
        "To Max": 1.5,
        "Adder": 0.1,
        "Divider": 80,
    },

    "torch": {
        "Multiplier": 1,
        "Middle Value": 0.4,
        "To Min": 0,
        "To Max": 1,
        "Adder": 0.2,
        "Divider": 50,
    }
}

Materials = {
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
        "Exclude": "soul_lantern"
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
        "Exclude": "None"
    },

    "Stone": {
        "Original Material": "stone",
        "Upgraded Material": "Upgraded Stone",
        "Exclude": "cobblestone. smooth_stone, redstone, blackstone"
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

    "Strider": {
        "Name": "Strider",
        "Type": "Rigs",
        ".blend_name": "Edited Pooka's Rigs.blend",
        "Collection_name": "Strider"
    },

    "Dolphin": {
        "Name": "Dolphin",
        "Type": "Rigs",
        ".blend_name": "Edited Pooka's Rigs.blend",
        "Collection_name": "Dolphin"
    },

    "Warden": {
        "Name": "Warden",
        "Type": "Rigs",
        ".blend_name": "Edited Pooka's Rigs.blend",
        "Collection_name": "Warden"
    },

    "Frog": {
        "Name": "Frog",
        "Type": "Rigs",
        ".blend_name": "Edited Pooka's Rigs.blend",
        "Collection_name": "Frog"
    },

    "Breeze": {
        "Name": "Breeze",
        "Type": "Rigs",
        ".blend_name": "Edited Pooka's Rigs.blend",
        "Collection_name": "Breeze"
    },

    "Shulker Box": {
        "Name": "Shulker Box",
        "Type": "Rigs",
        ".blend_name": "Edited Pooka's Rigs.blend",
        "Collection_name": "Shulker Box"
    },

    "Goat": {
        "Name": "Goat",
        "Type": "Rigs",
        ".blend_name": "Edited Pooka's Rigs.blend",
        "Collection_name": "Goat"
    },

    "Camel": {
        "Name": "Camel",
        "Type": "Rigs",
        ".blend_name": "Edited Pooka's Rigs.blend",
        "Collection_name": "Camel"
    },
}