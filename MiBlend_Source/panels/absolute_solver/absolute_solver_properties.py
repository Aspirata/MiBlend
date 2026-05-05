from bpy.types import PropertyGroup
from bpy.props import StringProperty


class MIBLEND_PG_absolute_solver(PropertyGroup):
    ignored_codes: StringProperty()
