import bpy
from ..MIB_API import * 
from bpy.types import Operator
from bpy.props import (IntProperty, BoolProperty, FloatProperty, EnumProperty, StringProperty, PointerProperty)

class Update_Components_Solution(Operator):
    bl_idname = "as_solutions.update_components"
    bl_label = "Update Components"
    bl_options = {'REGISTER', 'UNDO'}

    description: StringProperty()

    def execute(self, context):
        try:
            del bpy.types.Scene.world_properties
            del bpy.types.Scene.resource_properties
            del bpy.types.Scene.materials_properties
            del bpy.types.Scene.env_properties
            del bpy.types.Scene.ppbr_properties
            del bpy.types.Scene.optimizationproperties
            del bpy.types.Scene.utilsproperties
            del bpy.types.Scene.assetsproperties
            del bpy.types.Scene.script_asset_properties
        except:
            return {"CANCELLED"}
        return {'FINISHED'}
