import os
import bpy
from bpy.types import Panel
from ...mib_utils import dprint, get_preferences


class MIBLEND_PT_assets(Panel):
    bl_label = "Assets"
    bl_idname = "miblend.assets_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MiBlend'


    @staticmethod
    def import_asset_text(index):
        if index <= len(bpy.context.scene.miblend_properties.assets_properties.asset_items) and len(bpy.context.scene.miblend_properties.assets_properties.asset_items) > 0:
            asset_type = bpy.context.scene.miblend_properties.assets_properties.asset_items[index].get("Type", "")

            if asset_type == "Script":
                return "Run Script"
            else:
                return f"Import {asset_type}"

        return "Import Asset"

    def draw(self, context):
        layout = self.layout
        prefs = get_preferences()
        assets_props = bpy.context.scene.miblend_properties.assets_properties
        current_index = assets_props.asset_index
        items = assets_props.asset_items
        
        if prefs.transparent_ui:
            self.bl_options = {'HIDE_HEADER'}
        else:
            self.bl_options = {'DEFAULT_CLOSED'}
            
        if current_index >= 0 and current_index < len(items):
            current_asset = items[current_index]
        else:
            current_asset = None

        box = layout.box()
        row = box.row()
        row.label(text="Assets", icon="ASSET_MANAGER")
        sbox = box.box()
        row = sbox.row()
        if not assets_props.asset_items:
            row.label(text="No assets found, reload assets list", icon="ERROR")
            row = sbox.row()
            row.operator("miblend.update_assets", icon="FILE_REFRESH")
            return
        else:
            row.template_list("MIBLEND_UL_assets", "", assets_props, "asset_items", assets_props, "asset_index")

        row = sbox.row()
        row.operator("miblend.add_asset", text="", icon="ADD")

        if current_asset and os.path.dirname(current_asset.get("File_path", "")) in bpy.context.scene.get("mib_options", {}).get("temp_assets_paths", []):
            row.operator("miblend.remove_asset", icon="REMOVE")

        if prefs.dev_tools and prefs.debug_tools:
            remove_attr = row.operator("miblend.remove_attribute", text="", icon="X")
            remove_attr.attribute = "miblend_properties.assets_properties.asset_items"
            
        row.operator("miblend.update_assets", icon="FILE_REFRESH")

        if current_asset and current_asset.get("has_properties", False):
            properties = {key.replace('_property', ''): value for key, value in current_asset.items() if 'property' in key}

            sbox = box.box()
            row = sbox.row()
            row.label(text="Properties:", icon="PROPERTIES")
            row.prop(assets_props, "properties_toggle", icon=("TRIA_DOWN" if assets_props.properties_toggle else "TRIA_LEFT"), icon_only=True)
            
            if assets_props.properties_toggle:
                for key, value in properties.items():
                    row = sbox.row()
                    if isinstance(value, (bool, int, float, str)):
                        row.prop(current_asset, f'["{key}_property"]', text=key)
                    else:
                        row.label(text=f"{key}: {value}")

                row = sbox.row()
                row.operator("miblend.reset_properties", icon="LOOP_BACK")
                row.operator("miblend.save_properties", icon="FILE_TICK")
        
        # Filters
        row = box.row()
        row.prop(assets_props, "filters", toggle=True, icon=("TRIA_DOWN" if assets_props.filters else "TRIA_RIGHT"))

        if assets_props.filters:
            sbox = box.box()
            primary_tags = {"Rig", "Script", "Shader Node", "Geo Node", "Compositor Node", "Model", "Material"}
            secondary_tags = {"Simple", "Realistic", "Mixed", "Story Mode", "Node", "Particles"}

            # Sort tags into categories
            primary_tag_list = []
            secondary_tag_list = []
            other_tag_list = []
            
            for tag in assets_props.tags:
                if tag.name in primary_tags:
                    primary_tag_list.append(tag)
                elif tag.name in secondary_tags:
                    secondary_tag_list.append(tag)
                else:
                    other_tag_list.append(tag)
                
            # Sort tags within each category alphabetically
            primary_tag_list.sort(key=lambda x: x.name)
            secondary_tag_list.sort(key=lambda x: x.name)
            other_tag_list.sort(key=lambda x: x.name)

            row = sbox.row()
            row.label(text="Tags:", icon="TAG")
            row = sbox.row()

            split = row.split(factor=0.33 if other_tag_list else 0.5)

            col_primary = split.column()
            col_primary.label(text="Primary")
            for tag in primary_tag_list:
                col_primary.prop(tag, "enabled", text=tag.name)

            col_secondary = split.column()
            col_secondary.label(text="Secondary")
            for tag in secondary_tag_list:
                col_secondary.prop(tag, "enabled", text=tag.name)
            
            if other_tag_list:
                col_other = split.column()
                col_other.label(text="Other")
                for tag in other_tag_list:
                    col_other.prop(tag, "enabled", text=tag.name)

            row = sbox.row()
            row.label(text="Tags Mode:")
            row.prop(assets_props, "tags_mode", expand=True)
            row = sbox.row()
            row.prop(assets_props, "filter_by_version", toggle=True)

        if current_asset:
            row = box.row()
            row.scale_y = 1.4
            row.operator("miblend.import_asset", text=self.import_asset_text(current_index), icon="REC")

