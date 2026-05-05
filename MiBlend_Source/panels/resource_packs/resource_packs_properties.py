from bpy.props import BoolProperty
from bpy.types import PropertyGroup


class MIBLEND_PG_resource_packs(PropertyGroup):
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