from bpy.types import PropertyGroup
from bpy.props import BoolProperty


class MIBLEND_PG_world(PropertyGroup):
    use_lazy_biome_fix: BoolProperty(
        name="Lazy Biome Color Fix",
        description="Fixes Vegetation Biome Color",
        default=True
    )
    
    use_animated_uv_fix: BoolProperty(
        name="Animated UV Fix",
        description="Fixes UVs for Animated Blocks",
        default=True
    )

    use_backface_culling: BoolProperty(
        name="Backface Culling",
        description="Enables backface culling for blocks that need it (glass, doors, etc.)",
        default=True
    )
