from bpy.types import PropertyGroup
from bpy.props import BoolProperty


class MIBLEND_PG_environment(PropertyGroup):
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

    other_settings: BoolProperty(
        default=False
    )

    create_clouds: BoolProperty(
        name="Clouds",
        default=True
    )

    cloud_settings: BoolProperty(
        default=False
    )

    material_settings: BoolProperty(
        default=False
    )

    create_fog: BoolProperty(
        name="Fog",
        default=True
    )

    fog_settings: BoolProperty(
        default=False
    )

    migrate_old_environment: BoolProperty(
        name="Migrate Old Environment",
        default=True
    )