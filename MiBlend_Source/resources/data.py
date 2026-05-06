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
        "From Min": 0.19,
        "From Max": 1.0,
        "Green": 0,
        "Blue": 0,
    },
    "fire ; campfire coral": {},
    "campfire fire": {},
    "nether portal": {
        "From Min": 0.4,
        "From Max": 1,
        "To Max": 2,
    },
    "redstone on": {
        "Green": 0,
        "Blue": 0
    },
    "creaking heart active": {},
    "firefly bush": {
        "From Min": 0.1,
    },
    "brewing stand": {
        "Blue": 0,
        "From Min": 0.25,
    },
    "froglight": {
        "From Min": 0,
        "From Max": 1.6,
    },
    "lantern": {
        "Green": 0,
        "Blue": 0,
        "From Max": 1,
    },
    "copper lantern": {
        "Red": 0,
        "Green": 1,
        "Blue": 0,
        "From Max": 1,
    },
    "sea lantern": {
        "From Min": 0,
        "From Max": 1,
    },
    "glow lichen": {
        "From Min": 0.7,
        "From Max": 1,
    },
    "torch ; soul redstone": {
        "Green": 0,
        "Blue": 0,
        "From Min": 0.6,
        "From Max": 0.78,
    },
    "copper torch": {
        "Red": 0,
        "Green": 1,
        "Blue": 0,
        "From Min": 0.6,
        "From Max": 0.78,
    },
    "redstone torch": {
        "Green": 0,
        "Blue": 0,
        "From Min": 0.36,
        "From Max": 0.38,
    },
    "powered rail on": {
        "Green": 0,
        "Blue": 0,
        "From Min": 0.52,
    },
    "redstone wire on": {},
    "redstone block": {},
    "lava": {},
    "cave vines lit": {
        "From Min": 0.2,
    },
    "cave vines plant lit": {
        "From Min": 0.2,
        "To Max": 2,
        "Randomize": True,
    },
    "sculk sensor": {},
    "glowstone": {
        "From Max": 2,
        "To Min": 0.4,
    },
    "shroomlight": {
        "From Min": 0,
        "From Max": 1.5,
    },
    "magma": {
        "From Min": 0,
        "From Max": 0.8,
    },
    "beacon": {
        "From Min": 0,
        "From Max": 3,
    },
    "sea pickle": {},
    "sculk ; catalyst": {
        "From Min": 0,
        "From Max": 0.4,
    },
    "sculk vein": {
        "From Min": 0,
        "From Max": 0.4,
    },
    "end rod": {
        "From Min": 1,
        "From Max": 2,
    },
    "respawn anchor ; up": {
        "From Min": 0,
        "From Max": 1.5,
    },
    "respawn anchor up": {
        "From Min": 0,
        "From Max": 2,
    },
    "candle lit": {},
    "amethyst": {
        "From Min": 0,
        "From Max": 2,
    },
    "jack o lantern north": {
        "From Min": 1.5,
        "From Max": 2,
    },
    "furnace front on": {
        "From Min": 0,
        "From Max": 1.5,
        "Red": 1,
        "Green": 0,
        "Blue": 0,
    },
    "furnace north on": {
        "From Min": 0,
        "From Max": 1.5,
        "Red": 1,
        "Green": 0,
        "Blue": 0,
    },
    "crying obsidian": {
        "From Min": 0,
        "From Max": 0.6,
    },
    "smoker front on": {
        "From Min": 0.4,
        "From Max": 1,
    },
    "smoker north on": {
        "From Min": 0.4,
        "From Max": 1,
    },
}
