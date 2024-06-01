import re
from .Data import *
from .Assets import *
from .Properties import *
from .Materials import Materials
from .Optimization import Optimize
from .Utils import *
from .Translator import Translate
from .Preferences import McblendPreferences
from bpy.types import Panel, Operator
from bpy.app.handlers import persistent

bl_info = {
    "name": "Mcblend",
    "author": "Aspirata",
    "version": (0, 5, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Addons Tab",
    "description": "A useful tool for creating minecraft content in blender",
}

@persistent
def load_post_handler(dummy):
    InitOnStart()

class AbsoluteSolver(Operator):
    bl_label = "Absolute Solver"
    bl_idname = "wm.absolute_solver"
    bl_options = {'REGISTER', 'UNDO'}

    Error_Code: bpy.props.StringProperty()
    Error_Name: bpy.props.StringProperty()
    Description: bpy.props.StringProperty()
    Tech_Things: bpy.props.StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=600)
    
    def draw(self, context):
        layout = self.layout
            
        box = layout.box()
        sbox = box.box()
        if self.Error_Code != "None":
            row = sbox.row()
            row.label(text=f"Error Code: {self.Error_Code}")
        
        row = sbox.row()
        row.label(text=f"Error Name: {self.Error_Name}")

        sbox = box.box()
        row = sbox.row()
        row.label(text=f"Description: {self.Description}")

        if self.Tech_Things != "None":
            sbox = box.box()
            row = sbox.row()
            row.label(text="Tech Things:")

            split_tech_things = re.split(r'  |: ', self.Tech_Things)
            for part in split_tech_things:
                sbox.label(text=part)

            print(f"\033[33mAbsolute Solver Error Report: \033[31m\n{self.Tech_Things}\033[0m")
            sbox = box.box()
            row = sbox.row()
            row.operator("object.open_console")
    
    def execute(self, context):
        return {'FINISHED'}

# World & Materials

class RecreateEnvironment(Operator):
    bl_label = "Recreate Environment"
    bl_idname = "wm.recreate_env"
    bl_options = {'REGISTER', 'UNDO'}
    
    reset_settings: BoolProperty(
        name="Reset Settings",
        description="Resets the settings",
        default=False
    )

    create_sky: EnumProperty(
        items=[('None', 'None', ''),
            ('Create Sky', 'Create Sky', 'Reuses Already Imported Sky Material'), 
            ('Recreate Sky', 'Recreate Sky', 'Reappends Sky Material')],
        name="create_sky",
        default='None'
    )
    
    create_clouds: EnumProperty(
        items=[('None', 'None', ''),
            ('Create Clouds', 'Create Clouds', ''), 
            ('Recreate Clouds', 'Recreate Clouds', '')],
        name="create_clouds",
        default='None'
    )

    def execute(self, context):

        Materials.create_env(self)

        return {'FINISHED'}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=560)
    
    def draw(self, context):
        layout = self.layout
        
        if Preferences.enable_warnings:
            box = layout.box()
            row = box.row()
            row.label(text="WARNING !", icon='ERROR')
            row = box.row()
            row.label(text="This option should be used with caution")
            
        box = layout.box()
        row = box.row()

        if world != None:
            for node in world.node_tree.nodes:
                if node.type == 'GROUP':
                    if "Mcblend Sky" in node.node_tree.name:
                        row.prop(self, "reset_settings")
                        row = box.row()

        row.prop(self, "create_sky", text='create_sky', expand=True)
        row = box.row()
        row.prop(self, "create_clouds", text='create_clouds', expand=True)


