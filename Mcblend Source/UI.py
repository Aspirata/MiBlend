from .MCB_API import *
from .Data import *
from bpy.types import Panel
from .Assets import Assets
from .Resource_Packs import get_resource_packs

class WorldAndMaterialsPanel(Panel):
    bl_label = "World & Materials"
    bl_idname = "world.panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):
        layout = self.layout

        scene = bpy.context.scene

        global WProperties
        WProperties = scene.world_properties

        global Preferences
        Preferences = bpy.context.preferences.addons[__package__].preferences

        world = scene.world
        
        clouds_exists = False
        sky_exists = False

        if Preferences.transparent_ui:
            self.bl_options = {'HIDE_HEADER'}
        else:
            self.bl_options = {'DEFAULT_CLOSED'}

        # World

        box = layout.box()
        row = box.row()
        row.label(text="World", icon="WORLD_DATA")
        row = box.row()
        row.prop(WProperties, "backface_culling")

        row = box.row()
        row.prop(WProperties, "delete_useless_textures")

        row = box.row()
        row.prop(WProperties, "lazy_biome_fix")

        row = box.row()
        row.prop(WProperties, "use_alpha_blend")

        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("world.fix_world", text="Fix World")

        # Resource Packs

        box = layout.box()
        row = box.row()
        row.label(text="Resource Packs", icon="FILE_FOLDER")
        
        sbox = box.box()
        row = sbox.row()
        row.label(text="Resource Packs List", icon="OUTLINER")
        row.prop(scene.resource_properties, "toggle_resource_packs_list", toggle=True, icon=("TRIA_DOWN" if scene.resource_properties.toggle_resource_packs_list else "TRIA_LEFT"), icon_only=True)
        if scene.resource_properties.toggle_resource_packs_list:
            try:
                resource_packs = get_resource_packs()

                for pack, pack_info in resource_packs.items():
                    row = sbox.row()

                    icon = 'CHECKBOX_HLT' if pack_info["enabled"] else 'CHECKBOX_DEHLT'
                    toggle_op = row.operator("resource_pack.toggle", text="", icon=icon)
                    toggle_op.pack_name = pack

                    row.label(text=pack)
                    
                    move_up = row.operator("resource_pack.move_up", text="", icon='TRIA_UP')
                    move_up.pack_name = pack

                    move_down = row.operator("resource_pack.move_down", text="", icon='TRIA_DOWN')
                    move_down.pack_name = pack

                    remove = row.operator("resource_pack.remove", text="", icon='X')
                    remove.pack_name = pack
            
                row = sbox.row()
                row.operator("resource_pack.update_default_pack", icon='NEWFOLDER')

                row = sbox.row()
                row.operator("resource_pack.add", icon='ADD')
            except:
                row = sbox.row()
                row.operator("resource_pack.fix", icon='TOOL_SETTINGS')
        
        row = box.row()
        row.prop(scene.resource_properties, "resource_packs_settings", toggle=True, icon=("TRIA_DOWN" if scene.resource_properties.resource_packs_settings else "TRIA_RIGHT"))
        if scene.resource_properties.resource_packs_settings:

            sbox = box.box()
            row = sbox.row()
            row.prop(scene.resource_properties, "ignore_dublicates")

            row = sbox.row()
            row.prop(scene.resource_properties, "use_i")

            row = sbox.row()
            row.prop(scene.resource_properties, "use_additional_textures")
            row.prop(scene.resource_properties, "textures_settings", toggle=True, icon=("TRIA_DOWN" if scene.resource_properties.textures_settings else "TRIA_LEFT"), icon_only=True)
            if scene.resource_properties.textures_settings:

                tbox = sbox.box()
                row = tbox.row()
                row.label(text="PBR Textures:", icon="SHADING_RENDERED")
                row = tbox.row()
                row.enabled = scene.resource_properties.use_additional_textures
                row.prop(scene.resource_properties, "use_n")

                row = tbox.row()
                row.enabled = scene.resource_properties.use_additional_textures
                row.prop(scene.resource_properties, "use_s")
                row.prop(scene.resource_properties, "s_settings", toggle=True, icon=("TRIA_DOWN" if scene.resource_properties.s_settings else "TRIA_LEFT"), icon_only=True)
                if scene.resource_properties.s_settings:
                    fbox = tbox.box()
                    row = fbox.row()
                    row.enabled = scene.resource_properties.use_s
                    row.prop(scene.resource_properties, "roughness")

                    row = fbox.row()
                    row.enabled = scene.resource_properties.use_s
                    row.prop(scene.resource_properties, "metallic")

                    row = fbox.row()
                    row.enabled = scene.resource_properties.use_s
                    row.prop(scene.resource_properties, "sss")

                    row = fbox.row()
                    row.enabled = scene.resource_properties.use_s
                    row.prop(scene.resource_properties, "specular")

                    row = fbox.row()
                    row.enabled = scene.resource_properties.use_s
                    row.prop(scene.resource_properties, "emission")

                row = tbox.row()
                row.enabled = scene.resource_properties.use_additional_textures
                row.prop(scene.resource_properties, "use_e")
            
            row = sbox.row()
            row.prop(scene.resource_properties, "animate_textures")
            row.prop(scene.resource_properties, "animate_textures_settings", toggle=True, icon=("TRIA_DOWN" if scene.resource_properties.animate_textures_settings else "TRIA_LEFT"), icon_only=True)
            if scene.resource_properties.animate_textures_settings:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Animation Settings:", icon="SEQUENCE")
                row = tbox.row()
                row.enabled = scene.resource_properties.animate_textures
                row.prop(scene.resource_properties, "interpolate")

                row = tbox.row()
                row.enabled = scene.resource_properties.animate_textures
                row.prop(scene.resource_properties, "only_fix_uv")

        if Preferences.dev_tools:
            row = box.row()
            remove_attr = row.operator("special.remove_attribute", text="Remove Resource Packs List")
            remove_attr.attribute = "resource_packs"

        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("resource_pack.apply", icon='CHECKMARK')

        # Sky

        node_group = None
        clouds_obj = None
        geonodes_modifier = None 

        if world is not None and (any(node.name == "Mcblend Sky" for node in bpy.data.node_groups)):
            if world_material_name in bpy.data.worlds:
                sky_exists = True
                world_material = scene.world.node_tree
                for node in world_material.nodes:
                    if node.type == 'GROUP':
                        if "Mcblend Sky" in node.node_tree.name:
                            node_group = node
                            break

        for obj in scene.objects:
            if obj.get("Mcblend ID") == "Clouds":
                clouds_exists = True
                clouds_obj = obj
                geonodes_modifier = obj.modifiers.get("Clouds Generator")
                material_tree = obj.material_slots[0].material.node_tree
                map_range_node = material_tree.nodes.get("Map Range").inputs[2]
                base_color = material_tree.nodes.get("Principled BSDF").inputs[0]
                break

        box = layout.box()
        row = box.row()
        row.label(text="Environment", icon="OUTLINER_DATA_VOLUME")

        row = box.row()
        row.prop(scene.env_properties, "create_clouds", text="Create Clouds")
        if clouds_exists:
            row.prop(scene.env_properties, "clouds_settings", toggle=True, icon=("TRIA_DOWN" if scene.env_properties.clouds_settings else "TRIA_LEFT"), icon_only=True)

            if scene.env_properties.clouds_settings:
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
                row.prop(scene.env_properties, "geonodes_settings", toggle=True, icon=("TRIA_DOWN" if scene.env_properties.geonodes_settings else "TRIA_LEFT"), icon_only=True)

                if scene.env_properties.geonodes_settings:
                    if blender_version("4.x.x"):

                        fbox = tbox.box()
                        row = fbox.row()
                        row.label(text="Layers Settings:", icon="AXIS_TOP")
                        row.prop(scene.env_properties, "layers_settings", toggle=True, icon=("TRIA_DOWN" if scene.env_properties.layers_settings else "TRIA_LEFT"), icon_only=True)
                        if scene.env_properties.layers_settings:

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
                row.prop(scene.env_properties, "material_settings", toggle=True, icon=("TRIA_DOWN" if scene.env_properties.material_settings else "TRIA_LEFT"), icon_only=True)

                if scene.env_properties.material_settings:

                    row = tbox.row()
                    row.prop(base_color, "default_value", text="Color")
                    
                    row = tbox.row()
                    row.prop(map_range_node, "default_value", text="Fade Distance")

        row = box.row() 
        row.prop(scene.env_properties, "create_sky", text="Create Sky")

        if node_group is not None:
            row.prop(scene.env_properties, "sky_settings", toggle=True, icon=("TRIA_DOWN" if scene.env_properties.sky_settings else "TRIA_LEFT"), icon_only=True)
            try:
                if not node_group.inputs["End"].default_value:
                    if scene.env_properties.sky_settings:
                        sbox = box.box()

                        tbox = sbox.box()
                        row = tbox.row()
                        row.label(text="Main Settings:", icon="PROPERTIES")
                        row = tbox.row()
                        row.prop(node_group.inputs["Time"], "default_value", text="Time")

                        if scene.render.engine == "BLENDER_EEVEE_NEXT":
                            row = tbox.row()
                            row.prop(bpy.data.worlds[world_material_name], "sun_angle", text="Shadow Softness")

                        row = tbox.row()
                        row.prop(node_group.inputs["End"], "default_value", text="End", toggle=True)

                        tbox = sbox.box()
                        row = tbox.row()
                        row.label(text="Strength:", icon="LIGHT_SUN")
                        row.prop(scene.env_properties, "strength_settings", icon=("TRIA_DOWN" if scene.env_properties.strength_settings else "TRIA_LEFT"), icon_only=True)
                        if scene.env_properties.strength_settings:
                            row = tbox.row()
                            row.prop(node_group.inputs["Moon Strenght"], "default_value", text="Moon Strenght")
                            row = tbox.row()
                            row.prop(node_group.inputs["Sun Strength"], "default_value", text="Sun Strength")
                            row = tbox.row()
                            row.prop(node_group.inputs["Stars Strength"], "default_value", text="Stars Strength")
                            row = tbox.row()
                            row.prop(node_group.inputs["Camera Ambient Light Strength"], "default_value", text="Camera Ambient Light Strength")
                            row = tbox.row()
                            row.prop(node_group.inputs["Non-Camera Ambient Light Strength"], "default_value", text="Non-Camera Ambient Light Strength")
                                                    
                        tbox = sbox.box()
                        row = tbox.row()
                        row.label(text="Colors:", icon="IMAGE")
                        row.prop(scene.env_properties, "colors_settings", icon=("TRIA_DOWN" if scene.env_properties.colors_settings else "TRIA_LEFT"), icon_only=True)

                        if scene.env_properties.colors_settings:
                            row = tbox.row()
                            row.prop(node_group.inputs["Moon Color"], "default_value", text="Moon Color")
                            row = tbox.row()
                            row.prop(node_group.inputs["Sun Color"], "default_value", text="Sun Color")
                            row = tbox.row()
                            row.prop(node_group.inputs["Sun Color In Sunset"], "default_value", text="Sun Color In Sunset")
                            row = tbox.row()
                            row.prop(node_group.inputs["Stars Color"], "default_value", text="Stars Color")
                        
                        tbox = sbox.box()
                        row = tbox.row()
                        row.label(text="Ambient Light Colors:", icon="IMAGE")
                        row.prop(scene.env_properties, "ambient_colors_settings", icon=("TRIA_DOWN" if scene.env_properties.ambient_colors_settings else "TRIA_LEFT"), icon_only=True)
                        if scene.env_properties.ambient_colors_settings:
                            for node in bpy.data.node_groups:
                                if "Ambient Color" in node.name:
                                    for Node in node.nodes:
                                        if Node.type == "VALTORGB":
                                            row = tbox.row()
                                            row.label(text=f"{Node.name}:")
                                            for element in Node.color_ramp.elements:                                                    
                                                row.prop(element, "color", icon_only=True)
                        
                        tbox = sbox.box()
                        row = tbox.row()
                        row.label(text="Sun & Moon Rotation:", icon="DRIVER_ROTATIONAL_DIFFERENCE")
                        row.prop(scene.env_properties, "rotation_settings", icon=("TRIA_DOWN" if scene.env_properties.rotation_settings else "TRIA_LEFT"), icon_only=True)

                        if scene.env_properties.rotation_settings:
                            row = tbox.row()
                            row.prop(node_group.inputs["Rotation"], "default_value", index=0, text="X")
                            row = tbox.row()
                            row.prop(node_group.inputs["Rotation"], "default_value", index=1, text="Y")
                            row = tbox.row()
                            row.prop(node_group.inputs["Rotation"], "default_value", index=2, text="Z")

                        tbox = sbox.box()
                        row = tbox.row()
                        row.label(text="Other Settings:", icon="COLLAPSEMENU")
                        row.prop(scene.env_properties, "other_settings", icon=("TRIA_DOWN" if scene.env_properties.other_settings else "TRIA_LEFT"), icon_only=True)

                        if scene.env_properties.other_settings:
                            row = tbox.row()
                            row.prop(node_group.inputs["Pixelated Stars"], "default_value", text="Pixelated Stars", toggle=True)
                            row = tbox.row()
                            row.prop(node_group.inputs["Stars Amount"], "default_value", text="Stars Amount", slider=True)
                else:
                    if scene.env_properties.sky_settings:
                        sbox = box.box()

                        tbox = sbox.box()
                        row = tbox.row()
                        row.label(text="Main Settings:", icon="PROPERTIES")
                        row = tbox.row()
                        row.prop(node_group.inputs["Stars Amount"], "default_value", text="Stars Amount", slider=True)
                        row = tbox.row()
                        row.prop(node_group.inputs["End"], "default_value", text="End", toggle=True)

                        tbox = sbox.box()
                        row = tbox.row()
                        row.label(text="Strength:", icon="LIGHT_SUN")
                        row.prop(scene.env_properties, "strength_settings", icon=("TRIA_DOWN" if scene.env_properties.strength_settings else "TRIA_LEFT"), icon_only=True)
                        if scene.env_properties.strength_settings:
                            row = tbox.row()
                            row.prop(node_group.inputs["End Stars Strength"], "default_value", text="Stars Strength")
                            row = tbox.row()
                            row.prop(node_group.inputs["Camera Ambient Light Strength"], "default_value", text="Camera Ambient Light Strength")
                            row = tbox.row()
                            row.prop(node_group.inputs["Non-Camera Ambient Light Strength"], "default_value", text="Non-Camera Ambient Light Strength")

                        tbox = sbox.box()
                        row = tbox.row()
                        row.label(text="Colors:", icon="IMAGE")
                        row.prop(scene.env_properties, "colors_settings", icon=("TRIA_DOWN" if scene.env_properties.colors_settings else "TRIA_LEFT"), icon_only=True)
                        if scene.env_properties.colors_settings:
                            row = tbox.row()
                            row.prop(node_group.inputs["End Stars Color"], "default_value", text="Stars Color")

                        tbox = sbox.box()
                        row = tbox.row()
                        row.label(text="Ambient Light Colors:", icon="IMAGE")
                        row.prop(scene.env_properties, "ambient_colors_settings", icon=("TRIA_DOWN" if scene.env_properties.ambient_colors_settings else "TRIA_LEFT"), icon_only=True)
                        if scene.env_properties.ambient_colors_settings:
                            for node in bpy.data.node_groups:
                                if node.name == "Mcblend End":
                                    for Node in node.nodes:
                                        if Node.type == "VALTORGB":
                                            row = tbox.row()
                                            row.label(text=f"{Node.name}:")
                                            for element in Node.color_ramp.elements:                                                    
                                                row.prop(element, "color", icon_only=True)
                        
                        tbox = sbox.box()
                        row = tbox.row()
                        row.label(text="Star Rotation:", icon="DRIVER_ROTATIONAL_DIFFERENCE")
                        row.prop(scene.env_properties, "rotation_settings", icon=("TRIA_DOWN" if scene.env_properties.rotation_settings else "TRIA_LEFT"), icon_only=True)

                        if scene.env_properties.rotation_settings:
                            row = tbox.row()
                            row.prop(node_group.inputs["End Stars Rotation"], "default_value", index=0, text="X")
                            row = tbox.row()
                            row.prop(node_group.inputs["End Stars Rotation"], "default_value", index=1, text="Y")
                            row = tbox.row()
                            row.prop(node_group.inputs["End Stars Rotation"], "default_value", index=2, text="Z")
                        
                        tbox = sbox.box()
                        row = tbox.row()
                        row.label(text="Other Settings:", icon="COLLAPSEMENU")
                        row.prop(scene.env_properties, "other_settings", icon=("TRIA_DOWN" if scene.env_properties.other_settings else "TRIA_LEFT"), icon_only=True)

                        if scene.env_properties.other_settings:
                            row = tbox.row()
                            row.prop(node_group.inputs["Pixelated Stars"], "default_value", text="Pixelated Stars", toggle=True)


            except Exception as Error:
                row = box.row()
                row.label(text="Unknown Error Printed in Console. Report To Aspirata", icon="ERROR")
                row = box.row()
                row.label(text="To Open Console Press Window > Toggle System Console")
                print(Error)

        if clouds_exists or sky_exists:
            row = box.row()
            row.scale_y = Big_Button_Scale
            row.operator("env.create_env", text="Recreate Environment", icon="FILE_REFRESH")

        if not clouds_exists and not sky_exists:
            row = box.row()
            row.scale_y = Big_Button_Scale
            row.operator("env.create_env")
        
        # Materials
            
        box = layout.box()
        row = box.row()
        row.label(text="Materials", icon="MATERIAL_DATA")

        if os.path.isfile(os.path.join(materials_folder, "Upgraded Materials.blend")):
            row = box.row()
            row.scale_y = Big_Button_Scale
            row.operator("materials.upgrade_materials", text="Upgrade Materials")

        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("materials.fix_materials", text="Fix Materials")

        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("materials.swap_textures", icon="UV_SYNC_SELECT")
        
        # PPBR

        box = layout.box()
        row = box.row()
        row.label(text="Procedural PBR", icon="NODE_MATERIAL")

        row = box.row()
        row.prop(scene.ppbr_properties, "use_normals")
        row.prop(scene.ppbr_properties, "normals_settings", icon=("TRIA_DOWN" if scene.ppbr_properties.normals_settings else "TRIA_LEFT"), icon_only=True)
        if scene.ppbr_properties.normals_settings:
            sbox = box.box()
            row = sbox.row()
            row.label(text="Normals Type:", icon="NORMALS_FACE")

            row = sbox.row()
            row.prop(scene.ppbr_properties, "normals_selector", expand=True)

            if scene.ppbr_properties.normals_selector == "Bump":
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Bump Settings:", icon="MODIFIER")

                row = tbox.row()
                row.prop(scene.ppbr_properties, "bump_strength", slider=True)
            else:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Procedural Normals Settings:", icon="MODIFIER")

                row = tbox.row()
                row.prop(scene.ppbr_properties, "pnormals_size", slider=True)

                row = tbox.row()
                row.prop(scene.ppbr_properties, "pnormals_blur", slider=True)

                row = tbox.row()
                row.prop(scene.ppbr_properties, "pnormals_strength", slider=True)

                row = tbox.row()
                row.prop(scene.ppbr_properties, "pnormals_exclude", slider=True)

                row = tbox.row()
                row.prop(scene.ppbr_properties, "pnormals_min", slider=True)

                row = tbox.row()
                row.prop(scene.ppbr_properties, "pnormals_max", slider=True)

                row = tbox.row()
                row.prop(scene.ppbr_properties, "pnormals_size_x_multiplier", slider=True)

                row = tbox.row()
                row.prop(scene.ppbr_properties, "pnormals_size_y_multiplier", slider=True)
            
            row = tbox.row()
            row.prop(scene.ppbr_properties, "revert_normals", slider=True)
            row.enabled = not context.scene.ppbr_properties.use_normals
        
        if Preferences.dev_tools:
            row = box.row()
            row.prop(scene.ppbr_properties, "pspecular")
            row.prop(scene.ppbr_properties, "pspecular_settings", icon=("TRIA_DOWN" if scene.ppbr_properties.pspecular_settings else "TRIA_LEFT"), icon_only=True)
            if scene.ppbr_properties.pspecular_settings:
                sbox = box.box()
                row = sbox.row()
                row.label(text="Procedural Specular Settings:", icon="MODIFIER")

                row = sbox.row()
                row.prop(scene.ppbr_properties, "ps_interpolation")

                row = sbox.row()
                row.prop(scene.ppbr_properties, "ps_dif")

                row = sbox.row()
                row.prop(scene.ppbr_properties, "ps_revert")
        
            row = box.row()
            row.prop(scene.ppbr_properties, "proughness")
            row.prop(scene.ppbr_properties, "proughness_settings", icon=("TRIA_DOWN" if scene.ppbr_properties.proughness_settings else "TRIA_LEFT"), icon_only=True)
            if scene.ppbr_properties.proughness_settings:
                sbox = box.box()
                row = sbox.row()
                row.label(text="Procedural Roughness Settings:", icon="MODIFIER")

                row = sbox.row()
                row.prop(scene.ppbr_properties, "pr_interpolation")

                row = sbox.row()
                row.prop(scene.ppbr_properties, "pr_dif")

                row = sbox.row()
                row.prop(scene.ppbr_properties, "pr_revert")

        row = box.row()
        row.prop(scene.ppbr_properties, "advanced_settings", toggle=True, text="Advanced Settings", icon=("TRIA_DOWN" if scene.ppbr_properties.advanced_settings else "TRIA_RIGHT"))
        if scene.ppbr_properties.advanced_settings:
            sbox = box.box()
            row = sbox.row()
            row.prop(scene.ppbr_properties, "make_better_emission", text="Make Better Emission")

            row = sbox.row()
            row.prop(scene.ppbr_properties, "animate_textures", text="Animate Textures")

            row = sbox.row()
            row.prop(context.scene.ppbr_properties, "change_bsdf")
            row.prop(scene.ppbr_properties, "change_bsdf_settings", icon=("TRIA_DOWN" if scene.ppbr_properties.change_bsdf_settings else "TRIA_LEFT"), icon_only=True)
            if  scene.ppbr_properties.change_bsdf_settings:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Global PBSDF Settings:", icon="MODIFIER")
                row = tbox.row()
                # Добавить все штуки из PBSDF
                row.prop(scene.ppbr_properties, "specular", slider=True, text="Specular")
                row = tbox.row()
                row.prop(scene.ppbr_properties, "roughness", slider=True, text="Roughness")

            row = sbox.row()
            row.prop(scene.ppbr_properties, "use_sss")
            row.prop(scene.ppbr_properties, "sss_settings", icon=("TRIA_DOWN" if scene.ppbr_properties.sss_settings else "TRIA_LEFT"), icon_only=True)
            if scene.ppbr_properties.sss_settings:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="SSS Settings:", icon="MODIFIER")
                row = tbox.row()
                row.prop(scene.ppbr_properties, "sss_type", text="")
                row = tbox.row()
                row.prop(scene.ppbr_properties, "sss_skip")
                row = tbox.row()
                if blender_version("4.x.x"):
                    row.prop(scene.ppbr_properties, "connect_texture")
                else:
                    row.prop(scene.ppbr_properties, "connect_texture", text="Connect Texture To The SSS Color")

                if blender_version("4.x.x"):
                    row = tbox.row()
                    row.prop(scene.ppbr_properties, "sss_weight", slider=True)
                    row = tbox.row()
                    row.prop(scene.ppbr_properties, "sss_scale", slider=True)
                else:
                    row = tbox.row()
                    row.prop(scene.ppbr_properties, "sss_weight", text="Subsurface", slider=True)
                
                row = tbox.row()
                row.prop(context.scene.ppbr_properties, "revert_sss")
                row.enabled = not context.scene.ppbr_properties.use_sss
            
            row = sbox.row()
            row.prop(scene.ppbr_properties, "use_translucency")
            row.prop(scene.ppbr_properties, "translucency_settings", icon=("TRIA_DOWN" if scene.ppbr_properties.translucency_settings else "TRIA_LEFT"), icon_only=True)
            if scene.ppbr_properties.translucency_settings:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Translucent Materials Settings:", icon="MODIFIER")
                row = tbox.row()
                row.prop(scene.ppbr_properties, "translucency", slider=True)

                row = tbox.row()
                row.prop(context.scene.ppbr_properties, "revert_translucency")
                row.enabled = not context.scene.ppbr_properties.use_translucency

            row = sbox.row()
            row.prop(scene.ppbr_properties, "make_metal")
            row.prop(scene.ppbr_properties, "metal_settings", icon=("TRIA_DOWN" if scene.ppbr_properties.metal_settings else "TRIA_LEFT"), icon_only=True)
            if scene.ppbr_properties.metal_settings:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Metallic Materials Settings:", icon="MODIFIER")
                row = tbox.row()
                row.prop(scene.ppbr_properties, "metal_metallic", slider=True)
                row = tbox.row()
                row.prop(scene.ppbr_properties, "metal_roughness", slider=True)

            row = sbox.row()
            row.prop(scene.ppbr_properties, "make_reflections")
            row.prop(scene.ppbr_properties, "reflections_settings", icon=("TRIA_DOWN" if scene.ppbr_properties.reflections_settings else "TRIA_LEFT"), icon_only=True)
            if scene.ppbr_properties.reflections_settings:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Reflective Materials Settings:", icon="MODIFIER")
                row = tbox.row()
                row.prop(scene.ppbr_properties, "reflections_roughness", text="Roughness", slider=True)
                
        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("ppbr.setproceduralpbr", text="Set Procedural PBR")

