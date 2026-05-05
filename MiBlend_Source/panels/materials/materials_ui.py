from bpy.types import Panel
from ...mib_utils import get_preferences


class MIBLEND_PT_materials(Panel):
    bl_label = "Materials"
    bl_idname = "miblend.materials_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MiBlend'

    def draw(self, context):
        layout = self.layout
        preferences = get_preferences()

        if preferences.transparent_ui:
            self.bl_options = {'HIDE_HEADER'}
        else:
            self.bl_options = set()
        
        box = layout.box()
        row = box.row()
        row.label(text="Materials", icon="MATERIAL_DATA")

        row = box.row()
        row.scale_y = 1.4
        row.operator("miblend.materials_fix_materials", text="Fix Materials")

        row = box.row()
        row.scale_y = 1.4
        row.operator("miblend.materials_swap_textures", icon="UV_SYNC_SELECT")