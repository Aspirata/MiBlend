import bpy
import os
import json
import zipfile
import traceback
import time
from bpy.props import (IntProperty, BoolProperty, FloatProperty, EnumProperty, StringProperty, PointerProperty)
from bpy.types import PropertyGroup

main_directory = os.path.dirname(os.path.realpath(__file__))
resource_packs_directory = os.path.join(main_directory, "Resource Packs")
nodes_file = os.path.join(main_directory, "Materials", "Nodes.blend")
materials_folder = os.path.join(main_directory, "Materials")
optimization_folder = os.path.join(main_directory, "Optimization")
assets_directory = os.path.join(main_directory, "Assets")

clouds_node_tree_name = "Clouds Generator 2"
world_material_name = "Mcblend World"
BATGroup = "Better Animate Texture"

Big_Button_Scale = 1.4

Absolute_Solver_Errors = {

    "LoL": {
        "Error Name": "Zero Settings",
        "Description": "You disabled all {Data} settings, so it did nothing LoL",
        "Mode": "Full"
    },

    "000": {
        "Error Name": "Absolute Solver Error",
        "Description": "Absolute Solver Can't Display This Error - {Data}, Please Report To Aspirata",
    },

    "001": {
        "Error Name": "Unknown",
        "Description": "An Unknown Error",
    },

    "m002": {
        "Error Name": "Empty Material Slot",
        "Description": "Material doesn't exist on slot {Data}",
        "Mode": "Full"
    },

    "m003": {
        "Error Name": "Object Has No Materials",
        "Description": 'Object "{Data.name}" has no materials',
        "Mode": "Full"
    },

    "004": {
        "Error Name": ".blend File Not Found",
        "Description": "{Data}.blend not found",
    },

    "005": {
        "Error Name": "Internal Function Error",
        "Description": "Something is wrong in {Data}",
    },

    "u006": {
        "Error Name": "Color Space Not Found",
        "Description": "You have custom color manager that doesn't have {Data}",
    },
}

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
        "eevee.taa_samples": 32,
        "eevee.taa_render_samples": 32,
        "eevee.use_shadow_jitter_viewport": True,
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
    },

    "powered_rail_on": {
        "Middle Value": 0.2,
        11: 0.5,
        12: 2,
        "Adder": 0.1,
        "Divider": 50.0,
    }

}

# Materials Categories

Backface_Culling_Materials = ["glass", "door", "nether_portal"]

Alpha_Blend_Materials = ["water"]

SSS_Materials = ["leaves", "grass", "tulip", "oxeye_daisy", "dandelion", "poppy", "blue_orchid", "torchflower", "lily_of_the_valley", "cornflower", "allium", "azure bluet"]

Translucent_Materials = ["leaves", "glass"]

Metal = ["iron", "gold", "copper", "diamond", "netherite", "minecart", "lantern", "chain", "anvil", "clock", "cauldron", "spyglass", "rail"]

Reflective = ["glass", "ender", "amethyst", "water", "emerald", "quartz", "concrete"]

#

Upgrade_Materials_Array = {
    
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
        },

        "Enable Jittered Shadows": {
            "Blender_version": ">= 4.2.0",
            "File_name": "Jittered Shadows.py",
        },

        "Enable Contact Shadows": {
            "Blender_version": "< 4.2.0",
            "File_name": "Contact Shadows.py",
        }
    },
}