class OptimizationPanel(Panel):
    bl_label = "Optimization"
    bl_idname = "optimization.panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):
        layout = self.layout

        if Preferences.transparent_ui:
            self.bl_options = {'HIDE_HEADER'}
        else:
            self.bl_options = {'DEFAULT_CLOSED'}

        box = layout.box()
        row = box.row()
        row.prop(bpy.context.scene.optimizationproperties, "use_camera_culling", text="Use Camera Culling")
        row.prop(bpy.context.scene.optimizationproperties, "camera_culling_settings", icon=("TRIA_DOWN" if bpy.context.scene.optimizationproperties.camera_culling_settings else "TRIA_LEFT"), icon_only=True)
        # Camera Culling Settings
        if bpy.context.scene.optimizationproperties.camera_culling_settings:
            sbox = box.box()
            row = sbox.row()
            row.label(text="Camera Culling Type:", icon="CAMERA_DATA")
            row = sbox.row()
            row.prop(bpy.context.scene.optimizationproperties, "camera_culling_type", text='camera_culling_type', expand=True)
            if bpy.context.scene.optimizationproperties.camera_culling_type == 'Raycast':
                # Raycast Camera Culling Settings
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Culling Mode:")
                row = tbox.row()
                row.prop(bpy.context.scene.optimizationproperties, "culling_mode", expand=True, text='culling_mode')
                row = tbox.row()
                row.prop(bpy.context.scene.optimizationproperties, "culling_distance", text="Anti-Culling Distance")
                row = tbox.row()
                row.prop(bpy.context.scene.optimizationproperties, "predict_fov", text="Predict FOV")
                row = tbox.row()
                row.prop(bpy.context.scene.optimizationproperties, "merge_by_distance", text="Merge By Distance")
                    
                if bpy.context.scene.optimizationproperties.merge_by_distance:
                    row = tbox.row()
                    row.prop(bpy.context.scene.optimizationproperties, "merge_distance", text="Merge Distance")

                row = tbox.row()
                row.prop(bpy.context.scene.optimizationproperties, "backface_culling", text="Backface Culling")

                if bpy.context.scene.optimizationproperties.backface_culling:
                    row = tbox.row()
                    row.prop(bpy.context.scene.optimizationproperties, "backface_culling_distance", text="Backface Culling Distance")

                row = tbox.row()
                row.prop(bpy.context.scene.optimizationproperties, "scale")
            else:
                # Vector Camera Culling Settings
                tbox = sbox.box()
                row = tbox.row()
                row.prop(bpy.context.scene.optimizationproperties, "backface_culling", text="Backface Culling")
                row = tbox.row()
                row.prop(bpy.context.scene.optimizationproperties, "threshold", slider=True)

        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("optimization.optimization", text="Optimize")

