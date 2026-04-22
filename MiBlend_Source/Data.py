import os

main_directory = os.path.dirname(os.path.realpath(__file__))
materials_folder = os.path.join(main_directory, "Materials")
nodes_file = os.path.join(materials_folder, "Nodes.blend")
assets_directory = os.path.join(main_directory, "Assets")
utils_directory = os.path.join(main_directory, "Utils")

clouds_node_tree_name = "Clouds Generator 2"
fog_node_tree_name = "Fog"
world_material_name = "MiBlend World"

Grass_Color = {
    "Forest": (0.226964, 0.617207, 0.088656),
    "Birch": (0.242279, 0.396756, 0.16203),
    "Taiga": (0.25415, 0.467784, 0.250158),
    "Dark Forest": (0.021219, 0.03434, 0.003035),
    "Bad Land": (0.278893, 0.219526, 0.074214),
}

Foliage_Color = {
    "Forest": (0.227161, 0.614651, 0.089036),
    "Taiga": (0.152925, 0.366253, 0.147027),
    "Jungle": (0.2455, 0.664272, 0.096224),
    "Mangrove": (0.314244, 0.522575, 0.023661),
    "Savanna": (0.618196, 0.49695, 0.081344),
}

# Materials Categories

Backface_Culling_Materials = ["glass", "door", "nether portal", "redstone torch"]

SSS_Materials = ["leaves", "grass", "tulip", "oxeye daisy", "dandelion", "poppy", "blue orchid", "torchflower", "lily of the valley", "cornflower", "allium", "azure bluet", "azalea", "cactus", "wheat", "hay", "wildflowers"]

Translucent_Materials = ["leaves", "glass"]

Metal = ["iron", "gold", "emerald", "copper ; torch", "diamond", "netherite", "minecart", "lantern ; jack", "chain", "anvil", "clock", "cauldron", "spyglass", "rail"]

Reflective = ["glass", "ender", "amethyst", "water", "emerald", "quartz", "concrete", "ice"]

#

gray_blocks = {
    "vegetation" : ["grass ; snow azalea", "leaves ; cherry pale", "lily", "vine", "fern", "pink stem"],
    "redstone" : ["redstone ; torch", "dust"],
    "water" : ["water"]
}

