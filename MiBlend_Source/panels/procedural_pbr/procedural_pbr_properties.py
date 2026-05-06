import bpy
from bpy.props import BoolProperty, FloatProperty, EnumProperty
from bpy.types import PropertyGroup


class MIBLEND_PG_procedural_pbr(PropertyGroup):
    use_normals: BoolProperty(
        name="Normals",
        default=True
    )

    @staticmethod
    def define_normals_selector_items():
        if bpy.app.version < (5, 1, 0):
            return [
                ('BUMP', 'Bump', ''), 
                ('PROCEDURAL_NORMALS', 'Procedural Normals', '')
            ]
        else:
            return [
                ('BUMP', 'Bump', ''), 
                ('PROCEDURAL_NORMALS', 'Procedural Normals', ''),
                ('PROCEDURAL_NORMALS_V2', 'Procedural Normals V2', '')
            ]

    normals_selector: EnumProperty(
        items=define_normals_selector_items(),
        name="normals_selector",
        default='BUMP'
    )

    toggle_normals_settings: BoolProperty(
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

    procedural_normals_v2_size: FloatProperty(
        name="Procedural Normals V2 Size",
        default=1.0,
        min=0.0,
        max=20.0
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

    revert_normals: BoolProperty(
        name="Revert",
        default=True
    )

    use_procedural_emission: BoolProperty(
        name="Emission",
        default=True
    )

    toggle_procedural_emission_settings: BoolProperty(
        default=False
    )

    camera_emission_strength: FloatProperty(
        name="Camera Emission Strength",
        default=1.0
    )

    non_camera_emission_strength: FloatProperty(
        name="Non-Camera Emission Strength",
        default=1.0
    )

    randomize_emission_strength: BoolProperty(
        name="Randomize Emission Strength",
        description="Randomizes Emission Strength for Every Face",
        default=True
    )

    use_procedural_emission_custom_config: BoolProperty(
        name="Custom Config",
        description="Uses Custom Values for Specified Blocks and Items",
        default=True
    )

    revert_procedural_emission: BoolProperty(
        name="Revert",
        default=True
    )

    use_procedural_specular_and_roughness: BoolProperty(
        name="Specular & Roughness",
        default=True
    )

    toggle_procedural_specular_and_roughness_settings: BoolProperty(
        default=False
    )

    procedural_specular_interpolation: EnumProperty(
        items=[('LINEAR', 'Linear', ''), 
            ('SMOOTHSTEP', 'Smooth Step', ''),
            ('SMOOTHERSTEP', 'Smoother Step', '')],
        name="Interpolation",
        default='LINEAR'
    )

    procedural_specular_difference: FloatProperty(
        name="Difference",
        description="Value 1 will be Ignored",
        default=0.0,
        min=0.0,
        max=1.0
    )

    procedural_roughness_interpolation: EnumProperty(
        items=[('LINEAR', 'Linear', ''), 
            ('SMOOTHSTEP', 'Smooth Step', ''),
            ('SMOOTHERSTEP', 'Smoother Step', '')],
        name="Interpolation",
        default='LINEAR'
    )

    procedural_roughness_difference: FloatProperty(
        name="Difference",
        description="Value 1 will be Ignored",
        default=0.6,
        min=0.0,
        max=1.0
    )

    revert_procedural_specular_and_roughness: BoolProperty(
        name="Revert",
        default=True
    )

    use_pbsdf_tweaks: BoolProperty(
        name="Principled BSDF Tweaks",
        default=True
    )

    toggle_pbsdf_tweaks_settings: BoolProperty(
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
        name="Subsurface Scattering",
        default=True
    )

    toggle_sss_settings: BoolProperty(
        default=False
    )

    sss_type: EnumProperty(
        items=[('BURLEY', 'Christensen Burley', ''), 
                ('RANDOM_WALK', 'Random Walk', ''),
                ('RANDOM_WALK_SKIN', 'Random Walk (Skin)', '')],
        name="Type",
        default='BURLEY'
    )

    use_sss_connect_texture_to_radius: BoolProperty(
        name="Connect Texture To The Radius",
        default=False
    )

    sss_weight: FloatProperty(
        name="Weight",
        default=1,
        min=0.0,
        max=1.0
    )

    sss_scale: FloatProperty(
        name="Scale",
        default=0.05,
        min=0.0,
        max=10.0,
        subtype='DISTANCE'
    )

    revert_sss: BoolProperty(
        name="Revert",
        default=True
    )

    use_metallic: BoolProperty(
        name="Metallic",
        description="Changes Metallic for Metallic Blocks and Items (iron, gold, diamond etc.)",
        default=True
    )

    toggle_metallic_settings: BoolProperty(
        default=False
    )

    metallic: FloatProperty(
        name="Metallic",
        default=0.7,
        min=0.0,
        max=1.0
    )

    metallic_roughness: FloatProperty(
        name="Roughness",
        default=0.2,
        min=0.0,
        max=1.0
    )

    use_reflectiveness: BoolProperty(
        name="Reflections",
        description="Changes Roughness for Reflective Blocks and Items (glass, quartz, emerald, awter etc.)",
        default=True
    )

    toggle_reflectiveness_settings: BoolProperty(
        default=False
    )

    reflections_roughness: FloatProperty(
        name="Roughness",
        default=0.1,
        min=0.0,
        max=1.0
    )

    use_translucency: BoolProperty(
        name="Translucency",
        description="Changes Translucency for Some Blocks (leaves and glass)",
        default=True
    )

    toggle_translucency_settings: BoolProperty(
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