class UtilsPanel(Panel):
    bl_label = "Utils"
    bl_idname = "utils.panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):
        layout = self.layout

        if Preferences.transparent_ui:
            self.bl_options = {'HIDE_HEADER'}
        else:
            self.bl_options = {'DEFAULT_CLOSED'}


        box = layout.box()
        row = box.row()
        row.label(text="Rendering", icon="RESTRICT_RENDER_OFF")

        row = box.row()
        row.prop(bpy.context.scene.utilsproperties, "current_preset", text="Current Preset")
        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("utils.setrendersettings")

        box = layout.box()
        row = box.row()
        row.label(text="Materials", icon="MATERIAL")

        row = box.row()
        row.scale_x = 1.3
        row.prop(bpy.context.scene.utilsproperties, "enchant_settings", toggle=True, icon=("TRIA_DOWN" if bpy.context.scene.utilsproperties.enchant_settings else "TRIA_RIGHT"), icon_only=True)
        row.scale_y = Big_Button_Scale
        row.operator("utils.enchant", text="Enchant Objects")

        if bpy.context.scene.utilsproperties.enchant_settings:
            sbox = box.box()
            row = sbox.row()
            row.prop(bpy.context.scene.utilsproperties, "divider")
            row = sbox.row()
            row.prop(bpy.context.scene.utilsproperties, "camera_strenght")
            row = sbox.row()
            row.prop(bpy.context.scene.utilsproperties, "non_camera_strenght")

        box = layout.box()
        row = box.row()
        row.label(text="Rigging", icon="ARMATURE_DATA")
        row = box.row()
        row.prop(bpy.context.scene.utilsproperties, "armature")

        row = box.row()
        row.prop(bpy.context.scene.utilsproperties, "lattice")

        row = box.row()
        row.prop(bpy.context.scene.utilsproperties, "vertex_group_name")

        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("utils.assingvertexgroup")

