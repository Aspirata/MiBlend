import bpy
from ..MIB_API import * 
from ..Resource_Packs import update_default_pack
from bpy.types import Operator
from bpy.props import (IntProperty, BoolProperty, FloatProperty, EnumProperty, StringProperty, PointerProperty)

class Recreate_Lists_Solution(Operator):
    bl_idname = "as_solutions.recreate_lists"
    bl_label = "Recreate Lists"
    bl_options = {'REGISTER', 'UNDO'}

    description: StringProperty(
        name="Description",
        default=""
    )

    def execute(self, context):
        if bpy.context.scene.get("resource_packs"):
            bpy.context.scene["resource_packs"] = {}
            update_default_pack()
        return {'FINISHED'}