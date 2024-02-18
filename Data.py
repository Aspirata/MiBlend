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
    "bricks": "Upgraded Bricks",
    "cobblestone": "Exclude",
    "diamond_ore": "Upgraded Diamond Ore",
    "deepslate_diamond_ore": "Exclude",
    "glow_lichen": "Upgraded Glow Lichen",
    "gold_block": "Upgraded Gold Block",
    "iron_block": "Upgraded Iron Block",
    "lantern": "Upgraded Lantern",
    "obsidian": "Upgraded Obsidian",
    "sand": "Upgraded Sand",
    "red_sand": "Exclude",
    "sandstone": "Exclude",
    "chiseled_red_sandstone": "Exclude",
    "cut_red_sandstone": "Exclude",
    "smooth_red_sandstone": "Exclude",
    "sandstone_slab": "Exclude",
    "sandstone_stairs": "Exclude",
    "sandstone_wall": "Exclude",
    "red_sandstone_slab": "Exclude",
    "red_sandstone_stairs": "Exclude",
    "red_sandstone_wall": "Exclude",
    "soul_sand": "Exclude",
    "sculk": "Upgraded Sculk",
    "sculk_catalyst": "Exclude",
    "sculk_sensor": "Exclude",
    "calibrated_sculk_sensor": "Exclude",
    "sculk_shrieker": "Exclude",
    "sculk_vein": "Exclude",
    "soul_lantern": "Upgraded Soul Lantern",
    "stone": "Upgraded Stone",
    "smooth_stone": "Exclude",
    "chiseled_stone_bricks": "Exclude",
    "mossy_cobblestone": "Exclude",
    "mossy_stone_bricks": "Exclude",
    "smooth_red_sandstone": "Exclude",
    "smooth_sandstone": "Exclude",
    "stone_bricks": "Exclude",
    "blackstone": "Exclude",
    "blackstone_slab": "Exclude",
    "blackstone_stairs": "Exclude",
    "blackstone_wall": "Exclude",
    "water_flow": "Upgraded Water Flow",
    "chiseled_red_sandstone_bricks": "Exclude",
    "cracked_deepslate_bricks": "Exclude",
    "cracked_nether_bricks": "Exclude",
    "cracked_polished_blackstone_bricks": "Exclude",
    "mossy_cobblestone_bricks": "Exclude",
    "mossy_stone_bricks": "Exclude",
    "nether_bricks": "Exclude",
    "polished_blackstone_bricks": "Exclude",
    "red_nether_bricks": "Exclude",
    "red_sandstone_bricks": "Exclude",
    "warped_wart_block_bricks": "Exclude"
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
        ".blend_name": "Rig-creeper.blend",
        "Collection_name": "Creeper"
    },

    "Allay": {
        "Name": "Allay Rig",
        "Type": "Rigs",
        ".blend_name": "Allay Rig.blend",
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