class AssetPanel(Panel):
    bl_label = "Assets"
    bl_idname = "assets.panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):

        def importcategoryfix():
            asset_category = context.scene.assetsproperties.asset_category

            if asset_category == "Scripts":
                return "Run Script"
            
            if asset_category == "Rigs":
                return "Import Rig"
            
            if asset_category == "Shader Nodes":
                return "Import Node Group"
            
            if asset_category == "Geo Nodes":
                return "Import Geo Node"

            if asset_category == "Model":
                return "Import Model"

        layout = self.layout
        
        if Preferences.transparent_ui:
            self.bl_options = {'HIDE_HEADER'}
        else:
            self.bl_options = {'DEFAULT_CLOSED'}

        box = layout.box()

        row = box.row()
        row.label(text="Asset Category:")
        row = box.row()
        row.prop(context.scene.assetsproperties, "asset_category", text="")

        box.template_list("Assets_List_UL_", "", context.scene.assetsproperties, "asset_items", bpy.context.scene.assetsproperties, "asset_index")

        row = box.row()
        row.operator("assets.update_assets")

        if Preferences.dev_tools:
            row = box.row()
            remove_attr = row.operator("special.remove_attribute", text="Remove Assets List")
            remove_attr.attribute = "assetsproperties.asset_items"

        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("assets.import_asset", text=importcategoryfix())

