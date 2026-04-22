import bpy, os, json
from .Data import assets_directory
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty, FloatProperty, StringProperty, EnumProperty, PointerProperty, CollectionProperty


class WorldProperties(PropertyGroup):
    lazy_biome_fix: BoolProperty(
        name="Lazy Biome Color Fix",
        description="Fixes Vegitation Biome Color",
        default=True
    )
    
    animated_uv_fix: BoolProperty(
        name="Animated UV Fix",
        description="Fixes UV for Animated Blocks",
        default=True
    )

    backface_culling: BoolProperty(
        name="Backface Culling",
        description="Enables Backface Culling for blocks that needs that (glass, doors etc.)",
        default=True
    )


class ResourcePackProperties(PropertyGroup):
    resource_packs_settings: BoolProperty(
        name="Advanced Settings",
        default=False
    )

    combine_duplicates: BoolProperty(
        name="Combine Duplicates",
        description="Merges Texture Duplicates (.001, .002 etc.)",
        default=True
    )

    use_additional_textures: BoolProperty(
        name="Use PBR Textures",            # 16.09.2024 This was renamed, but i'm too lazy to change the name in the code LoL | 24.03.2025 Change this in Resource Packs Rewrite Update
        default=True
    )

    textures_settings: BoolProperty(
        default=False
    )

    use_i: BoolProperty(
        name="Use Image Textures",
        default=True
    )

    use_n: BoolProperty(
        name="Use Normal Textures",
        default=True
    )

    use_s: BoolProperty(
        name="Use Specular Textures",
        default=True
    )

    s_settings: BoolProperty(
        default=False
    )

    roughness: BoolProperty(
        name="Use Roughness",
        default=True
    )

    metallic: BoolProperty(
        name="Use Metallic",
        default=True
    )

    sss: BoolProperty(
        name="Use SSS",
        default=True
    )

    specular: BoolProperty(
        name="Use Specular",
        default=True
    )

    emission: BoolProperty(
        name="Use Emssion",
        default=True
    )

    use_e: BoolProperty(
        name="Use Emission Textures",
        default=True
    )

    e_settings: BoolProperty(
        default=False
    )

    use_color: BoolProperty(
        name="Use Color",
        default=True
    )

    use_strength: BoolProperty(
        name="Use Strength",
        default=True
    )

    animate_textures: BoolProperty(
        name="Animate Textures",
        default=True
    )

    animate_textures_settings: BoolProperty(
        name="Animate Textures Settings",
        default=False
    )

    interpolate: BoolProperty(
        name="Interpolate",
        description="Adds Smooth Blend Between Animation Frames",
        default=True
    )

    randomize_speed: BoolProperty(
        name="Randomize Speed",
        description="Randomizes Animations Speed for Every Face",
        default=False
    )


