from bpy.props import BoolProperty, FloatProperty, EnumProperty
from bpy.types import PropertyGroup


class MIBLEND_PG_procedural_pbr(PropertyGroup):
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

    use_procedural_emission_and_animation: BoolProperty(
        name="Procedural Emission & Animation",
        default=True
    )

    toggle_procedural_emission_and_animation_settings: BoolProperty(
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

    use_procedural_animation: BoolProperty(
        name="Procedural Animation",
        default=False
    )

    randomize_animation_speed: BoolProperty(
        name="Randomize Animation Speed",
        description="Randomizes Animation Speed for Every Face",
        default=True
    )

    use_custom_peaa_config: BoolProperty(
        name="Custom Config",
        description="Uses Custom Values for Specified Blocks and Items",
        default=True
    )

    revert_procedural_emission_and_animation: BoolProperty(
        name="Revert",
        default=True
    )

    use_procedural_specular: BoolProperty(
        name="Procedural Specular",
        default=True
    )

    toggle_procedural_specular_settings: BoolProperty(
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

    revert_procedural_specular: BoolProperty(
        name="Revert",
        default=True
    )

    use_procedural_roughness: BoolProperty(
        name="Procedural Roughness",
        default=True
    )

    toggle_procedural_roughness_settings: BoolProperty(
        default=False
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

    revert_procedural_roughness: BoolProperty(
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