class Assets_List_UL_(bpy.types.UIList):

    def get_custom_icon(self, item):
        for category, assets in Assets.items():
            if item.name in assets:
                asset_type = category

                if asset_type == "Rigs":
                    return "ARMATURE_DATA"
                
                if asset_type == "Scripts":
                    return "FILE_SCRIPT"
                
                if asset_type == "Shader Nodes":
                    return "NODE"
                
                if asset_type == "Geo Nodes":
                    return "GEOMETRY_NODES"

                if asset_type == "Model":
                    return "OBJECT_DATA"
                
        return "QUESTION"


    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = self.get_custom_icon(item)
        layout.label(text=item.name, icon=custom_icon)
    
    def filter_items(self, context, data, property):
        flt_flags = []
        flt_neworder = []

        asset_category = context.scene.assetsproperties.asset_category

        for index, item in enumerate(data.asset_items):
            found = False
            for category, assets in Assets.items():
                if item.name in assets:
                    try:
                        if blender_version(assets[item.name]["Blender_version"]):
                            if asset_category == "All" or category == asset_category:
                                flt_flags.append(self.bitflag_filter_item)
                            else:
                                flt_flags.append(0)
                        else:
                            flt_flags.append(0)
                    except KeyError:
                        if asset_category == "All" or category == asset_category:
                            flt_flags.append(self.bitflag_filter_item)
                        else:
                            flt_flags.append(0)
                    found = True
                    break

            if not found:
                flt_flags.append(0)
        
        while len(flt_flags) < len(data.asset_items):
            flt_flags.append(0)

        return flt_flags, flt_neworder