class PPBRProperties(PropertyGroup):
    use_normals: BoolProperty(
        name="Use Normals",
        default=True
    )

    normals_selector: EnumProperty(
        items=[('Bump', 'Bump', ''), 
            ('Procedural Normals', 'Procedural Normals', '')],
        name="normals_selector",
        default='Bump'
    )

    normals_settings: BoolProperty(
        default=False
    )

    bump_strength: FloatProperty(
        name="Bump Strength",
        default=0.4,
        min=0.0,
        max=1.0
    )

    pnormals_size: FloatProperty(
        name="PNormals Size",
        default=4.0,
        min=0.0,
        max=16.0
    )

    pnormals_blur: FloatProperty(
        name="PNormals Blur",
        default=0,
        min=0.0,
        max=4.0
    )

    pnormals_strength: FloatProperty(
        name="PNormals Strength",
        default=1,
        min=-2.0,
        max=2.0
    )

    pnormals_exclude: FloatProperty(
        name="PNormals Exclude",
        default=0,
        min=0.0,
        max=1.0
    )

    pnormals_min: FloatProperty(
        name="PNormals Min",
        default=0,
        min=0.0,
        max=1.0
    )

    pnormals_max: FloatProperty(
        name="PNormals Max",
        default=1,
        min=0.0,
        max=1.0
    )

    pnormals_size_x_multiplier: FloatProperty(
        name="PNormals Size X Multiplier",
        default=1,
        min=-2.0,
        max=2.0
    )

    pnormals_size_y_multiplier: FloatProperty(
        name="PNormals Size Y Multiplier",
        default=1,
        min=-2.0,
        max=2.0
    )

    revert_normals: BoolProperty(
        name="Revert",
        default=True
    )

    procedural_emission_and_animation: BoolProperty(
        name="Procedural Emission & Animation",
        default=True
    )

    procedural_emission_and_animation_settings: BoolProperty(
        default=False
    )

    camera_strength: FloatProperty(
        name="Camera Emission Strength",
        default=1.0
    )

    non_camera_strength: FloatProperty(
        name="Non-Camera Emission Strength",
        default=1.0
    )

    procedural_animation: BoolProperty(
        name="Procedural Animation",
        default=False
    )

    randomize: BoolProperty(
        name="Randomize Animation Speed",
        description="Randomizes Animation Speed for Every Face",
        default=True
    )

    custom_peaa_config: BoolProperty(
        name="Custom Config",
        description="Uses Custom Values for Specified Blocks and Items",
        default=True
    )

    procedural_emission_and_animation_revert: BoolProperty(
        name="Revert",
        default=True
    )

    pspecular: BoolProperty(
        name="Procedural Specular",
        default=True
    )

    pspecular_settings: BoolProperty(
        default=False
    )

    ps_interpolation: EnumProperty(
        items=[('LINEAR', 'Linear', ''), 
            ('SMOOTHSTEP', 'Smooth Step', ''),
            ('SMOOTHERSTEP', 'Smoother Step', '')],
        name="Interpolation",
        default='LINEAR'
    )

    ps_dif: FloatProperty(
        name="Difference",
        description="Value 1 will be Ignored",
        default=0.0,
        min=0.0,
        max=1.0
    )

    ps_revert: BoolProperty(
        name="Revert",
        default=True
    )

    proughness: BoolProperty(
        name="Procedural Roughness",
        default=True
    )

    proughness_settings: BoolProperty(
        default=False
    )

    pr_interpolation: EnumProperty(
        items=[('LINEAR', 'Linear', ''), 
            ('SMOOTHSTEP', 'Smooth Step', ''),
            ('SMOOTHERSTEP', 'Smoother Step', '')],
        name="Interpolation",
        default='LINEAR'
    )

    pr_dif: FloatProperty(
        name="Difference",
        description="Value 1 will be Ignored",
        default=0.6,
        min=0.0,
        max=1.0
    )

    pr_revert: BoolProperty(
        name="Revert",
        default=True
    )

    advanced_settings: BoolProperty(
        name="Advanced Settings",
        default=False
    )

    change_bsdf: BoolProperty(
        name="Change PBSDF Settings",
        default=True
    )

    change_bsdf_settings: BoolProperty(
        default=False
    )

    specular: FloatProperty(
        name="Specular",
        default=0.4,
        min=0.0,
        max=1.0
    )

    roughness: FloatProperty(
        name="Roughness",
        default=0.6,
        min=0.0,
        max=1.0
    )

    use_sss: BoolProperty(
        name="Use SSS",
        default=True
    )

    revert_sss: BoolProperty(
        name="Revert",
        default=True
    )

    sss_skip: BoolProperty(
        name="Apply To All Materials",
        default=False
    )

    sss_settings: BoolProperty(
        default=False
    )

    sss_type: EnumProperty(
        items=[('BURLEY', 'Christensen Burley', ''), 
                ('RANDOM_WALK', 'Random Walk', ''),
                ('RANDOM_WALK_SKIN', 'Random Walk (Skin)', '')],
        name="sss_type",
        default='BURLEY'
    )

    connect_texture: BoolProperty(
        name="Connect Texture To The Radius",
        default=False
    )

    sss_weight: FloatProperty(
        name="SSS Weight",
        default=1,
        min=0.0,
        max=1.0
    )

    sss_scale: FloatProperty(
        name="SSS Scale",
        default=0.05,
        min=0.0,
        max=10.0,
        subtype='DISTANCE'
    )

    use_translucency: BoolProperty(
        name="Use Translucency",
        description="Changes Translucency for Some Blocks (leaves and glass)",
        default=True
    )

    translucency_settings: BoolProperty(
        default=False
    )

    translucency: FloatProperty(
        name="Translucency",
        default=0.4,
        min=0.0,
        max=1.0
    )

    revert_translucency: BoolProperty(
        name="Revert",
        default=True
    )

    make_metal: BoolProperty(
        name="Make Metal",
        description="Changes Metallic for Metallic Blocks and Items (iron, gold, diamond etc.)",
        default=True
    )

    metal_settings: BoolProperty(
        default=False
    )

    metal_metallic: FloatProperty(
        name="Metallic",
        default=0.7,
        min=0.0,
        max=1.0
    )

    metal_roughness: FloatProperty(
        name="Roughness",
        default=0.2,
        min=0.0,
        max=1.0
    )

    make_reflections: BoolProperty(
        name="Make Reflections",
        description="Changes Roughness for Reflective Blocks and Items (glass, quartz, emerald, awter etc.)",
        default=True
    )

    reflections_settings: BoolProperty(
        default=False
    )

    reflections_roughness: FloatProperty(
        name="Reflections Roughness",
        default=0.1,
        min=0.0,
        max=1.0
    )


