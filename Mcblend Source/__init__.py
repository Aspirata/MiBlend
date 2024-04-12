from .Data import *
from .Materials import Materials
from .Optimization import Optimize
from .Utils import *
from .Translator import Translate
from .Preferences import *
from bpy.types import Panel, Operator

bl_info = {
    "name": "Mcblend",
    "author": "Aspirata",
    "version": (0, 4, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Addons Tab",
    "description": "A useful tool for creating minecraft content in blender",
}

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
        scene = bpy.context.scene
        world = scene.world
        
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

class FixWorldProperties(PropertyGroup):

    backface_culling: BoolProperty(
        name="Backface Culling",
        default=True,
        description=""
    )

    delete_useless_textures: BoolProperty(
        name="Delete Useless Textures",
        default=True,
        description=""
    )

    emissiondetection: EnumProperty(
        items=[('Automatic', 'Automatic', ''), 
            ('Automatic & Manual', 'Automatic & Manual', ''),
            ('Manual', 'Manual', '')],
        name="emissiondetection",
        default='Automatic & Manual'
    )

class PPBRProperties(PropertyGroup):

    use_normals: BoolProperty(
        name=Translate("Use Normals"),
        default=False,
        description="Enables Normals In Materials"
    )

    normals_selector: EnumProperty(
        items=[('Bump', 'Bump', ''), 
            ('Procedural Normals', 'Procedural Normals', '')],
        name="normals_selector",
        default='Bump'
    )

    normals_settings: BoolProperty(
        name=Translate("Normals Settings"),
        default=False,
        description=""
    )

    bump_strength: FloatProperty(
        name="Bump Strength",
        default=0.4,
        min=0.0,
        max=1.0,
        description=""
    )

    pnormals_size: FloatProperty(
        name="PNormals Size",
        default=2,
        min=0.0,
        max=16.0,
        description=""
    )

    pnormals_blur: FloatProperty(
        name="PNormals Blur",
        default=0,
        min=0.0,
        max=4.0,
        description=""
    )

    pnormals_strength: FloatProperty(
        name="PNormals Strength",
        default=1,
        min=-2.0,
        max=2.0,
        description=""
    )

    pnormals_exclude: FloatProperty(
        name="PNormals Exclude",
        default=0,
        min=0.0,
        max=1.0,
        description=""
    )

    pnormals_min: FloatProperty(
        name="PNormals Min",
        default=0,
        min=0.0,
        max=1.0,
        description=""
    )

    pnormals_max: FloatProperty(
        name="PNormals Max",
        default=1,
        min=0.0,
        max=1.0,
        description=""
    )

    pnormals_size_x_multiplier: FloatProperty(
        name="PNormals Size X Multiplier",
        default=1,
        min=-2.0,
        max=2.0,
        description=""
    )

    pnormals_size_y_multiplier: FloatProperty(
        name="PNormals Size Y Multiplier",
        default=1,
        min=-2.0,
        max=2.0,
        description=""
    )

    use_sss: BoolProperty(
        name=Translate("Use SSS"),
        default=True,
        description=""
    )

    sss_settings: BoolProperty(
        name=Translate("SSS Settings"),
        default=False,
        description=""
    )

    sss_type: EnumProperty(
        items=[('BURLEY', 'Christensen Burley', ''), 
            ('RANDOM_WALK', 'Random Walk', ''),
            ('RANDOM_WALK_SKIN', 'Random Walk (Skin)', '')],
        name="sss_type",
        default='BURLEY'
    )

    sss_weight: FloatProperty(
        name="SSS Weight",
        default=1,
        min=0.0,
        max=1.0,
        description=""
    )

    sss_scale: FloatProperty(
        name="SSS Scale",
        default=0.05,
        min=0.0,
        max=10.0,
        subtype='DISTANCE',
        description=""
    )

    make_metal: BoolProperty(
        name="Make Metal",
        default=True,
        description="Enambles PBR For Metallic Materials"
    )

    metal_settings: BoolProperty(
        name="Metal Settings",
        default=False,
        description=""
    )

    metal_metallic: FloatProperty(
        name="Metal Metallic",
        default=0.7,
        min=0.0,
        max=1.0,
        description=""
    )

    metal_roughness: FloatProperty(
        name="Metal Roughness",
        default=0.2,
        min=0.0,
        max=1.0,
        description=""
    )

    make_reflections: BoolProperty(
        name="Make Reflections",
        default=True,
        description="Enambles PBR For Reflective Materials"
    )

    reflections_settings: BoolProperty(
        name="Reflections Settings",
        default=False,
        description=""
    )

    reflections_roughness: FloatProperty(
        name="Reflections Roughness",
        default=0.1,
        min=0.0,
        max=1.0,
        description=""
    )

    make_better_emission: BoolProperty(
        name="Make Better Emission",
        default=True,
        description=""
    )

    animate_textures: BoolProperty(
        name="Animate textures",
        default=True,
        description=""
    )

    advanced_settings: BoolProperty(
        name="Advanced Settings",
        default=False,
        description=""
    )

    change_bsdf: BoolProperty(
        name="Change BSDF",
        default=True,
        description=""
    )

    change_bsdf_settings: BoolProperty(
        name="Change BSDF Settings",
        default=False,
        description=""
    )

    specular: FloatProperty(
        name="Specular",
        default=0.4,
        min=0.0,
        max=1.0,
        description=""
    )

    roughness: FloatProperty(
        name="Roughness",
        default=0.6,
        min=0.0,
        max=1.0,
        description=""
    )

class CreateEnvProperties(PropertyGroup):

    advanced_settings: BoolProperty(
        name="Advanced Settings",
        default=False,
        description=""
    )

    strength_settings: BoolProperty(
        name="Strength Settings",
        default=False,
        description=""
    )

    colors_settings: BoolProperty(
        name="Colors Settings",
        default=False,
        description=""
    )

    ambient_colors_settings: BoolProperty(
        name="Ambient Colors Settings",
        default=False,
        description=""
    )

    rotation_settings: BoolProperty(
        name="Rotation Settings",
        default=False,
        description=""
    )

    create_clouds: BoolProperty(
        name="Create Clouds",
        default=True,
        description=""
    )

    create_sky: BoolProperty(
        name="Create Sky",
        default=True,
        description=""
    )

class WorldAndMaterialsPanel(Panel):
    bl_label = "World & Materials"
    bl_idname = "OBJECT_PT_fix_materials"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):
        layout = self.layout
        try:
            Preferences = bpy.context.preferences.addons["Mcblend"].preferences
        except:
            Preferences = bpy.context.preferences.addons["Mcblend Source"].preferences
            
        scene = bpy.context.scene
        world = scene.world
        WProperties = scene.world_properties
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
        if WProperties.delete_useless_textures == True and Preferences.enable_warnings:
            row = box.row()
            row.label(text=Translate("Warning !"), icon="ERROR")
            row = box.row()
            row.label(text=Translate("This option should be turned on only if you didn't add any extra textures to the materials"))
            row = box.row()
            row.label(text=Translate("This option can delete your custom textures !"))
        
        row = box.row()
        row.prop(WProperties, "delete_useless_textures")
        row = box.row()
        row.label(text="Emissive Blocks Detection Method:", icon="LIGHT")
        row = box.row()
        row.prop(WProperties, "emissiondetection", text='emissiondetection', expand=True)
        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("object.fix_world", text="Fix World")

        # Sky
        
        box = layout.box()
        row = box.row()
        row.label(text="Environment", icon="OUTLINER_DATA_VOLUME")
        row = box.row()
        row.prop(scene.env_properties, "create_clouds", text="Create Clouds")
        row = box.row()
        row.prop(scene.env_properties, "create_sky", text="Create Sky")
        for obj in scene.objects:
            if obj.name != "Clouds":
                clouds_exists = False
            else:
                clouds_exists = True
                geonodes_modifier = obj.modifiers.get("Clouds Generator")
                break
            
        #if clouds_exists == True:
            #row.prop(geonodes_modifier, ['Socket_2'], "default_value", text="Layers Count", slider=True)

        if (any(node.name == clouds_node_tree_name for node in bpy.data.node_groups)):
            clouds_exists = True

        if world != None and (any(node.name == "Mcblend Sky" for node in bpy.data.node_groups)):
            if world_material_name in bpy.data.worlds:
                sky_exists = True

        if clouds_exists == False and sky_exists == False:
            row = box.row()
            row.scale_y = Big_Button_Scale
            row.operator("object.create_env")

        if sky_exists == True:
            world_material = scene.world.node_tree
            node_group = None
            for node in world_material.nodes:
                if node.type == 'GROUP':
                    if "Mcblend Sky" in node.node_tree.name:
                        node_group = node
                        break

            if node_group != None:
                try:
                    if node_group.inputs["End"].default_value == False:
                        row = box.row()
                        row.prop(node_group.inputs["Time"], "default_value", text="Time")
                        row = box.row()
                        row.prop(node_group.inputs["End"], "default_value", text="End", toggle=True)
                        row = box.row()
                        row.prop(scene.env_properties, "advanced_settings", toggle=True, text="Advanced Settings", icon=("TRIA_DOWN" if scene.env_properties.advanced_settings else "TRIA_RIGHT"))
                        if scene.env_properties.advanced_settings:
                            sbox = box.box()
                            row = sbox.row()
                            row.label(text="Strength:", icon="LIGHT_SUN")
                            row.prop(scene.env_properties, "strength_settings", icon=("TRIA_DOWN" if scene.env_properties.strength_settings else "TRIA_LEFT"), icon_only=True)
                            if scene.env_properties.strength_settings:
                                tbox = sbox.box()
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
                            
                            row = sbox.row()
                            row.label(text="Ambient Light Colors:", icon="IMAGE")
                            row.prop(scene.env_properties, "ambient_colors_settings", icon=("TRIA_DOWN" if scene.env_properties.ambient_colors_settings else "TRIA_LEFT"), icon_only=True)
                            if scene.env_properties.ambient_colors_settings:
                                for node in bpy.data.node_groups:
                                    if node.name == "Ambient Color":
                                        tbox = sbox.box()
                                        
                                        for Node in node.nodes:
                                            if Node.type == "VALTORGB":
                                                row = tbox.row()
                                                row.label(text=f"{Node.name}:")
                                                for element in Node.color_ramp.elements:                                                    
                                                    row.prop(element, "color", icon_only=True)
                            
                            row = sbox.row()
                            row.label(text="Colors:", icon="IMAGE")
                            row.prop(scene.env_properties, "colors_settings", icon=("TRIA_DOWN" if scene.env_properties.colors_settings else "TRIA_LEFT"), icon_only=True)

                            if scene.env_properties.colors_settings:
                                tbox = sbox.box()
                                row = tbox.row()
                                row.prop(node_group.inputs["Moon Color"], "default_value", text="Moon Color")
                                row = tbox.row()
                                row.prop(node_group.inputs["Sun Color"], "default_value", text="Sun Color")
                                row = tbox.row()
                                row.prop(node_group.inputs["Sun Color In Sunset"], "default_value", text="Sun Color In Sunset")
                                row = tbox.row()
                                row.prop(node_group.inputs["Stars Color"], "default_value", text="Stars Color")
                            
                            row = sbox.row()
                            row.label(text="Rotation:", icon="DRIVER_ROTATIONAL_DIFFERENCE")
                            row.prop(scene.env_properties, "rotation_settings", icon=("TRIA_DOWN" if scene.env_properties.rotation_settings else "TRIA_LEFT"), icon_only=True)

                            if scene.env_properties.rotation_settings:
                                tbox = sbox.box()
                                row = tbox.row()
                                row.prop(node_group.inputs["Rotation"], "default_value", index=0, text="X")
                                row = tbox.row()
                                row.prop(node_group.inputs["Rotation"], "default_value", index=1, text="Y")
                                row = tbox.row()
                                row.prop(node_group.inputs["Rotation"], "default_value", index=2, text="Z")

                            row = sbox.row()
                            row.prop(node_group.inputs["Pixelated Stars"], "default_value", text="Pixelated Stars", toggle=True)
                            row = sbox.row()
                            row.prop(node_group.inputs["Stars Amount"], "default_value", text="Stars Amount", slider=True) 
                    else:
                        row = box.row()
                        row.prop(node_group.inputs["Stars Amount"], "default_value", text="Stars Amount", slider=True)
                        row = box.row()
                        row.prop(node_group.inputs["End"], "default_value", text="End", toggle=True)
                        row = box.row()
                        row.prop(scene.env_properties, "advanced_settings", toggle=True, text="Advanced Settings", icon=("TRIA_DOWN" if scene.env_properties.advanced_settings else "TRIA_RIGHT"))
                        if scene.env_properties.advanced_settings:
                            sbox = box.box()
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

                            # Нада исправить это под мир энда, так как я просто скопировал эту часть с Overworld 
                            row = sbox.row()
                            row.label(text="Ambient Light Colors:", icon="IMAGE")
                            row.prop(scene.env_properties, "ambient_colors_settings", icon=("TRIA_DOWN" if scene.env_properties.ambient_colors_settings else "TRIA_LEFT"), icon_only=True)
                            if scene.env_properties.ambient_colors_settings:
                                for node in bpy.data.node_groups:
                                    if node.name == "End":
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
                            row.prop(node_group.inputs["Pixelated Stars"], "default_value", text="Pixelated Stars", toggle=True)


                except Exception as Error:
                    row = box.row()
                    row.label(text="Unknown Error Printed in Console. Report To Aspirata", icon="ERROR")
                    row = box.row()
                    row.label(text="To Open Console Press Window > Toggle System Console")
                    print(Error)

            else:
                row.label(text="Mcblend Sky node not found, maybe you should recreate sky ?", icon="ERROR")
                row = box.row()
                row.label(text="Error code: m005")

        if clouds_exists == True or sky_exists == True:
            row = box.row()
            row.scale_y = Big_Button_Scale
            row.operator("object.create_env", text="Recreate Environment")
        
        # Materials
            
        box = layout.box()
        row = box.row()
        row.label(text="Materials", icon="MATERIAL_DATA")
        row = box.row()
        row.operator("object.upgrade_materials", text="Upgrade Materials")
        row = box.row()
        row.operator("object.fix_materials", text="Fix Materials")
        
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
                row.prop(scene.ppbr_properties, "sss_weight", slider=True)
                row = tbox.row()
                row.prop(scene.ppbr_properties, "sss_scale", slider=True)

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
    