class WorldAndMaterialsPanel(Panel):
    bl_label = "World & Materials"
    bl_idname = "OBJECT_PT_fix_materials"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):
        layout = self.layout

        global Preferences
        Preferences = bpy.context.preferences.addons[__package__].preferences

        global scene
        scene = bpy.context.scene

        global WProperties
        WProperties = scene.world_properties

        global world
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

        # Fix World

        sbox = box.box()
        row = sbox.row()
        row.label(text="Fix World", icon="WORLD_DATA")
        row = sbox.row()
        row.prop(WProperties, "backface_culling")
        row = sbox.row()
        row.prop(WProperties, "delete_useless_textures")
        row = sbox.row()
        row.label(text="Emissive Blocks Detection Method:", icon="LIGHT")
        row = sbox.row()
        row.prop(WProperties, "emissiondetection", text='emissiondetection', expand=True)

        row = sbox.row()
        row.scale_y = Big_Button_Scale
        row.operator("object.fix_world", text="Fix World")

        # Resource Packs

        sbox = box.box()
        row = sbox.row()
        row.label(text="Resource Packs", icon="FILE_FOLDER")

        tbox = sbox.box()
        resource_packs = get_resource_packs(scene)
        for pack, pack_info in resource_packs.items():
            row = tbox.row()

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
        
        row = tbox.row()
        row.operator("resource_pack.update_default_pack", icon='NEWFOLDER')

        row = tbox.row()
        row.operator("resource_pack.add", icon='ADD')

        row = sbox.row()
        row.prop(scene.resource_properties, "use_n")

        row = sbox.row()
        row.prop(scene.resource_properties, "use_s")

        row = sbox.row()
        row.operator("resource_pack.apply", icon='CHECKMARK')

        # Sky

        node_group = None
        clouds_obj = None
        geonodes_modifier = None 

        if world != None and (any(node.name == "Mcblend Sky" for node in bpy.data.node_groups)):
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
                break

        box = layout.box()
        row = box.row()
        row.label(text="Environment", icon="OUTLINER_DATA_VOLUME")

        row = box.row()
        row.prop(scene.env_properties, "create_clouds", text="Create Clouds")
        if clouds_exists == True:
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
                

        row = box.row()
        row.prop(scene.env_properties, "create_sky", text="Create Sky")

        if node_group != None:
            row.prop(scene.env_properties, "sky_settings", toggle=True, icon=("TRIA_DOWN" if scene.env_properties.sky_settings else "TRIA_LEFT"), icon_only=True)
            try:
                if node_group.inputs["End"].default_value == False:
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

                        row = sbox.row()
                        row.label(text="Strength:", icon="LIGHT_SUN")
                        row.prop(scene.env_properties, "strength_settings", icon=("TRIA_DOWN" if scene.env_properties.strength_settings else "TRIA_LEFT"), icon_only=True)
                        if scene.env_properties.strength_settings:
                            tbox = sbox.box()
                            row = tbox.row()
                            row.prop(node_group.inputs["End Stars Strength"], "default_value", text="Stars Strength")
                            row = tbox.row()
                            row.prop(node_group.inputs["Camera Ambient Light Strength"], "default_value", text="Camera Ambient Light Strength")
                            row = tbox.row()
                            row.prop(node_group.inputs["Non-Camera Ambient Light Strength"], "default_value", text="Non-Camera Ambient Light Strength")

                        row = sbox.row()
                        row.label(text="Colors:", icon="IMAGE")
                        row.prop(scene.env_properties, "colors_settings", icon=("TRIA_DOWN" if scene.env_properties.colors_settings else "TRIA_LEFT"), icon_only=True)
                        if scene.env_properties.colors_settings:
                            tbox = sbox.box()
                            row = tbox.row()
                            row.prop(node_group.inputs["End Stars Color"], "default_value", text="Stars Color")

                        row = sbox.row()
                        row.label(text="Ambient Light Colors:", icon="IMAGE")
                        row.prop(scene.env_properties, "ambient_colors_settings", icon=("TRIA_DOWN" if scene.env_properties.ambient_colors_settings else "TRIA_LEFT"), icon_only=True)
                        if scene.env_properties.ambient_colors_settings:
                            for node in bpy.data.node_groups:
                                if node.name == "Mcblend End":
                                    tbox = sbox.box()
                                    
                                    for Node in node.nodes:
                                        if Node.type == "VALTORGB":
                                            row = tbox.row()
                                            row.label(text=f"{Node.name}:")
                                            for element in Node.color_ramp.elements:                                                    
                                                row.prop(element, "color", icon_only=True)
                        
                        row = sbox.row()
                        row.label(text="Star Rotation:", icon="DRIVER_ROTATIONAL_DIFFERENCE")
                        row.prop(scene.env_properties, "rotation_settings", icon=("TRIA_DOWN" if scene.env_properties.rotation_settings else "TRIA_LEFT"), icon_only=True)

                        if scene.env_properties.rotation_settings:
                            tbox = sbox.box()
                            row = tbox.row()
                            row.prop(node_group.inputs["End Stars Rotation"], "default_value", index=0, text="X")
                            row = tbox.row()
                            row.prop(node_group.inputs["End Stars Rotation"], "default_value", index=1, text="Y")
                            row = tbox.row()
                            row.prop(node_group.inputs["End Stars Rotation"], "default_value", index=2, text="Z")
                        
                        row = sbox.row()
                        row.label(text="Other Settings:", icon="COLLAPSEMENU")
                        row.prop(scene.env_properties, "other_settings", icon=("TRIA_DOWN" if scene.env_properties.other_settings else "TRIA_LEFT"), icon_only=True)

                        if scene.env_properties.other_settings:
                            tbox = sbox.box()
                            row = tbox.row()
                            row.prop(node_group.inputs["Pixelated Stars"], "default_value", text="Pixelated Stars", toggle=True)


            except Exception as Error:
                row = box.row()
                row.label(text="Unknown Error Printed in Console. Report To Aspirata", icon="ERROR")
                row = box.row()
                row.label(text="To Open Console Press Window > Toggle System Console")
                print(Error)

        if clouds_exists == True or sky_exists == True:
            row = box.row()
            row.scale_y = Big_Button_Scale
            row.operator("object.create_env", text="Recreate Environment", icon="FILE_REFRESH")

        if clouds_exists == False and sky_exists == False:
            row = box.row()
            row.scale_y = Big_Button_Scale
            row.operator("object.create_env")
        
        # Materials
            
        box = layout.box()
        row = box.row()
        row.label(text="Materials", icon="MATERIAL_DATA")

        row = box.row()
        row.operator("object.upgrade_materials", text="Upgrade Materials")

        row = box.row()
        row.operator("object.fix_materials", text="Fix Materials")

        row = box.row()
        row.operator("wm.swap_textures", icon="UV_SYNC_SELECT")
        
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
                row.label(text=Translate("Bump Settings:"), icon="MODIFIER")

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

        
        row = box.row()
        row.prop(scene.ppbr_properties, "make_better_emission", text="Make Better Emission")

        row = box.row()
        row.prop(scene.ppbr_properties, "animate_textures", text="Animate Textures")

        row = box.row()
        row.prop(scene.ppbr_properties, "advanced_settings", toggle=True, text="Advanced Settings", icon=("TRIA_DOWN" if scene.ppbr_properties.advanced_settings else "TRIA_RIGHT"))
        if scene.ppbr_properties.advanced_settings:
            sbox = box.box()
            row = sbox.row()
            row.prop(context.scene.ppbr_properties, "change_bsdf", text="Change BSDF Settings")
            row.prop(scene.ppbr_properties, "change_bsdf_settings", icon=("TRIA_DOWN" if scene.ppbr_properties.change_bsdf_settings else "TRIA_LEFT"), icon_only=True)
            if  scene.ppbr_properties.change_bsdf_settings:
                tbox = sbox.box()
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
        row.operator("object.setproceduralpbr", text="Set Procedural PBR")