class CreateEnvProperties(PropertyGroup):
    create_sky: BoolProperty(
        name="Sky",
        default=True
    )

    sky_settings: BoolProperty(
        default=False
    )

    strength_settings: BoolProperty(
        default=False
    )

    colors_settings: BoolProperty(
        default=False
    )

    ambient_colors_settings: BoolProperty(
        default=False
    )

    rotation_settings: BoolProperty(
        default=False
    )

    other_settings: BoolProperty(
        default=False
    )

    create_clouds: BoolProperty(
        name="Clouds",
        default=True
    )

    clouds_settings: BoolProperty(
        default=False
    )

    geonodes_settings: BoolProperty(
        default=True
    )

    material_settings: BoolProperty(
        default=False
    )

    layers_settings: BoolProperty(
        default=False
    )

    create_fog: BoolProperty(
        name="Fog",
        default=True
    )

    fog_settings: BoolProperty(
        default=False
    )


class AssetTagItem(PropertyGroup):
    name: StringProperty()
    enabled: BoolProperty(default=False)


class AssetsProperties(PropertyGroup):
    asset_items: CollectionProperty(type=PropertyGroup)

    asset_index: IntProperty(default=0)

    filters: BoolProperty(
        name="Filters",
        default=False
    )

    def get_tags(self):
        unique_tags = set()

        for root, dirs, files in os.walk(assets_directory):
            for file in files:
                if file.endswith(".json"):
                    json_path = os.path.join(root, file)
                    with open(json_path, 'r') as f:
                        asset_data = json.load(f)
                        tags = asset_data.get("Tags", [])
                        unique_tags.update(tags)

        unique_tags = sorted(unique_tags)
        return [('All', "All", "")] + [(tag, tag, "") for tag in unique_tags]

    tags: CollectionProperty(type=AssetTagItem)
    
    properties_toggle: BoolProperty(
        name="Properties Toggle",
        default=True
    )
    
    tags_mode: EnumProperty(
        items=[("and", "And", ""), ("or", "Or", "")],
        name="tags_mode",
        default='or',
    )

    filter_by_version: BoolProperty(
        name="Filter By Blender Version",
        default=True
    )

class AbsoluteSolverProperties(PropertyGroup):
    ignored_codes: StringProperty()


class MiBlendProperties(PropertyGroup):
    world_properties: PointerProperty(type=WorldProperties)
    resource_properties: PointerProperty(type=ResourcePackProperties)
    env_properties: PointerProperty(type=CreateEnvProperties)
    ppbr_properties: PointerProperty(type=PPBRProperties)
    assets_properties: PointerProperty(type=AssetsProperties)
    absolute_solver_properties: PointerProperty(type=AbsoluteSolverProperties)