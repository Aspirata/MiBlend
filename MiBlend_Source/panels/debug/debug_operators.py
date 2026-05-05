import platform
import os
import subprocess
import bpy
from bpy.types import Operator
from ..absolute_solver.absolute_solver_logic import trigger_absolute_solver
from ...mib_utils import get_preferences
from ...resources.data import main_directory


class MIBLEND_OT_clear_ignored_codes(Operator):
    bl_idname = "miblend.debug_clear_ignored_codes"
    bl_label = "Clear Ignored Codes"
    bl_description = "Cleares the List of Ignored Errors and Warnings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.miblend_properties.absolute_solver_properties.ignored_codes = ""
        return {'FINISHED'}


class MIBLEND_OT_trigger_absolute_solver_error(Operator):
    bl_idname = "miblend.debug_trigger_absolute_solver_error"
    bl_label = "Trigger AS Error"
    bl_description = "Triggers e00"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if "e-1" in context.scene.miblend_properties.absolute_solver_properties.ignored_codes:
            self.report({'ERROR'}, "You're ignoring this error dumbass")
        elif not get_preferences().show_warnings:
            self.report({'ERROR'}, "You can't see warnings because you've disabled them dumbass")
        else:
            trigger_absolute_solver("e-1")
        return {'FINISHED'}


class MIBLEND_OT_open_miblend_folder(Operator):
    bl_idname = "miblend.debug_open_miblend_folder"
    bl_label = "Open MiBlend Folder"
    bl_description = "Opens MiBlend Folder in your File Explorer"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if platform.system() == "Windows":
            os.startfile(main_directory)
        elif platform.system() == "Darwin":
            subprocess.call(["open", main_directory])
        else:
            subprocess.call(["xdg-open", main_directory])
        return {'FINISHED'}


class MIBLEND_OT_remove_attribute(Operator):
    bl_idname = "miblend.remove_attribute"
    bl_label = "Remove Attribute"
    bl_description = "Removes a Specified Attribute from the Scene"
    bl_options = {'REGISTER', 'UNDO'}

    attribute: bpy.props.StringProperty()

    def execute(self, context):
        attr_name = self.attribute
        
        if attr_name in bpy.context.scene:
            del bpy.context.scene[attr_name]
            self.report({'INFO'}, f"Attribute '{attr_name}' has been removed.")
        else:
            try:
                parts = attr_name.split(".")
                current = bpy.context.scene

                for part in parts[:-1]:
                    current = getattr(current, part)
                
                attr = getattr(current, parts[-1])
                attr.clear()
                return {'FINISHED'}
            except AttributeError as e:
                self.report({'WARNING'}, f"Failed to remove attribute '{attr_name}': {str(e)}")
            except TypeError as e:
                self.report({'WARNING'}, f"Failed to remove attribute '{attr_name}': {str(e)}")
            self.report({'WARNING'}, f"Attribute '{attr_name}' does not exist.")
        return {'FINISHED'}