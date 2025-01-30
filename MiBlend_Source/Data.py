import bpy
import os
import json
import zipfile
import traceback
from bpy.props import (IntProperty, BoolProperty, FloatProperty, EnumProperty, StringProperty, PointerProperty)

main_directory = os.path.dirname(os.path.realpath(__file__))
materials_folder = os.path.join(main_directory, "Materials")
nodes_file = os.path.join(materials_folder, "Nodes.blend")
optimization_folder = os.path.join(main_directory, "Optimization")
assets_directory = os.path.join(main_directory, "Assets")
utils_directory = os.path.join(main_directory, "Utils")

clouds_node_tree_name = "Clouds Generator 2"
fog_node_tree_name = "Fog"
world_material_name = "MiBlend World"

Big_Button_Scale = 1.4

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

    "Aspirata Eevee Next Viewport":{
        "eevee.taa_samples": 16,
        "eevee.taa_render_samples": 16,
        "eevee.shadow_ray_count": 1,
        "eevee.shadow_step_count": 16,
        "eevee.use_volumetric_shadows": True,
        "eevee.use_raytracing": True,
        "eevee.ray_tracing_options.resolution_scale": '4',
        "eevee.ray_tracing_options.trace_max_roughness": 0,
        "eevee.fast_gi_resolution": '4',
        "eevee.fast_gi_ray_count": 1,
        "eevee.fast_gi_step_count": 16,
    },

    "Aspirata Eevee Next Render":{
        "eevee.taa_samples": 32,
        "eevee.taa_render_samples": 32,
        "eevee.shadow_ray_count": 2,
        "eevee.shadow_step_count": 16,
        "eevee.use_volumetric_shadows": True,
        "eevee.use_raytracing": True,
        "eevee.ray_tracing_options.resolution_scale": '4',
        "eevee.ray_tracing_options.trace_max_roughness": 0,
        "eevee.fast_gi_resolution": '4',
        "eevee.fast_gi_ray_count": 2,
        "eevee.fast_gi_step_count": 16,
        "eevee.use_overscan": True,
        "eevee.overscan_size": 10.0,
    }
}

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

SSS_Materials = ["leaves", "grass", "tulip", "oxeye daisy", "dandelion", "poppy", "blue orchid", "torchflower", "lily of the valley", "cornflower", "allium", "azure bluet", "azalea", "cactus", "wheat", "hay"]

Translucent_Materials = ["leaves", "glass"]

Metal = ["iron", "gold", "emerald", "copper", "diamond", "netherite", "minecart", "lantern", "chain", "anvil", "clock", "cauldron", "spyglass", "rail"]

Reflective = ["glass", "ender", "amethyst", "water", "emerald", "quartz", "concrete", "ice"]

#

gray_blocks = {
    "vegetation" : ["grass ; side snow azalea", "leaves ; cherry pale", "lily", "vine", "fern", "pink stem"],
    "redstone" : ["redstone", "dust"],
    "water" : ["water"]
}

Emissive_Materials = {
    "fire": {},
    "nether portal": {},
    "firefly":{
									"Better Emission":{
														"From Min": 0.1,
														"From Max": 0.6,
									},
					},
    "brewing":{
									"Better Emission":{
														"From Min": 0.6,
														"From Max": 1,
									},
					},
    "froglight":{
									"Better Emission":{
														"From Min": 0.3,
														"From Max": 0.6,
									},
					},
    "campfire log lit": {
        "Better Emission": {
            "From Min": 0.19,
            "From Max": 0.52,
        },
    },
    "sea lantern": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 1,
        },
        "Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
            "Period": 100,
        },
    },
    "glow lichen": {
        "Better Emission": {
            "From Min": 0.18,
            "From Max": 0.6,
        },
    },
    "torch": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 0.6,
        },
    },
    "powered rail on": {
        "Better Emission": {
            "From Min": 0.52,
            "From Max": 0.6,
        },
    },
    "redstone wire on": {
        "Better Emission": {
            "From Min": 0.52,
            "From Max": 0.6,
        },
    },
    "redstone block": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 0.6,
        },
    },
    "redstone_lamp_on": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 0.6,
        },
    },
    "lava": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 0.6,
        },
    },
    "cave vines lit": {
        "Better Emission": {
            "From Min": 0.2,
            "From Max": 0.6,
        },
    },
    "cave vines plant lit": {
        "Better Emission": {
            "From Min": 0.2,
            "From Max": 0.6,
        },
    },
    "sculk sensor": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 0.6,
        },
									"Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
            "Period": 100,
        },
    },
    "glowstone": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 2,
        },
    },
    "shroomlight": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 2,
        },
									"Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
            "Period": 100,
        },
    },
    "magma": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 0.6,
        },
										"Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
            "Period": 100,
        },
    },
    "beacon": {
									"Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
            "Period": 100,
        },
},
    "sea pickle": {},
    "sculk ; catalyst": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 0.4,
        },
									"Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
            "Period": 100,
        },
    },
    "sculk vein": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 0.6,
        },
    },
    "end rod": {
        "Better Emission": {
            "From Min": 0.5,
            "From Max": 0.6,
        },
    },
    "respawn anchor": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 0.6,
        },
    },
    "candle lit": {},
    "large amethyst bud": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 0.6,
        },
    },
    "medium amethyst bud": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 0.4,
        },
    },
    "small amethyst bud": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 0.2,
        },
    },
    "amethyst cluster": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 0.6,
        },
    },
    "jack o lantern": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 0.6,
        },
    },
    "furnace front on": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 0.6,
        },
									"Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
            "Period": 100,
        },
    },
    "crying obsidian": {
									"Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
            "Period": 100,
        },
					},
    "smoker front on": {
        "Better Emission": {
            "From Min": 0,
            "From Max": 0.6,
        },
									"Procedural Animation": {
            "To Min": 0,
            "To Max": 1.5,
            "Period": 100,
        },
    },
}