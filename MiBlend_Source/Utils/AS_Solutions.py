import bpy
from ..MIB_API import * 
from ..Resource_Packs import update_default_pack
from bpy.types import Operator
from bpy.props import StringProperty

class FixCompatibility(Operator):
    bl_idname = "as_solutions.fix_compatibility"
    bl_label = "Fix Compatibility"
    bl_options = {'REGISTER', 'UNDO'}

    description: StringProperty(
        name="Description",
        default=""
    )

    def execute(self, context):
        if "resource_packs" in bpy.context.scene:
            bpy.context.scene["resource_packs"] = {}
            update_default_pack()
        return {'FINISHED'}