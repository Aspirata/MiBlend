import os
from bpy.types import Operator
from bpy.props import StringProperty
from . import materials_logic


class MIBLEND_OT_fix_materials(Operator):
    bl_idname = "miblend.materials_fix_materials"
    bl_label = "Fix Materials"
    bl_description = "Fixes Materials with Maximum Compatibility"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        materials_logic.fix_materials()
        return {'FINISHED'}


class MIBLEND_OT_swap_textures(Operator):
    bl_idname = "miblend.materials_swap_textures"
    bl_label = "Swap Textures"
    bl_description = "Swapes Textures with Maximum Compatibility"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        if os.path.isdir(self.filepath) or self.filepath.endswith('.zip'):
            materials_logic.swap_textures(os.path.abspath(self.filepath))
            self.report({'INFO'}, f"Selected Folder: {os.path.abspath(self.filepath)}")
        else:
            materials_logic.swap_textures(os.path.dirname(self.filepath))
            self.report({'INFO'}, f"Selected Folder: {os.path.dirname(self.filepath)}")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
