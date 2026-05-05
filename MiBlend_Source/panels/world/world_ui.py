from bpy.types import Panel
from ...mib_utils import get_preferences


class MIBLEND_PT_world(Panel):
    bl_label = "World"
    bl_idname = "miblend.world_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MiBlend'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        world_properties = scene.miblend_properties.world_properties
        preferences = get_preferences()

        if preferences.transparent_ui:
            self.bl_options = {'HIDE_HEADER'}
        else:
            self.bl_options = set()

        box = layout.box()
        row = box.row()
        row.label(text="World", icon="WORLD_DATA")

        row = box.row()
        row.prop(world_properties, "use_animated_uv_fix")

        row = box.row()
        row.prop(world_properties, "use_lazy_biome_fix")

        row = box.row()
        row.prop(world_properties, "use_backface_culling")

        row = box.row()
        row.scale_y = 1.4
        row.operator("miblend.fix_world", text="Fix World")