import traceback
import bpy
from bpy.types import Panel
from ...mib_utils import get_preferences
from .environment_logic import WORLD_MATERIAL_NAME


class MIBLEND_PT_environment(Panel):
    bl_label = "Environment"
    bl_idname = "miblend.environment_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MiBlend'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        world = scene.world
        preferences = get_preferences()

        if preferences.transparent_ui:
            self.bl_options = {'HIDE_HEADER'}
        else:
            self.bl_options = set()

        sky_exists = False
        fog_exists = False
        clouds_exists = False

        sky_node = None
        fog_node = None

        fog_obj = None
        clouds_obj = None

        geonodes_modifier = None 

        try:
            if world is not None and (any(node.name == "MiBlend Sky" for node in bpy.data.node_groups)):
                if WORLD_MATERIAL_NAME in bpy.data.worlds:
                    sky_exists = True
                    world_material = scene.world.node_tree
                    for node in world_material.nodes:
                        if node.type == 'GROUP':
                            if "MiBlend Sky" in node.node_tree.name:
                                sky_node = node
                                break

            for obj in scene.objects:
                if obj.get("MiBlend ID") == "Clouds":
                    clouds_exists = True
                    clouds_obj = obj
                    geonodes_modifier = obj.modifiers.get("Clouds Generator")
                    clouds_material_tree = obj.material_slots[0].material.node_tree.nodes
                    fade_distance_value = next((node for node in clouds_material_tree if node.label == "Fade Distance"), None).inputs[2]
                    height_transparency_multiplier_value = next((node for node in clouds_material_tree if node.label == "Height Transparency Multiplier"), None).inputs[1]
                    shadow_intensity_value = next((node for node in clouds_material_tree if node.label == "Shadow Intensity"), None).inputs[1]
                    base_color = next((node for node in clouds_material_tree if node.type == "BSDF_PRINCIPLED"), None).inputs[0]
                    
                elif obj.get("MiBlend ID") == "Fog":
                    fog_exists = True
                    fog_obj = obj
                    fog_material_tree = obj.material_slots[0].material.node_tree.nodes
                    fog_node = next((node for node in fog_material_tree if node.type == 'GROUP' and "Fog" in node.node_tree.name), None)
                
                if clouds_exists and fog_exists:
                    break

            box = layout.box()
            row = box.row()
            row.label(text="Environment", icon="OUTLINER_DATA_VOLUME")

            row = box.row() 
            row.prop(scene.miblend_properties.environment_properties, "create_sky")

            # Sky Settings

            if sky_node:
                row.prop(scene.miblend_properties.environment_properties, "sky_settings", toggle=True, icon=("TRIA_DOWN" if scene.miblend_properties.environment_properties.sky_settings else "TRIA_LEFT"), icon_only=True)
                if scene.miblend_properties.environment_properties.sky_settings:
                    sbox = box.box()

                    tbox = sbox.box()
                    row = tbox.row()
                    row.label(text="Main Settings:", icon="PROPERTIES")
                    row = tbox.row()
                    row.prop(sky_node.inputs["Time"], "default_value", text="Time")

                    if scene.render.engine == "BLENDER_EEVEE_NEXT":
                        row = tbox.row()
                        row.prop(bpy.data.worlds[WORLD_MATERIAL_NAME], "sun_angle", text="Shadow Softness")

                    tbox = sbox.box()
                    row = tbox.row()
                    row.label(text="Strength:", icon="LIGHT_SUN")
                    row.prop(scene.miblend_properties.environment_properties, "strength_settings", icon=("TRIA_DOWN" if scene.miblend_properties.environment_properties.strength_settings else "TRIA_LEFT"), icon_only=True)
                    if scene.miblend_properties.environment_properties.strength_settings:
                        if not sky_node.inputs["End"].default_value:
                            row = tbox.row()
                            row.prop(sky_node.inputs["Moon Strenght"], "default_value", text="Moon Strenght")
                            row = tbox.row()
                            row.prop(sky_node.inputs["Sun Strength"], "default_value", text="Sun Strength")
                            row = tbox.row()
                            row.prop(sky_node.inputs["Stars Strength"], "default_value", text="Stars Strength")
                        else:
                            row = tbox.row()
                            row.prop(sky_node.inputs["End Stars Strength"], "default_value", text="Stars Strength")
                        row = tbox.row()
                        row.prop(sky_node.inputs["Camera Ambient Light Strength"], "default_value", text="Camera Ambient Light Strength")
                        row = tbox.row()
                        row.prop(sky_node.inputs["Non-Camera Ambient Light Strength"], "default_value", text="Non-Camera Ambient Light Strength")
                                                
                    tbox = sbox.box()
                    row = tbox.row()
                    row.label(text="Colors:", icon="IMAGE")
                    row.prop(scene.miblend_properties.environment_properties, "colors_settings", icon=("TRIA_DOWN" if scene.miblend_properties.environment_properties.colors_settings else "TRIA_LEFT"), icon_only=True)

                    if scene.miblend_properties.environment_properties.colors_settings:
                        if not sky_node.inputs["End"].default_value:
                            row = tbox.row()
                            row.prop(sky_node.inputs["Moon Color"], "default_value", text="Moon Color")
                            row = tbox.row()
                            row.prop(sky_node.inputs["Sun Color"], "default_value", text="Sun Color")
                            row = tbox.row()
                            row.prop(sky_node.inputs["Sun Color In Sunset"], "default_value", text="Sun Color In Sunset")
                            row = tbox.row()
                            row.prop(sky_node.inputs["Stars Color"], "default_value", text="Stars Color")
                        else:
                            row = tbox.row()
                            row.prop(sky_node.inputs["End Stars Color"], "default_value", text="Stars Color")
                    
                    tbox = sbox.box()
                    row = tbox.row()
                    row.label(text="Ambient Light Colors:", icon="IMAGE")
                    row.prop(scene.miblend_properties.environment_properties, "ambient_colors_settings", icon=("TRIA_DOWN" if scene.miblend_properties.environment_properties.ambient_colors_settings else "TRIA_LEFT"), icon_only=True)
                    if scene.miblend_properties.environment_properties.ambient_colors_settings:
                        for node in bpy.data.node_groups:
                            if "MiBlend End" in node.name or "Ambient Color" in node.name:
                                for Node in node.nodes:
                                    if Node.type == "VALTORGB":
                                        row = tbox.row()
                                        row.label(text=f"{Node.name}:")
                                        for element in Node.color_ramp.elements:                                                    
                                            row.prop(element, "color", icon_only=True)
                    
                    tbox = sbox.box()
                    row = tbox.row()
                    row.label(text=( "Star Rotation:" if sky_node.inputs["End"].default_value else "Sun & Moon Rotation:"), icon="DRIVER_ROTATIONAL_DIFFERENCE")
                    row.prop(scene.miblend_properties.environment_properties, "rotation_settings", icon=("TRIA_DOWN" if scene.miblend_properties.environment_properties.rotation_settings else "TRIA_LEFT"), icon_only=True)

                    if scene.miblend_properties.environment_properties.rotation_settings:
                        if sky_node.inputs["End"].default_value:
                            row = tbox.row()
                            row.prop(sky_node.inputs["End Stars Rotation"], "default_value", index=0, text="X")
                            row = tbox.row()
                            row.prop(sky_node.inputs["End Stars Rotation"], "default_value", index=1, text="Y")
                            row = tbox.row()
                            row.prop(sky_node.inputs["End Stars Rotation"], "default_value", index=2, text="Z")
                        else:
                            row = tbox.row()
                            row.prop(sky_node.inputs["Rotation"], "default_value", index=0, text="X")
                            row = tbox.row()
                            row.prop(sky_node.inputs["Rotation"], "default_value", index=1, text="Y")
                            row = tbox.row()
                            row.prop(sky_node.inputs["Rotation"], "default_value", index=2, text="Z")

                    tbox = sbox.box()
                    row = tbox.row()
                    row.label(text="Other Settings:", icon="COLLAPSEMENU")
                    row.prop(scene.miblend_properties.environment_properties, "other_settings", icon=("TRIA_DOWN" if scene.miblend_properties.environment_properties.other_settings else "TRIA_LEFT"), icon_only=True)

                    if scene.miblend_properties.environment_properties.other_settings:
                        row = tbox.row()
                        row.prop(sky_node.inputs["Stars Amount"], "default_value", text="Stars Amount", slider=True)
                        
                        row = tbox.row()
                        row.prop(sky_node.inputs["Pixelated Stars"], "default_value", text="Pixelated Stars", toggle=True)

                        row = tbox.row()
                        row.prop(sky_node.inputs["End"], "default_value", text="End", toggle=True)
            
            row = box.row()
            row.prop(scene.miblend_properties.environment_properties, "create_fog")

            # Fog Settings

            if fog_exists:
                row.prop(scene.miblend_properties.environment_properties, "fog_settings", toggle=True, icon=("TRIA_DOWN" if scene.miblend_properties.environment_properties.fog_settings else "TRIA_LEFT"), icon_only=True)

                if scene.miblend_properties.environment_properties.fog_settings:
                    sbox = box.box()
                    tbox = sbox.box()

                    row = tbox.row()
                    row.label(text="Main Settings:", icon="PROPERTIES")

                    row = tbox.row()
                    row.prop(fog_node.inputs["Fog Color"], "default_value", text="Fog Color")
                    row = tbox.row()
                    row.prop(fog_obj, "location", index=2, text="Height") 
                    row = tbox.row()
                    row.prop(fog_node.inputs["Density"], "default_value", text="Density")
                    row = tbox.row()
                    row.prop(fog_node.inputs["Max Distance"], "default_value", text="Max Distance")
                    row = tbox.row()
                    row.prop(fog_node.inputs["Min Distance"], "default_value", text="Min Distance")
                    row = tbox.row()
                    row.prop(fog_node.inputs["Anisotropy"], "default_value", text="Anisotropy")
                    row = tbox.row()
                    row.prop(fog_node.inputs["Emission"], "default_value", text="Emission")

            row = box.row()
            row.prop(scene.miblend_properties.environment_properties, "create_clouds")

            # Clouds Settings

            if clouds_exists:
                row.prop(scene.miblend_properties.environment_properties, "clouds_settings", toggle=True, icon=("TRIA_DOWN" if scene.miblend_properties.environment_properties.clouds_settings else "TRIA_LEFT"), icon_only=True)

                if scene.miblend_properties.environment_properties.clouds_settings:
                    sbox = box.box()
                    tbox = sbox.box()

                    row = tbox.row()
                    row.label(text="Main Settings:", icon="PROPERTIES")

                    row = tbox.row()                
                    row.prop(clouds_obj, "location", index=2, text="Height")

                    row = tbox.row()
                    row.prop(clouds_obj, "visible_shadow", text="Clouds Shadow", toggle=True)

                    tbox = sbox.box()

                    row = tbox.row()
                    row.label(text="Geometry Nodes Settings:", icon="GEOMETRY_NODES")
                    row.prop(scene.miblend_properties.environment_properties, "geonodes_settings", toggle=True, icon=("TRIA_DOWN" if scene.miblend_properties.environment_properties.geonodes_settings else "TRIA_LEFT"), icon_only=True)

                    if scene.miblend_properties.environment_properties.geonodes_settings:
                        fbox = tbox.box()
                        row = fbox.row()
                        row.label(text="Layers Settings:", icon="AXIS_TOP")
                        row.prop(scene.miblend_properties.environment_properties, "layers_settings", toggle=True, icon=("TRIA_DOWN" if scene.miblend_properties.environment_properties.layers_settings else "TRIA_LEFT"), icon_only=True)
                        if scene.miblend_properties.environment_properties.layers_settings:

                            row = fbox.row()
                            row.prop(geonodes_modifier, '["Socket_2"]', text="Layers Count", slider=True)

                            row = fbox.row()
                            row.label(text="Layers Offset:", icon="DRIVER_DISTANCE")

                            row = fbox.row()
                            row.prop(geonodes_modifier, '["Socket_5"]', index=0, text="X")
                            row = fbox.row()
                            row.prop(geonodes_modifier, '["Socket_5"]', index=1, text="Y")
                            row = fbox.row()
                            row.prop(geonodes_modifier, '["Socket_5"]', index=2, text="Z")
                        
                        row = tbox.row()
                        row.prop(geonodes_modifier, '["Socket_6"]', text="Density Factor", slider=True)

                        row = tbox.row()
                        row.prop(geonodes_modifier, '["Socket_7"]', text="Offset Scale")

                        row = tbox.row()
                        row.prop(geonodes_modifier, '["Socket_9"]', text="Subdivisions")

                        row = tbox.row()
                        row.prop(geonodes_modifier, '["Socket_19"]', text="Seed")

                        row = tbox.row()
                        row.prop(geonodes_modifier, '["Socket_10"]', text="3D Clouds", toggle=True)
                    
                    tbox = sbox.box()
                    row = tbox.row()
                    row.label(text="Material Settings:", icon="MATERIAL")
                    row.prop(scene.miblend_properties.environment_properties, "material_settings", toggle=True, icon=("TRIA_DOWN" if scene.miblend_properties.environment_properties.material_settings else "TRIA_LEFT"), icon_only=True)

                    if scene.miblend_properties.environment_properties.material_settings:

                        row = tbox.row()
                        row.prop(base_color, "default_value", text="Color")
                        
                        row = tbox.row()
                        row.prop(fade_distance_value, "default_value", text="Fade Distance")

                        row = tbox.row()
                        row.prop(shadow_intensity_value, "default_value", text="Shadow intensity")

                        row = tbox.row()
                        row.prop(height_transparency_multiplier_value, "default_value", text="Height Transparency Multiplier")

        except Exception:
            box = layout.box()
            row = box.row()
            row.label(text="An Error occured !", icon="ERROR")

            row = box.row()
            row.label(text="This error could be caused by outdated sky or clouds")

            row = box.row()
            row.label(text="Try to recreate the environment")

            print(traceback.format_exc())

            row = box.row()
            row.operator("miblend.absolute_solver_open_console")

        if clouds_exists or sky_exists:
            row = box.row()
            row.scale_y = 1.4
            row.operator("miblend.create_env", text="Recreate Environment", icon="FILE_REFRESH")

        if not clouds_exists and not sky_exists:
            row = box.row()
            row.scale_y = 1.4
            row.operator("miblend.create_env")