class SetProceduralPBROperator(Operator):
    bl_idname = "object.setproceduralpbr"
    bl_label = "Set Procedural PBR"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.setproceduralpbr()
        return {'FINISHED'}

#

# Optimization
class OptimizationProperties(PropertyGroup):

    camera_culling_type: EnumProperty(
        items=[('Vector', 'Vector', ''), ('Raycast', 'Raycast', '')],
        name="camera_culling_type",
        default='Raycast'
    )

    use_camera_culling: BoolProperty(
        name="Use Camera Culling",
        default=True,
        description="Enables Camera Culling"
    )

    camera_culling_settings: BoolProperty(
        name="Camera Culling Settings",
        default=False,
        description=""
    )

    predict_fov: BoolProperty(
        name="Predict FOV",
        default=False,
        description=""
    )

    merge_by_distance: BoolProperty(
        name="Merge By Distance",
        default=False,
        description=""
    )

    merge_distance: FloatProperty(
        name="Merge Distance",
        default=100.0,
        min=0.0,
        max=1000000.0,
        description=""
    )

    threshold: FloatProperty(
        name="Threshold",
        default=0.8,
        min=0.0,
        max=1.0,
        description=""
    )

    scale: FloatProperty(
        name="Scale",
        default=1,
        min=0.0,
        max=100.0,
        description=""
    )

    backface_culling: BoolProperty(
        name="Backface Culling",
        default=True,
        description=""
    )

    backface_culling_distance: FloatProperty(
        name="Backface Culling Distance",
        default=50.0,
        min=0.0,
        max=1000000.0,
        description=""
    )