Emissive_Materials = {
    "campfire log lit": {
        "Procedural Emission": {
            "From Min": 0.19,
            "From Max": 1.0,
            "Green": 0,
            "Blue": 0,
        },
        "Procedural Animation": {}
    },

    "fire ; campfire coral": {},
    "campfire fire": {},
    "nether portal": {
        "Procedural Emission": {
            "From Min": 0.4,
            "From Max": 1,
            "To Max": 2,
        },
        "Procedural Animation": {}
    },
    "redstone on": {
        "Procedural Emission": {
            "Green": 0,
            "Blue": 0
        }
    },
    "creaking heart active": {},
    "firefly bush": {
        "Procedural Emission": {
            "From Min": 0.1,
        },
    },
    "brewing stand": {
        "Procedural Emission": {
            "Blue": 0,
            "From Min": 0.25,
        },
        "Procedural Animation": {}
    },
    "froglight": {
        "Procedural Emission": {
            "From Min": 0,
            "From Max": 1.6,
        },
        "Procedural Animation": {}
    },
    "lantern": {
        "Procedural Emission": {
            "Green": 0,
            "Blue": 0,
            "From Max": 1,
        },
        "Procedural Animation": {},
    },
     "copper lantern": {
        "Procedural Emission": {
            "Red": 0,
            "Green": 1,
            "Blue": 0,
            "From Max": 1,
        },
        "Procedural Animation": {},
    },
    "sea lantern": {
        "Procedural Emission": {
            "From Min": 0,
            "From Max": 1,
        },
        "Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
        },
    },
    "glow lichen": {
        "Procedural Emission": {
            "From Min": 0.7,
            "From Max": 1,
        },
        "Procedural Animation": {
            "Randomize": True,
        }
    },
    "torch ; soul redstone": {
        "Procedural Emission": {
            "Green": 0,
            "Blue": 0,
            "From Min": 0.6,
            "From Max": 0.78,
        },
    },
    "copper torch": {
        "Procedural Emission": {
            "Red": 0,
            "Green": 1,
            "Blue": 0,
            "From Min": 0.6,
            "From Max": 0.78,
        },
    },
    "redstone torch": {
        "Procedural Emission": {
            "Green": 0,
            "Blue": 0,
            "From Min": 0.36,
            "From Max": 0.38,
        },
    },
    
    "powered rail on": {
        "Procedural Emission": {
            "Green": 0,
            "Blue": 0,
            "From Min": 0.52,
        },
    },
    "redstone wire on": {
        "Procedural Emission": {},
    },
    "redstone block": {
        "Procedural Emission": {},
    },
    "lava": {
        "Procedural Emission": {},
    },
    "cave vines lit": {
        "Procedural Emission": {
            "From Min": 0.2,
        },
    },
    "cave vines plant lit": {
        "Procedural Emission": {
            "From Min": 0.2,
            "To Max": 2,
            "Randomize": True,
        },
    },
    "sculk sensor": {
        "Procedural Emission": {},
        "Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
        },
    },
    "glowstone": {
        "Procedural Emission": {
            "From Max": 2,
            "To Min": 0.4,
        }, 
    },
    "shroomlight": {
        "Procedural Emission": {
            "From Min": 0,
            "From Max": 1.5,
        },
    },
    "magma": {
        "Procedural Emission": {
            "From Min": 0,
            "From Max": 0.8,
        },
        "Procedural Animation": {
            "To Min": 0.5,
            "To Max": 1.5,
            "Randomize": True,
        },
    },
    "beacon": {
        "Procedural Emission": {
            "From Min": 0,
            "From Max": 3,
        },
        "Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
        },
    },
    "sea pickle": {},
    "sculk ; catalyst": {
        "Procedural Emission": {
            "From Min": 0,
            "From Max": 0.4,
        },
        "Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
            "Speed": 0.4,
            "Randomize": True,
        },
    },
    "sculk vein": {
        "Procedural Emission": {
            "From Min": 0,
            "From Max": 0.4,
        },
        "Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
            "Randomize": True,
        },
    },
    "end rod": {
        "Procedural Emission": {
            "From Min": 1,
            "From Max": 2,
        },
    },
    "respawn anchor ; up": {
        "Procedural Emission": {
            "From Min": 0,
            "From Max": 1.5,
        },
    },
    "respawn anchor up": {
        "Procedural Emission": {
            "From Min": 0,
            "From Max": 2,
        },
          "Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
        },
    },
    "candle lit": {},
    "amethyst": {
        "Procedural Emission": {
            "From Min": 0,
            "From Max": 2,
        },
    },
    "jack o lantern north": {
        "Procedural Emission": {
            "From Min": 1.5,
            "From Max": 2,
        },
    },
    "furnace front on": {
        "Procedural Emission": {
            "From Min": 0,
            "From Max": 1.5,
            "Red": 1,
            "Green": 0,
            "Blue": 0,
        },
        "Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
        },
    },
    "furnace north on": {
        "Procedural Emission": {
            "From Min": 0,
            "From Max": 1.5,
            "Red": 1,
            "Green": 0,
            "Blue": 0,
        },
        "Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
        },
    },
    "crying obsidian": {
         "Procedural Emission": {
            "From Min": 0,
            "From Max": 0.6,
        },
        "Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
        },
    },
    "smoker front on": {
        "Procedural Emission": {
            "From Min": 0.4,
            "From Max": 1,
        },
        "Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
        },
    },
   "smoker north on": {
        "Procedural Emission": {
            "From Min": 0.4,
            "From Max": 1,
        },
        "Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
        },
    },
}
