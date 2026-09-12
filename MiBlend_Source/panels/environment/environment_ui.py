import bpy
from bpy.types import Panel
from ...mib_utils import get_preferences, draw_toggle_button, get_miblend_object, draw_gui_failure


class MIBLEND_PT_environment(Panel):
    bl_label = "Environment"
    bl_idname = "miblend.environment_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MiBlend'

    def draw(self, context):
        try:
            layout = self.layout
            preferences = get_preferences()

            if preferences.transparent_ui:
                self.bl_options = {'HIDE_HEADER'}
            else:
                self.bl_options = set()
            
            sky_material = bpy.data.worlds.get("MiBlend Sky", None)
            sky_controller = get_miblend_object("sky_controller")
            if sky_material and sky_material.node_tree:
                sky_material_node = next((node for node in sky_material.node_tree.nodes if node.type == 'GROUP'), None)

            clouds_obj = get_miblend_object("clouds")
            if clouds_obj:
                if clouds_obj.active_material and clouds_obj.active_material.node_tree:
                    clouds_material_node = next((node for node in clouds_obj.active_material.node_tree.nodes if node.type == 'GROUP'), None)
                
                clouds_geometry_node_modifier = next((node for node in clouds_obj.modifiers if node.type == 'NODES'), None)
                clouds_solidify_modifier = next((node for node in clouds_obj.modifiers if node.type == 'SOLIDIFY'), None)
                clouds_bevel_modifier = next((node for node in clouds_obj.modifiers if node.type == 'BEVEL'), None)

            fog_obj = get_miblend_object("fog")

            box = layout.box()
            row = box.row()
            row.label(text="Environment", icon="OUTLINER_DATA_VOLUME")

            row = box.row()
            row.prop(context.scene.miblend_properties.environment_properties, "create_sky")
            if sky_controller and sky_material_node:
                draw_toggle_button(row, context.scene.miblend_properties.environment_properties, "sky_settings")
                self.draw_sky_settings(box, context, sky_material_node, sky_controller)

            row = box.row()
            row.prop(context.scene.miblend_properties.environment_properties, "create_clouds")
            if clouds_obj:
                draw_toggle_button(row, context.scene.miblend_properties.environment_properties, "cloud_settings")
                self.draw_cloud_settings(box, context, clouds_material_node, clouds_geometry_node_modifier, clouds_solidify_modifier, clouds_bevel_modifier)

            row = box.row()
            row.prop(context.scene.miblend_properties.environment_properties, "create_fog")
            if fog_obj:
                draw_toggle_button(row, context.scene.miblend_properties.environment_properties, "fog_settings")
                self.draw_fog_settings(box, context)

            row = box.row()
            row.scale_y = 1.4
            row.operator("miblend.create_environment")
        except Exception as e:
            draw_gui_failure(self, layout)
    
    def draw_sky_settings(self, layout, context, sky_material_node, sky_controller):
        if not context.scene.miblend_properties.environment_properties.sky_settings:
            return

        box = layout.box()
        row = box.row()
        row.label(text="Sky Settings:", icon="MODIFIER")

        sbox = box.box()
        row = sbox.row()
        row.label(text="Main Settings:", icon="PROPERTIES")

        row = sbox.row()
        row.prop(sky_controller, '["Sky Mode"]', expand=True)

        if sky_controller.get("Sky Mode") == 0:
            row = sbox.row()
            row.prop(sky_controller, "rotation_euler", text="Rotation X", index=0)

            row = sbox.row()
            row.scale_y = 0.7
            row.label(text=f"Time - {sky_controller.get('local_time'):.2f}", icon="INFO")

        sbox = box.box()
        row = sbox.row() 
        row.label(text="Lighting:", icon="LIGHT")

        tbox = sbox.box()
        row = tbox.row()
        row.label(text="Sky:", icon="WORLD_DATA")

        row = tbox.row()
        row.prop(sky_material_node.inputs["Camera Sky Strength"], "default_value", text="Camera Sky Strength")

        row = tbox.row()
        row.prop(sky_material_node.inputs["Non-Camera Sky Strength"], "default_value", text="Non-Camera Sky Strength")

        if sky_controller.get("Sky Mode") == 0:
            row = tbox.row()
            row.prop(sky_material_node.inputs["Sun & Moon Strength"], "default_value", text="Sun & Moon Emission Strength")

            tbox = sbox.box()
            row = tbox.row()
            row.label(text="Sun & Moon:", icon="LIGHT_SUN")

            row = tbox.row()
            row.prop(sky_controller, '["Sun Light Strength"]', text="Sun Light Strength")

            row = tbox.row()
            row.prop(sky_controller, '["Moon Light Strength"]', text="Moon Light Strength")

        if sky_controller.get("Sky Mode") != 1:
            tbox = sbox.box()
            row = tbox.row()
            row.label(text="Stars:", icon="SOLO_ON")

            row = tbox.row()
            row.prop(sky_material_node.inputs["Stars Strength"], "default_value", text="Stars Strength")
        
            sbox = box.box()
            row = sbox.row() 
            row.label(text="Other:", icon="OPTIONS")

            row = sbox.row()
            row.prop(sky_material_node.inputs["Stars Offset"], "default_value", text="Stars Offset")

    def draw_cloud_settings(self, layout, context, clouds_material_node, clouds_geometry_node_modifier,
                            clouds_solidify_modifier, clouds_bevel_modifier):
        if not context.scene.miblend_properties.environment_properties.cloud_settings:
            return

        box = layout.box()
        row = box.row()
        row.label(text="Cloud Settings:", icon="MODIFIER")

        sbox = box.box()
        row = sbox.row()
        row.label(text="Mesh Settings:", icon="PROPERTIES")

        row = sbox.row()
        row.prop(clouds_geometry_node_modifier.properties.inputs.Socket_4, "value", text="1.21.6 Clouds")

        row = sbox.row()
        row.prop(clouds_geometry_node_modifier.properties.inputs.Socket_6, "value", text="Second Layer")

        row = sbox.row()
        row.prop(clouds_solidify_modifier, "thickness", text="Thickness")
    
    def draw_fog_settings(self, layout, context):
        if not context.scene.miblend_properties.environment_properties.fog_settings:
            return

        box = layout.box()
        row = box.row()
        row.label(text="Fog Settings:", icon="MODIFIER")