class OptimizationPanel(Panel):
    bl_label = "Optimization"
    bl_idname = "OBJECT_PT_optimization"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):
        layout = self.layout
        try:
            Preferences = bpy.context.preferences.addons["Mcblend"].preferences
        except:
            Preferences = bpy.context.preferences.addons["Mcblend Source"].preferences

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
            row.label(text="Camera Culling Settings:", icon="CAMERA_DATA")
            row = sbox.row()
            row.prop(bpy.context.scene.optimizationproperties, "camera_culling_type", text='camera_culling_type', expand=True)
            if bpy.context.scene.optimizationproperties.camera_culling_type == 'Raycast':
                # Raycast Camera Culling Settings
                row = sbox.row()
                row.prop(bpy.context.scene.optimizationproperties, "predict_fov", text="Predict FOV")
                row = sbox.row()
                row.prop(bpy.context.scene.optimizationproperties, "merge_by_distance", text="Merge By Distance")
                    
                if bpy.context.scene.optimizationproperties.merge_by_distance == True:
                    row = sbox.row()
                    row.prop(bpy.context.scene.optimizationproperties, "merge_distance", text="Merge Distance")

                row = sbox.row()
                row.prop(bpy.context.scene.optimizationproperties, "backface_culling", text="Backface Culling")

                if bpy.context.scene.optimizationproperties.backface_culling == True:
                    row = sbox.row()
                    row.prop(bpy.context.scene.optimizationproperties, "backface_culling_distance", text="Backface Culling Distance")

                row = sbox.row()
                row.prop(bpy.context.scene.optimizationproperties, "scale")
            else:
                row = sbox.row()
                row.prop(bpy.context.scene.optimizationproperties, "backface_culling", text="Backface Culling")
                row = sbox.row()
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

