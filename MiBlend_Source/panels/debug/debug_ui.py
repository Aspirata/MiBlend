from bpy.types import Panel
from ...mib_utils import get_preferences


class MIBLEND_PT_debug(Panel):
    bl_label = "Debug"
    bl_idname = "miblend.debug_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MiBlend'
    
    @classmethod
    def poll(cls, context):
        try:
            preferences = get_preferences()
            return preferences.dev_tools and preferences.debug_panel
        except (AttributeError, KeyError):
            return False

    def draw(self, context):
        layout = self.layout
        preferences = get_preferences()
        
        if preferences.transparent_ui:
            self.bl_options = {'HIDE_HEADER'}
        else:
            self.bl_options = {'DEFAULT_CLOSED'}

        box = layout.box()
        row = box.row()
        row.label(text="Debug", icon="MODIFIER_DATA")

        row = box.row()
        row.operator("miblend.debug_trigger_absolute_solver_error")

        row = box.row()
        row.operator("miblend.debug_clear_ignored_codes")

        row = box.row()
        row.operator("miblend.debug_open_miblend_folder")