class MIBLEND_UL_assets(bpy.types.UIList):
    @staticmethod
    def blender_version(blender_version: str) -> bool:
        try:
            version_parts = blender_version.split(" ")
            operator = version_parts[0]
            major, minor, patch = version_parts[1].lower().split(".")
            version = (int(major), int(minor), int(patch))
            return {
                '<': bpy.app.version < version,
                '<=': bpy.app.version <= version,
                '>': bpy.app.version > version,
                '>=': bpy.app.version >= version,
                '==': bpy.app.version == version,
            }.get(operator, False)
        except ValueError:
            return False

    @staticmethod
    def get_custom_icon(item):
        asset_type = item.get("Type", "")
        return {
            "Rig": "ARMATURE_DATA",
            "Material": "MATERIAL_DATA",
            "Script": "FILE_SCRIPT",
            "Compositor Node": "NODE_SEL",
            "Shader Node": "NODE",
            "Geo Node": "GEOMETRY_NODES",
            "Model": "OBJECT_DATA",
        }.get(asset_type, "QUESTION")

    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, _index):
        layout.row().label(text=item.get("Asset_name", "Unknown"), icon=self.get_custom_icon(item))
    
    def filter_items(self, context, data, _property):
        flt_flags = []
        selected_tags = {tag.name for tag in context.scene.miblend_properties.assets_properties.tags if tag.enabled}
        tags_mode = context.scene.miblend_properties.assets_properties.tags_mode
        filter_by_version = context.scene.miblend_properties.assets_properties.filter_by_version

        for index, item in enumerate(data.asset_items):
            item_tags = set(item.get('Tags', []))
            
            matches_tags = (tags_mode == "and" and selected_tags.issubset(item_tags)) or \
                 (tags_mode == "or" and selected_tags.intersection(item_tags))
            
            # Check if name matches filter (only if filter is not empty)
            matches_name = True if not self.filter_name else self.filter_name.lower() in item.get('Asset_name').lower()
            
            # Check version compatibility
            dprint(item.get('Asset_name'), item.get('Blender_version', ">= 4.2.0"), item.get('File_path'), is_deep=True, zone="ui")
            matches_version = self.blender_version(item.get('Blender_version', ">= 4.2.0")) or not filter_by_version
            
            # Item passes if it matches all enabled filters
            if ((not selected_tags or matches_tags) and matches_name and matches_version):
                flt_flags.append(self.bitflag_filter_item)
            else:
                flt_flags.append(0)

        return flt_flags, []
