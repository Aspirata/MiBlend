import os
from bpy.types import Panel
from .resource_packs_logic import get_resource_packs, get_resource_path
from ...mib_utils import get_preferences, get_pack_info_properties


class MIBLEND_PT_resource_packs(Panel):
    bl_label = "Resource Packs"
    bl_idname = "miblend.resource_packs_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MiBlend'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        preferences = get_preferences()

        if preferences.transparent_ui:
            self.bl_options = {'HIDE_HEADER'}
        else:
            self.bl_options = set()
        
        box = layout.box()
        row = box.row()
        row.label(text="Resource Packs", icon="FILE_FOLDER")
        
        sbox = box.box()
        try:
            resource_packs: dict = get_resource_packs()
        except Exception:
            resource_packs = {}

        if not resource_packs:
            row = sbox.row()
            row.label(text="No resource packs found, reload default packs", icon="ERROR")
            if not os.path.exists(get_resource_path()) and preferences.dev_tools:
                row = sbox.row()
                row.label(text="Dev path is not set", icon="ERROR")
        else:
            tbox = sbox.box()
            for pack, pack_info in resource_packs.items():
                row = tbox.row()

                if os.path.exists(pack_info.get("path", "")):
                    icon = 'CHECKBOX_HLT' if pack_info["enabled"] else 'CHECKBOX_DEHLT'
                    toggle_op = row.operator("miblend.toggle_resource_pack", text="", icon=icon)
                    toggle_op.pack_name = pack
                else:
                    row.label(text="", icon='ERROR')

                pack_info_props = get_pack_info_properties(pack)
                mc_version = pack_info_props.get('mc_version', '')
                pack_type = pack_info.get('type', 'Texture & PBR')
                
                if mc_version is None:
                    row.label(text=f"{pack} ({pack_type})")
                else:
                    version_text = mc_version if mc_version != 'Unknown' else ''
                    row.label(text=f"{pack} {version_text} ({pack_type})")
                    
                buttons_row = row.row(align=True)

                if not pack_info.get("is_built_in", False):
                    remove = buttons_row.operator("miblend.remove_resource_pack", text="", icon='X')
                    remove.pack_name = pack
                
                if os.path.exists(pack_info.get("path", "")):
                    move_up = buttons_row.operator("miblend.move_resource_pack_up", text="", icon='TRIA_UP')
                    move_up.pack_name = pack

                    move_down = buttons_row.operator("miblend.move_resource_pack_down", text="", icon='TRIA_DOWN')
                    move_down.pack_name = pack
            
            row = sbox.row()
            row.operator("miblend.add_resource_pack", text="", icon='ADD')
            
            if preferences.dev_tools and preferences.debug_tools:
                remove_attr = row.operator("miblend.remove_attribute", text="", icon='X')
                remove_attr.attribute = "resource_packs"
                
            row.operator("miblend.update_default_pack", icon='FILE_REFRESH')
        
        row = box.row()
        row.prop(scene.miblend_properties.resource_properties, "resource_packs_settings", toggle=True, icon=("TRIA_DOWN" if scene.miblend_properties.resource_properties.resource_packs_settings else "TRIA_RIGHT"))
        if scene.miblend_properties.resource_properties.resource_packs_settings:

            sbox = box.box()
            row = sbox.row()
            row.prop(scene.miblend_properties.resource_properties, "combine_duplicates")

            row = sbox.row()
            row.prop(scene.miblend_properties.resource_properties, "use_i")

            row = sbox.row()
            row.prop(scene.miblend_properties.resource_properties, "use_additional_textures")
            row.prop(scene.miblend_properties.resource_properties, "textures_settings", toggle=True, icon=("TRIA_DOWN" if scene.miblend_properties.resource_properties.textures_settings else "TRIA_LEFT"), icon_only=True)
            if scene.miblend_properties.resource_properties.textures_settings:

                tbox = sbox.box()
                row = tbox.row()
                row.label(text="PBR Textures:", icon="SHADING_RENDERED")
                row = tbox.row()
                row.enabled = scene.miblend_properties.resource_properties.use_additional_textures
                row.prop(scene.miblend_properties.resource_properties, "use_n")

                row = tbox.row()
                row.enabled = scene.miblend_properties.resource_properties.use_additional_textures
                row.prop(scene.miblend_properties.resource_properties, "use_s")
                row.prop(scene.miblend_properties.resource_properties, "s_settings", toggle=True, icon=("TRIA_DOWN" if scene.miblend_properties.resource_properties.s_settings else "TRIA_LEFT"), icon_only=True)
                if scene.miblend_properties.resource_properties.s_settings:
                    fbox = tbox.box()
                    row = fbox.row()
                    row.enabled = scene.miblend_properties.resource_properties.use_s
                    row.prop(scene.miblend_properties.resource_properties, "roughness")

                    row = fbox.row()
                    row.enabled = scene.miblend_properties.resource_properties.use_s
                    row.prop(scene.miblend_properties.resource_properties, "metallic")

                    row = fbox.row()
                    row.enabled = scene.miblend_properties.resource_properties.use_s
                    row.prop(scene.miblend_properties.resource_properties, "sss")

                    row = fbox.row()
                    row.enabled = scene.miblend_properties.resource_properties.use_s
                    row.prop(scene.miblend_properties.resource_properties, "specular")

                    row = fbox.row()
                    row.enabled = scene.miblend_properties.resource_properties.use_s
                    row.prop(scene.miblend_properties.resource_properties, "emission")

                row = tbox.row()
                row.enabled = scene.miblend_properties.resource_properties.use_additional_textures
                row.prop(scene.miblend_properties.resource_properties, "use_e")
                row.prop(scene.miblend_properties.resource_properties, "e_settings", toggle=True, icon=("TRIA_DOWN" if scene.miblend_properties.resource_properties.e_settings else "TRIA_LEFT"), icon_only=True)
                if scene.miblend_properties.resource_properties.e_settings:
                    fbox = tbox.box()
                    row = fbox.row()
                    row.enabled = scene.miblend_properties.resource_properties.use_e
                    row.prop(scene.miblend_properties.resource_properties, "use_color")

                    row = fbox.row()
                    row.enabled = scene.miblend_properties.resource_properties.use_e
                    row.prop(scene.miblend_properties.resource_properties, "use_strength")
            
            row = sbox.row()
            row.prop(scene.miblend_properties.resource_properties, "animate_textures")
            row.prop(scene.miblend_properties.resource_properties, "animate_textures_settings", toggle=True, icon=("TRIA_DOWN" if scene.miblend_properties.resource_properties.animate_textures_settings else "TRIA_LEFT"), icon_only=True)
            if scene.miblend_properties.resource_properties.animate_textures_settings:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Animation Settings:", icon="SEQUENCE")
                row = tbox.row()
                row.prop(scene.miblend_properties.resource_properties, "interpolate")
                row.enabled = scene.miblend_properties.resource_properties.animate_textures
                row = tbox.row()
                row.prop(scene.miblend_properties.resource_properties, "randomize_speed")
                row.enabled = scene.miblend_properties.resource_properties.animate_textures

        row = box.row()
        row.scale_y = 1.4
        row.operator("miblend.apply_resource_pack", icon='CHECKMARK')