class FixWorldOperator(Operator):
    bl_idname = "object.fix_world"
    bl_label = "Fix World"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.fix_world()
        return {'FINISHED'}
    
class ResourcePackToggleOperator(bpy.types.Operator):
    bl_idname = "resource_pack.toggle"
    bl_label = "Toggle Resource Pack"
    bl_options = {'REGISTER', 'UNDO'}

    pack_name: bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene
        resource_packs = get_resource_packs(scene)
        if self.pack_name in resource_packs:
            resource_packs[self.pack_name]["enabled"] = not resource_packs[self.pack_name]["enabled"]
            set_resource_packs(scene, resource_packs)
        return {'FINISHED'}

class MoveResourcePackUp(Operator):
    bl_idname = "resource_pack.move_up"
    bl_label = "Move Resource Pack Up"
    bl_options = {'REGISTER', 'UNDO'}

    pack_name: bpy.props.StringProperty()

    def execute(self, context):
        resource_packs = get_resource_packs(context.scene)
        keys = list(resource_packs.keys())
        idx = keys.index(self.pack_name)
        if idx > 0:
            keys[idx], keys[idx - 1] = keys[idx - 1], keys[idx]
            reordered_packs = {k: resource_packs[k] for k in keys}
            set_resource_packs(context.scene, reordered_packs)
        return {'FINISHED'}

class MoveResourcePackDown(Operator):
    bl_idname = "resource_pack.move_down"
    bl_label = "Move Resource Pack Down"
    bl_options = {'REGISTER', 'UNDO'}

    pack_name: bpy.props.StringProperty()

    def execute(self, context):
        resource_packs = get_resource_packs(context.scene)
        keys = list(resource_packs.keys())
        idx = keys.index(self.pack_name)
        if idx < len(keys) - 1:
            keys[idx], keys[idx + 1] = keys[idx + 1], keys[idx]
            reordered_packs = {k: resource_packs[k] for k in keys}
            set_resource_packs(context.scene, reordered_packs)
        return {'FINISHED'}

