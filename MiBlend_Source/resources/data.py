import os


main_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
resources_directory = os.path.join(main_directory, "resources")
nodes_file = os.path.join(resources_directory, "Nodes.blend")
assets_directory = os.path.join(main_directory, "Assets")


GRAY_BLOCKS = {
    "vegetation" : ["grass ; snow azalea", "leaves ; cherry pale", "lily", "vine", "fern", "pink stem"],
    "redstone" : ["redstone ; torch", "dust"],
    "water" : ["water"]
}

EMISSIVE_MATERIALS = {
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
