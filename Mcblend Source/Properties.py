from .Data import *
from .Translator import *

class FixWorldProperties(PropertyGroup):

    backface_culling: BoolProperty(
        name="Backface Culling",
        default=True,
        description=""
    )

    delete_useless_textures: BoolProperty(
        name="Delete Useless Textures",
        default=True,
        description=""
    )

    emissiondetection: EnumProperty(
        items=[('Automatic', 'Automatic', ''), 
            ('Automatic & Manual', 'Automatic & Manual', ''),
            ('Manual', 'Manual', '')],
        name="emissiondetection",
        default='Automatic & Manual'
    )






class PPBRProperties(PropertyGroup):

    use_normals: BoolProperty(
        name=Translate("Use Normals"),
        default=True,
        description="Enables Normals In Materials"
    )

    normals_selector: EnumProperty(
        items=[('Bump', 'Bump', ''), 
            ('Procedural Normals', 'Procedural Normals', '')],
        name="normals_selector",
        default='Bump'
    )

    normals_settings: BoolProperty(
        name=Translate("Normals Settings"),
        default=False,
        description=""
    )

    bump_strength: FloatProperty(
        name="Bump Strength",
        default=0.4,
        min=0.0,
        max=1.0,
        description=""
    )

    pnormals_size: FloatProperty(
        name="PNormals Size",
        default=2,
        min=0.0,
        max=16.0,
        description=""
    )

    pnormals_blur: FloatProperty(
        name="PNormals Blur",
        default=0,
        min=0.0,
        max=4.0,
        description=""
    )

    pnormals_strength: FloatProperty(
        name="PNormals Strength",
        default=1,
        min=-2.0,
        max=2.0,
        description=""
    )

    pnormals_exclude: FloatProperty(
        name="PNormals Exclude",
        default=0,
        min=0.0,
        max=1.0,
        description=""
    )

    pnormals_min: FloatProperty(
        name="PNormals Min",
        default=0,
        min=0.0,
        max=1.0,
        description=""
    )

    pnormals_max: FloatProperty(
        name="PNormals Max",
        default=1,
        min=0.0,
        max=1.0,
        description=""
    )

    pnormals_size_x_multiplier: FloatProperty(
        name="PNormals Size X Multiplier",
        default=1,
        min=-2.0,
        max=2.0,
        description=""
    )

    pnormals_size_y_multiplier: FloatProperty(
        name="PNormals Size Y Multiplier",
        default=1,
        min=-2.0,
        max=2.0,
        description=""
    )

    use_sss: BoolProperty(
        name=Translate("Use SSS"),
        default=True,
        description=""
    )

    sss_settings: BoolProperty(
        name=Translate("SSS Settings"),
        default=False,
        description=""
    )

    def sss_type_fix():
        if blender_version >= (4,0,0):
            items=[('BURLEY', 'Christensen Burley', ''), 
                ('RANDOM_WALK', 'Random Walk', ''),
                ('RANDOM_WALK_SKIN', 'Random Walk (Skin)', '')]
        else:
            items=[('BURLEY', 'Christensen Burley', ''), 
                ('RANDOM_WALK', 'Random Walk', ''),
                ('RANDOM_WALK_FIXED_RADIUS', 'Random Walk (Fixed Radius)', '')]
        return items

    sss_type: EnumProperty(
        items=sss_type_fix(),
        name="sss_type",
        default='BURLEY'
    )

    connect_texture: BoolProperty(
        name="Connect Texture To The Radius",
        default=(blender_version < (4, 0, 0)),
        description=""
    )

    sss_weight: FloatProperty(
        name="SSS Weight",
        default=1,
        min=0.0,
        max=1.0,
        description=""
    )

    sss_scale: FloatProperty(
        name="SSS Scale",
        default=0.05,
        min=0.0,
        max=10.0,
        subtype='DISTANCE',
        description=""
    )

    make_metal: BoolProperty(
        name="Make Metal",
        default=True,
        description="Enambles PBR For Metallic Materials"
    )

    metal_settings: BoolProperty(
        name="Metal Settings",
        default=False,
        description=""
    )

    metal_metallic: FloatProperty(
        name="Metallic",
        default=0.7,
        min=0.0,
        max=1.0,
        description=""
    )

    metal_roughness: FloatProperty(
        name="Roughness",
        default=0.2,
        min=0.0,
        max=1.0,
        description=""
    )

    make_reflections: BoolProperty(
        name="Make Reflections",
        default=True,
        description="Enambles PBR For Reflective Materials"
    )

    reflections_settings: BoolProperty(
        name="Reflections Settings",
        default=False,
        description=""
    )

    reflections_roughness: FloatProperty(
        name="Reflections Roughness",
        default=0.1,
        min=0.0,
        max=1.0,
        description=""
    )

    make_better_emission: BoolProperty(
        name="Make Better Emission",
        default=True,
        description=""
    )

    animate_textures: BoolProperty(
        name="Animate textures",
        default=True,
        description=""
    )

    advanced_settings: BoolProperty(
        name="Advanced Settings",
        default=False,
        description=""
    )

    change_bsdf: BoolProperty(
        name="Change BSDF",
        default=True,
        description=""
    )

    change_bsdf_settings: BoolProperty(
        name="Change BSDF Settings",
        default=False,
        description=""
    )

    specular: FloatProperty(
        name="Specular",
        default=0.4,
        min=0.0,
        max=1.0,
        description=""
    )

    roughness: FloatProperty(
        name="Roughness",
        default=0.6,
        min=0.0,
        max=1.0,
        description=""
    )