class UtilsProperties(PropertyGroup):

    cs_settings: BoolProperty(
        name="Contact Shadows Settings",
        default=False,
        description=""
    )

    cshadowsselection: EnumProperty(
        items=[('All Light Sources', 'All Light Sources', ''), 
               ('Only Selected Light Sources', 'Only Selected Light Sources', '')],
        name="cshadowsselection",
        default='All Light Sources'
    )

    distance: FloatProperty(
        name="Distance",
        description="",
        default=0.2,
        min=0.0,
        max=100000.0
    )

    bias: FloatProperty(
        name="Bias",
        description="",
        default=0.03,
        min=0.001,
        max=5.0
    )

    thickness: FloatProperty(
        name="Thickness",
        description="",
        default=0.01,
        min=0.0,
        max=100.0
    )

    current_preset: EnumProperty(
        items=[(name, name, "") for name, data in Render_Settings.items()],
        description="Select Settings to Use",
    )

    enchant_settings: BoolProperty(
        name="Enchant Settings",
        default=False,
        description=""
    )

    divider: FloatProperty(
        name="Divider",
        description="",
        default=70.0,
        min=0.0,
        max=100000.0
    )

    camera_strenght: FloatProperty(
        name="Camera Strenght",
        description="",
        default=1.0,
        min=0.0,
        max=1000000.0
    )

    non_camera_strenght: FloatProperty(
        name="Non-Camera Strenght",
        description="",
        default=1.0,
        min=0.0,
        max=1000000.0
    )

    armature: bpy.props.PointerProperty(
        name="Armature",
        description="",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )

    lattice: bpy.props.PointerProperty(
        name="Lattice",
        description="",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'LATTICE'
    )

    vertex_group_name: StringProperty(
        name="Vertex Group Name",
        description=""
    )