class RemoveResourcePack(Operator):
    bl_idname = "resource_pack.remove"
    bl_label = "Remove Resource Pack"
    bl_options = {'REGISTER', 'UNDO'}

    pack_name: bpy.props.StringProperty()

    def execute(self, context):
        resource_packs = get_resource_packs(context.scene)
        if self.pack_name in resource_packs:
            del resource_packs[self.pack_name]
            set_resource_packs(context.scene, resource_packs)
        return {'FINISHED'}

class UpdateDefaultPack(Operator):
    bl_idname = "resource_pack.update_default_pack"
    bl_label = "Update Default Pack"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        update_default_pack(context.scene, True)
        return {'FINISHED'}

class AddResourcePack(Operator):
    bl_idname = "resource_pack.add"
    bl_label = "Add Resource Pack"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        scene = context.scene
        resource_packs = get_resource_packs(scene)

        if os.path.isdir(self.filepath) or self.filepath.endswith('.zip'):
            pack_name = os.path.basename(self.filepath)
            resource_packs[pack_name] = {"path": os.path.abspath(self.filepath), "enabled": True}
        else:
            pack_name = os.path.basename(os.path.dirname(self.filepath))
            resource_packs[pack_name] = {"path": os.path.dirname(self.filepath), "enabled": True}
        
        set_resource_packs(scene, resource_packs)

        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class ApplyResourcePack(Operator):
    bl_idname = "resource_pack.apply"
    bl_label = "Apply Resource Packs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.apply_resources()
        return {'FINISHED'}

class CreateEnvOperator(Operator):
    bl_idname = "object.create_env"
    bl_label = "Create Environment"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.create_env()
        return {'FINISHED'}
        
class UpgradeMaterialsOperator(Operator):
    bl_idname = "object.upgrade_materials"
    bl_label = "Upgrade Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.upgrade_materials()
        return {'FINISHED'}

class FixMaterialsOperator(Operator):
    bl_idname = "object.fix_materials"
    bl_label = "Fix Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.fix_materials()
        return {'FINISHED'}
    
class SwapTexturesOperator(Operator):
    bl_idname = "wm.swap_textures"
    bl_label = "Swap Textures"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        if os.path.isdir(self.filepath) or self.filepath.endswith('.zip'):
            #context.scene.materials_properties.folder_path = os.path.abspath(self.filepath)
            Materials.swap_textures(os.path.abspath(self.filepath))
            self.report({'INFO'}, f"Selected Folder: {os.path.abspath(self.filepath)}")
        else:
            #context.scene.materials_properties.folder_path = os.path.dirname(self.filepath)
            Materials.swap_textures(os.path.dirname(self.filepath))
            self.report({'INFO'}, f"Selected Folder: {os.path.dirname(self.filepath)}")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class OpenConsoleOperator(Operator):
    bl_idname = "object.open_console"
    bl_label = "Open Console"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            bpy.ops.wm.console_toggle()
        except RuntimeError:
            pass
        return {'FINISHED'}
    
class SetProceduralPBROperator(Operator):
    bl_idname = "object.setproceduralpbr"
    bl_label = "Set Procedural PBR"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.setproceduralpbr()
        return {'FINISHED'}
#

# Optimization

class OptimizationPanel(Panel):
    bl_label = "Optimization"
    bl_idname = "OBJECT_PT_optimization"
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
        if bpy.context.scene.optimizationproperties.camera_culling_settings == True:
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
                    
                if bpy.context.scene.optimizationproperties.merge_by_distance == True:
                    row = tbox.row()
                    row.prop(bpy.context.scene.optimizationproperties, "merge_distance", text="Merge Distance")

                row = tbox.row()
                row.prop(bpy.context.scene.optimizationproperties, "backface_culling", text="Backface Culling")

                if bpy.context.scene.optimizationproperties.backface_culling == True:
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
        row.operator("object.optimization", text="Optimize")

class OptimizeOperator(Operator):
    bl_idname = "object.optimization"
    bl_label = "Optimize"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Optimize.Optimize()
        return {'FINISHED'}
#
    
# Utils

class UtilsPanel(Panel):
    bl_label = "Utils"
    bl_idname = "OBJECT_PT_utils"
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
        row.operator("object.setrendersettings")

        box = layout.box()
        row = box.row()
        row.label(text="Materials", icon="MATERIAL")

        row = box.row()
        row.scale_x = 1.3
        row.prop(bpy.context.scene.utilsproperties, "enchant_settings", toggle=True, icon=("TRIA_DOWN" if bpy.context.scene.utilsproperties.enchant_settings else "TRIA_RIGHT"), icon_only=True)
        row.scale_y = Big_Button_Scale
        row.operator("object.enchant", text="Enchant Objects")

        if bpy.context.scene.utilsproperties.enchant_settings == True:
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
        row.operator("object.assingvertexgroup")