class CreateEnvProperties(PropertyGroup):

    advanced_settings: BoolProperty(
        name="Advanced Settings",
        default=False,
        description=""
    )

    strength_settings: BoolProperty(
        name="Strength Settings",
        default=False,
        description=""
    )

    colors_settings: BoolProperty(
        name="Colors Settings",
        default=False,
        description=""
    )

    ambient_colors_settings: BoolProperty(
        name="Ambient Colors Settings",
        default=False,
        description=""
    )

    rotation_settings: BoolProperty(
        name="Rotation Settings",
        default=False,
        description=""
    )

    create_clouds: BoolProperty(
        name="Create Clouds",
        default=True,
        description=""
    )

    create_sky: BoolProperty(
        name="Create Sky",
        default=True,
        description=""
    )






class OptimizationProperties(PropertyGroup):

    use_camera_culling: BoolProperty(
        name="Use Camera Culling",
        default=True,
        description="Enables Camera Culling"
    )

    camera_culling_settings: BoolProperty(
        name="Camera Culling Settings",
        default=False,
        description=""
    )

    camera_culling_type: EnumProperty(
        items=[('Vector', 'Vector', ''), ('Raycast', 'Raycast', '')],
        name="camera_culling_type",
        default='Raycast'
    )

    culling_mode: EnumProperty(
        items=[('Simplify Faces', 'Simplify Faces', ''), ('Delete Faces', 'Delete Faces', '')],
        name="culling_mode",
        default='Delete Faces'
    )

    culling_distance: FloatProperty(
        name="Anti-Culling Distance",
        default=10.0,
        min=0.0,
        max=1000000.0,
        description=""
    )

    predict_fov: BoolProperty(
        name="Predict FOV",
        default=False,
        description=""
    )

    merge_by_distance: BoolProperty(
        name="Merge By Distance",
        default=False,
        description=""
    )

    merge_distance: FloatProperty(
        name="Merge Distance",
        default=100.0,
        min=0.0,
        max=1000000.0,
        description=""
    )

    threshold: FloatProperty(
        name="Threshold",
        default=0.8,
        min=0.0,
        max=1.0,
        description=""
    )

    scale: FloatProperty(
        name="Scale",
        default=1,
        min=0.0,
        max=100.0,
        description=""
    )

    backface_culling: BoolProperty(
        name="Backface Culling",
        default=True,
        description=""
    )

    backface_culling_distance: FloatProperty(
        name="Backface Culling Distance",
        default=50.0,
        min=0.0,
        max=1000000.0,
        description=""
    )






class UtilsProperties(PropertyGroup):

    cs_settings: BoolProperty(
        name="Contact Shadows Settings",
        default=False,
        description=""
    )

    cshadowsselection: EnumProperty(
        items=[('All Light Sources', 'All Light Sources', ''), 
               ('Only Selected Light Sources', 'Only Selected Light Sources', '')],
        name="cshadowsselection",
        default='All Light Sources'
    )

    distance: FloatProperty(
        name="Distance",
        description="",
        default=0.2,
        min=0.0,
        max=100000.0
    )

    bias: FloatProperty(
        name="Bias",
        description="",
        default=0.03,
        min=0.001,
        max=5.0
    )

    thickness: FloatProperty(
        name="Thickness",
        description="",
        default=0.01,
        min=0.0,
        max=100.0
    )

    current_preset: EnumProperty(
        items=[(name, name, "") for name, data in Render_Settings.items()],
        description="Select Settings to Use",
    )

    enchant_settings: BoolProperty(
        name="Enchant Settings",
        default=False,
        description=""
    )

    divider: FloatProperty(
        name="Divider",
        description="",
        default=70.0,
        min=0.0,
        max=100000.0
    )

    camera_strenght: FloatProperty(
        name="Camera Strenght",
        description="",
        default=1.0,
        min=0.0,
        max=1000000.0
    )

    non_camera_strenght: FloatProperty(
        name="Non-Camera Strenght",
        description="",
        default=1.0,
        min=0.0,
        max=1000000.0
    )

    armature: bpy.props.PointerProperty(
        name="Armature",
        description="",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )

    lattice: bpy.props.PointerProperty(
        name="Lattice",
        description="",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'LATTICE'
    )

    vertex_group_name: StringProperty(
        name="Vertex Group Name",
        description=""
    )