class UtilsPanel(Panel):
    bl_label = "Utils"
    bl_idname = "OBJECT_PT_utils"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):
        layout = self.layout
        try:
            Preferences = bpy.context.preferences.addons["Mcblend"].preferences
        except:
            Preferences = bpy.context.preferences.addons["Mcblend Source"].preferences

        if Preferences.transparent_ui:
            self.bl_options = {'HIDE_HEADER'}
        else:
            self.bl_options = {'DEFAULT_CLOSED'}

        box = layout.box()
        row = box.row()
        row.label(text="Rendering", icon="RESTRICT_RENDER_OFF")
        row = box.row()
        if bpy.context.scene.render.engine != 'BLENDER_EEVEE' and Preferences.enable_warnings:
            row.label(text="Contact shadows exist only on eevee", icon="ERROR")
            row = box.row()

        row.scale_x = 1.3
        row.prop(bpy.context.scene.utilsproperties, "cs_settings", toggle=True, icon=("TRIA_DOWN" if bpy.context.scene.utilsproperties.cs_settings else "TRIA_RIGHT"), icon_only=True)
        row.scale_y = Big_Button_Scale
        row.operator("object.cshadows", text="Turn On Contact Shadows")
        if bpy.context.scene.utilsproperties.cs_settings == True:
            sbox = box.box()
            row = sbox.row()
            row.label(text="Contact Shadows Settings:", icon="LIGHT_DATA")
            row = sbox.row()
            row.prop(bpy.context.scene.utilsproperties, "cshadowsselection", text='cshadowsselection', expand=True)
            row = sbox.row()
            row.prop(bpy.context.scene.utilsproperties, "distance")
            row = sbox.row()
            row.prop(bpy.context.scene.utilsproperties, "bias", slider=True)
            row = sbox.row()
            row.prop(bpy.context.scene.utilsproperties, "thickness", slider=True)

        row = box.row()
        row.prop(bpy.context.scene.utilsproperties, "current_preset", text="Current Preset")
        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("object.setrendersettings")
        
        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("object.sleppafterrender", text="Sleep After Render")

        box = layout.box()
        row = box.row()
        row.label(text="Materials", icon="MATERIAL")
        row = box.row()
        row.operator("object.convertdbsdf2pbsdf", text="Convert DBSDF 2 PBSDF")
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
        row.label(text="Mesh", icon="MESH_DATA")
        row = box.row()
        row.operator("object.fixautosmooth", text="Fix Shade Auto Smooth")

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