class SetRenderSettingsOperator(Operator):
    bl_idname = "object.setrendersettings"
    bl_label = "Set Render Settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        current_preset = bpy.context.scene.utilsproperties.current_preset
        SetRenderSettings(current_preset)
        return {'FINISHED'}
    
class EnchantOperator(Operator):
    bl_idname = "object.enchant"
    bl_label = "Enchant Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Enchant()
        return {'FINISHED'}
    
class AssingVertexGroupOperator(Operator):
    bl_idname = "object.assingvertexgroup"
    bl_label = "Assing Vertex Group"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        VertexRiggingTool()
        return {'FINISHED'}

# Assets
class AssetPanel(Panel):
    bl_label = "Assets"
    bl_idname = "OBJECT_PT_assets"
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
        row.label(text="Asset Category:")
        row = box.row()
        row.prop(context.scene.assetsproperties, "asset_category", text="")

        box.template_list("Assets_List_UL_", "", context.scene.assetsproperties, "asset_items", bpy.context.scene.assetsproperties, "asset_index")

        row = box.row()
        row.operator("object.update_assets", text="Manually Update Assets List")

        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("object.import_asset", text="Import Asset")

class Assets_List_UL_(bpy.types.UIList):

    def get_custom_icon(self, item):
        for category, assets in Assets.items():
            if item.name in assets:
                asset_type = category

                if asset_type == "Rigs":
                    return "ARMATURE_DATA"
                
                if asset_type == "Scripts":
                    return "FILE_SCRIPT"
                
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

class ImportAssetOperator(Operator):
    bl_idname = "object.import_asset"
    bl_label = "Import Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        current_index = bpy.context.scene.assetsproperties.asset_index
        index = 0
        found = False
        for category, assets in Assets.items():
            for key in assets.keys():
                if current_index == index:
                    append_asset(key, category)
                    found = True
                    break
                index += 1
            if found:
                break
        
        return {'FINISHED'}
    
class ManualAssetsUpdateOperator(Operator):
    bl_idname = "object.update_assets"
    bl_label = "Update Assets"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        update_assets()
        return {'FINISHED'}
#

classes = [McblendPreferences, AbsoluteSolver, RecreateEnvironment, 
    WorldProperties, MaterialsProperties, ResourcePackProperties, CreateEnvProperties, PPBRProperties,
    WorldAndMaterialsPanel, CreateEnvOperator, FixWorldOperator, OpenConsoleOperator, SetProceduralPBROperator, FixMaterialsOperator, UpgradeMaterialsOperator, SwapTexturesOperator, 
    ResourcePackToggleOperator, MoveResourcePackUp, MoveResourcePackDown, RemoveResourcePack, UpdateDefaultPack, AddResourcePack, ApplyResourcePack,
    OptimizationProperties, OptimizationPanel, OptimizeOperator, 
    UtilsProperties, UtilsPanel, SetRenderSettingsOperator, EnchantOperator, AssingVertexGroupOperator, 
    AssetsProperties, AssetPanel, Assets_List_UL_, ImportAssetOperator, ManualAssetsUpdateOperator
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.world_properties = bpy.props.PointerProperty(type=WorldProperties)
    bpy.types.Scene.resource_properties = bpy.props.PointerProperty(type=ResourcePackProperties)
    bpy.types.Scene.materials_properties = bpy.props.PointerProperty(type=MaterialsProperties)
    bpy.types.Scene.env_properties = bpy.props.PointerProperty(type=CreateEnvProperties)
    bpy.types.Scene.ppbr_properties = bpy.props.PointerProperty(type=PPBRProperties)
    bpy.types.Scene.optimizationproperties = bpy.props.PointerProperty(type=OptimizationProperties)
    bpy.types.Scene.utilsproperties = bpy.props.PointerProperty(type=UtilsProperties)
    bpy.types.Scene.assetsproperties = bpy.props.PointerProperty(type=AssetsProperties)

    bpy.app.handlers.load_post.append(load_post_handler)

def unregister():
    del bpy.types.Scene.world_properties
    del bpy.types.Scene.resource_properties
    del bpy.types.Scene.materials_properties
    del bpy.types.Scene.env_properties
    del bpy.types.Scene.ppbr_properties
    del bpy.types.Scene.optimizationproperties
    del bpy.types.Scene.utilsproperties
    del bpy.types.Scene.assetsproperties

    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    bpy.app.handlers.load_post.remove(load_post_handler)


if __name__ == "__main__":
    register()

# TODO:
    # - World & Materials - Сделать ветер