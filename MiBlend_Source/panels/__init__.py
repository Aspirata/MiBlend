from bpy.types import PropertyGroup
from bpy.props import PointerProperty
from .absolute_solver import classes as absolute_solver_classes, MIBLEND_PG_absolute_solver
from .world import classes as world_classes, MIBLEND_PG_world
from .resource_packs import classes as resource_pack_classes, MIBLEND_PG_resource_packs
from .environment import classes as environment_classes, MIBLEND_PG_environment
from .materials import classes as material_classes
from .procedural_pbr import classes as procedural_pbr_classes, MIBLEND_PG_procedural_pbr
from .assets import classes as asset_classes, MIBLEND_PG_assets
from .debug import classes as debug_classes


class MIBLEND_PG_properties(PropertyGroup):
    absolute_solver_properties: PointerProperty(type=MIBLEND_PG_absolute_solver)
    world_properties: PointerProperty(type=MIBLEND_PG_world)
    resource_properties: PointerProperty(type=MIBLEND_PG_resource_packs)
    environment_properties: PointerProperty(type=MIBLEND_PG_environment)
    procedural_pbr_properties: PointerProperty(type=MIBLEND_PG_procedural_pbr)
    assets_properties: PointerProperty(type=MIBLEND_PG_assets)


classes = [
    *world_classes,
    *resource_pack_classes,
    *environment_classes,
    *material_classes,
    *procedural_pbr_classes,
    *asset_classes,
    *absolute_solver_classes,
    *debug_classes,
    MIBLEND_PG_properties
]