class CShadowsOperator(Operator):
    bl_idname = "object.cshadows"
    bl_label = "Contact Shadows"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        UProperties = bpy.context.scene.utilsproperties
        CShadows(UProperties)
        return {'FINISHED'}
    
class SleepAfterRenderOperator(Operator):
    bl_idname = "object.sleppafterrender"
    bl_label = "Sleep After Render"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sleep_detector()
        return {'FINISHED'}

class SetRenderSettingsOperator(Operator):
    bl_idname = "object.setrendersettings"
    bl_label = "Set Render Settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        current_preset = bpy.context.scene.utilsproperties.current_preset
        SetRenderSettings(current_preset)
        return {'FINISHED'}

class ConvertDBSDF2PBSDFOperator(Operator):
    bl_idname = "object.convertdbsdf2pbsdf"
    bl_label = "Convert DBSDF 2 PBSDF"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ConvertDBSDF2PBSDF()
        return {'FINISHED'}
    
class EnchantOperator(Operator):
    bl_idname = "object.enchant"
    bl_label = "Enchant Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Enchant()
        return {'FINISHED'}
    
class FixAutoSmoothOperator(Operator):
    bl_idname = "object.fixautosmooth"
    bl_label = "Fix Shade Auto Smooth"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        FixAutoSmooth()
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
        try:
            Preferences = bpy.context.preferences.addons["Mcblend"].preferences
        except:
            Preferences = bpy.context.preferences.addons["Mcblend Source"].preferences

        if Preferences.transparent_ui:
            self.bl_options = {'HIDE_HEADER'}
        else:
            self.bl_options = {'DEFAULT_CLOSED'}

        box = layout.box()
        row = box.row()
        row.prop(context.scene, "selected_asset", text="Selected Asset")
        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("object.import_asset", text="Import Asset")

class ImportAssetOperator(Operator):
    bl_idname = "object.import_asset"
    bl_label = "Import Asset"
    

    def execute(self, context):
        selected_asset_key = context.scene.selected_asset
        if selected_asset_key in Assets:
            append_asset(Assets[selected_asset_key])
            context.view_layer.update()
        return {'FINISHED'}

def append_asset(asset_data):
    blend_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Assets", asset_data["Type"], asset_data[".blend_name"])
    collection_name = asset_data["Collection_name"]

    with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
        data_to.collections = [collection_name]

    for collection in data_to.collections:
        bpy.context.collection.children.link(collection)

#

classes = [McblendPreferences, RecreateEnvironment, FixWorldProperties, CreateEnvProperties, PPBRProperties, WorldAndMaterialsPanel, CreateEnvOperator, FixWorldOperator, SetProceduralPBROperator, FixMaterialsOperator, UpgradeMaterialsOperator, OptimizationProperties, OptimizationPanel, OptimizeOperator,
           UtilsProperties, UtilsPanel, CShadowsOperator, SleepAfterRenderOperator, SetRenderSettingsOperator, ConvertDBSDF2PBSDFOperator, EnchantOperator, FixAutoSmoothOperator, AssingVertexGroupOperator, AssetPanel, ImportAssetOperator]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.world_properties = bpy.props.PointerProperty(type=FixWorldProperties)
    bpy.types.Scene.env_properties = bpy.props.PointerProperty(type=CreateEnvProperties)
    bpy.types.Scene.ppbr_properties = bpy.props.PointerProperty(type=PPBRProperties)
    bpy.types.Scene.optimizationproperties = bpy.props.PointerProperty(type=OptimizationProperties)
    bpy.types.Scene.utilsproperties = bpy.props.PointerProperty(type=UtilsProperties)
    bpy.types.Scene.selected_asset = bpy.props.EnumProperty(
        items=[(name, data["Name"], "") for name, data in Assets.items()],
        description="Select Asset to Import",
    )

def unregister():

    del bpy.types.Scene.world_properties
    del bpy.types.Scene.env_properties
    del bpy.types.Scene.ppbr_properties
    del bpy.types.Scene.optimizationproperties
    del bpy.types.Scene.utilsproperties
    del bpy.types.Scene.selected_asset

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

# TODO:
    # - Utils - Сделать удалятор пустых фейсов
    # - World & Materials - Сделать ветер