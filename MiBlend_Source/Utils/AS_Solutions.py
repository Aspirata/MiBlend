import bpy, shutil
from pathlib import Path
from ..Resource_Packs import update_default_pack
from ..Assets import update_assets
from bpy.types import Operator

class FixCompatibility(Operator):
    bl_idname = "as_solutions.fix_compatibility"
    bl_label = "Fix Compatibility"

    def execute(self, context):
        if "resource_packs" in bpy.context.scene:
            bpy.context.scene["resource_packs"] = {}
            update_default_pack()
        
        update_assets()
        self.report({'INFO'}, "Resource Packs and Assets Lists were recreated")
        return {'FINISHED'}

class SaveBlendFile(Operator):
    bl_idname = "as_solutions.save_blend_file"
    bl_label = "Save Blend File"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.data.filepath == "":
            bpy.ops.wm.save_homefile()
            self.report({'INFO'}, "Default file was overwritten")
        else:
            bpy.ops.wm.save_mainfile()
            self.report({'INFO'}, "Current file was saved")
        return {'FINISHED'}

class DeleteMiblendAddon(Operator):
    bl_idname = "as_solutions.delete_miblend_addon"
    bl_label = "Delete MiBlend Legacy Addon"

    def execute(self, context):
        miblend_addon_folder = Path(__file__).resolve().parent.parent.parent.parent.parent / "scripts" / "addons" / "MiBlend_Source"

        if not miblend_addon_folder.is_dir():
            self.report({'WARNING'}, "MiBlend Legacy Addon Folder not Found")
            return {'CANCELLED'}

        shutil.rmtree(miblend_addon_folder)
        self.report({'INFO'}, "MiBlend Legacy Addon Folder was Removed")
        return {'FINISHED'}