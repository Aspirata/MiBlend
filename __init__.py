from email.policy import default
from .Data import *
from bpy.types import Panel, Operator
from .Materials import Materials
from .Optimization import Optimize
from .Utils import *

bl_info = {
    "name": "Mcblend",
    "author": "Aspirata",
    "version": (0, 4, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Addons Tab",
    "description": "A useful tool for creating minecraft content in blender",
}

# World & Materials

class RecreateSky(Operator):
    bl_label = "Recreate Sky"
    bl_idname = "wm.recreate_sky"
    
    reset_settings: BoolProperty(
        name="Reset Settings",
        description="Resets the settings",
        default=True
    )
    
    reappend_material: BoolProperty(
        name="Reappend Material",
        description="Reappends Material",
        default=False
    )

    recreate_clouds: BoolProperty(
        name="Recreate Clouds",
        default=True,
        description=""
    )

    def execute(self, context):

        node_tree_name = "Clouds Generator 2"

        world = bpy.context.scene.world
        world_material_name = "Mcblend World"
        
        if self.reappend_material == True:

            if bpy.context.scene.world == bpy.data.worlds.get(world_material_name):
                bpy.data.worlds.remove(bpy.data.worlds.get(world_material_name))

            try:
                with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                    data_to.worlds = [world_material_name]
                appended_world_material = bpy.data.worlds.get(world_material_name)
            except:
                CEH('004')

            bpy.context.scene.world = appended_world_material
        
        if self.reset_settings == True:
            world_material = bpy.context.scene.world.node_tree
            node_group = None

            for node in world_material.nodes:
                if node.type == 'GROUP' and "Mcblend Sky" in node.node_tree.name:
                    node_group = node
                    break
            if node_group != None:
                node_group.inputs["Moon Strenght"].default_value = 200.0
                node_group.inputs["Sun Strength"].default_value = 200.0
                node_group.inputs["Stars Strength"].default_value = 800.0
                node_group.inputs["Non-Camera Ambient Light Strenght"].default_value = 1.0
                node_group.inputs["Camera Ambient Light Strenght"].default_value = 1.0
                node_group.inputs["Rotation"].default_value = 0
            else:
                CEH('m005')

        if self.recreate_clouds == True:
            for obj in bpy.context.scene.objects:
                if obj.name == "Clouds":
                    bpy.data.objects.remove(obj, do_unlink=True)

            if node_tree_name not in bpy.data.node_groups:
                with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator.blend"), link=False) as (data_from, data_to):
                    data_to.node_groups = [node_tree_name]
            else:
                bpy.data.node_groups[node_tree_name]

            bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
            bpy.context.object.name = "Clouds"
            bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
            geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
            geonodes_modifier.node_group = bpy.data.node_groups.get(node_tree_name)
            geonodes_modifier["Socket_11"] = bpy.context.scene.camera

            bpy.context.view_layer.update()

        return {'FINISHED'}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=560)
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        row = box.row()
        row.label(text="WARNING !", icon='ERROR')
        row = box.row()
        row.label(text="This option should be used only if something is broken, as this option can reset world material and it's settings")
        box = layout.box()
        box.prop(self, "reset_settings")
        box.prop(self, "reappend_material")
        box.prop(self, "recreate_clouds")


class PPBRProperties(bpy.types.PropertyGroup):

    backface_culling: BoolProperty(
        name="Backface Culling",
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

    use_bump: BoolProperty(
        name="Use Bump",
        default=False,
        description="Enables Bump In Materials"
    )

    bump_strenght: FloatProperty(
        name="Bump Strenght",
        default=0.4,
        min=0.0,
        max=1.0,
        description=""
    )

    make_metal: BoolProperty(
        name="Make Metal",
        default=True,
        description="Enambles PBR For Metallic Materials"
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

    change_bsdf_settings: BoolProperty(
        name="Change BSDF Settings",
        default=True,
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

class CreateSkyProperties(bpy.types.PropertyGroup):

    advanced_settings: BoolProperty(
        name="Advanced Settings",
        default=False,
        description=""
    )

    create_clouds: BoolProperty(
        name="Create Clouds",
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
        world = bpy.context.scene.world
        scene = bpy.context.scene

        # World
        box = layout.box()
        row = box.row()
        row.label(text="World", icon="WORLD_DATA")
        row = box.row()
        row.prop(scene.ppbr_properties, "backface_culling", text="Backface Culling")
        row = box.row()
        row.prop(scene.ppbr_properties, "emissiondetection", text='emissiondetection', expand=True)
        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("object.fix_world", text="Fix World")

        # Sky
        box = layout.box()
        row = box.row()
        row.label(text="Sky", icon="OUTLINER_DATA_VOLUME")
        row = box.row()
        row.prop(scene.sky_properties, "create_clouds", text="Create Clouds")
        row = box.row()
        for obj in scene.objects:
            if obj.name != "Clouds":
                clouds_exists = False
            else:
                clouds_exists = True
                geonodes_modifier = obj.modifiers.get("Clouds Generator")
                break
            
        #if clouds_exists == True:
            #row.prop(geonodes_modifier, ['Socket_2'], "default_value", text="Layers Count", slider=True)

        #row = box.row()
        if world != bpy.data.worlds.get(world_material_name) or world == None:
            row.scale_y = Big_Button_Scale
            row.operator("object.create_sky", text="Create Sky")
        else:
            world_material = scene.world.node_tree
            node_group = None
            for node in world_material.nodes:
                if node.type == 'GROUP' and "Mcblend Sky" in node.node_tree.name:
                    node_group = node
                    break

            if node_group != None:
                row.prop(node_group.inputs["Rotation"], "default_value", text="Rotation")
                row = box.row()
                row.prop(scene.sky_properties, "advanced_settings", toggle=True, text="Advanced Settings", icon=("TRIA_DOWN" if scene.sky_properties.advanced_settings else "TRIA_RIGHT"))
                if scene.sky_properties.advanced_settings:
                    sbox = box.box()
                    row = sbox.row()
                    row.prop(node_group.inputs["Moon Strenght"], "default_value", text="Moon Strenght")
                    row = sbox.row()
                    row.prop(node_group.inputs["Sun Strength"], "default_value", text="Sun Strength")
                    row = sbox.row()
                    row.prop(node_group.inputs["Stars Strength"], "default_value", text="Stars Strength")
                    row = sbox.row()
                    row.prop(node_group.inputs["Non-Camera Ambient Light Strenght"], "default_value", text="Non-Camera Ambient Light Strenght")
                    row = sbox.row()
                    row.prop(node_group.inputs["Camera Ambient Light Strenght"], "default_value", text="Camera Ambient Light Strenght")
                    row = sbox.row()
                    row.prop(node_group.inputs["Pixelated Stars"], "default_value", text="Pixelated Stars", toggle=True)
            else:
                row.label(text="Mcblend Sky node not found, maybe you should recreate sky ?", icon="ERROR")
                row = box.row()
                row.label(text="Error code: m005")
                
            row = box.row()
            row.scale_y = Big_Button_Scale
            row.operator("object.create_sky", text="Recreate Sky")
        
        box = layout.box()
        row = box.row()
        row.label(text="Materials", icon="MATERIAL_DATA")
        row = box.row()
        row.operator("object.upgrade_materials", text="Upgrade Materials")
        row = box.row()
        row.operator("object.fix_materials", text="Fix Materials")
        
        box = layout.box()
        row = box.row()
        row.label(text="Procedural PBR", icon="NODE_MATERIAL")
        row = box.row()
        row.prop(scene.ppbr_properties, "use_bump", text="Use Bump")
        if scene.ppbr_properties.use_bump:
            row = box.row()
            row.prop(scene.ppbr_properties, "bump_strenght", slider=True, text="Bump Strength")
        row = box.row()
        row.prop(scene.ppbr_properties, "make_metal", text="Make Metal")
        row = box.row()
        row.prop(scene.ppbr_properties, "make_better_emission", text="Make Better Emission")
        row = box.row()
        row.prop(scene.ppbr_properties, "animate_textures", text="Animate Textures")
        row = box.row()
        row.prop(scene.ppbr_properties, "advanced_settings", toggle=True, text="Advanced Settings", icon=("TRIA_DOWN" if scene.ppbr_properties.advanced_settings else "TRIA_RIGHT"))
        if scene.ppbr_properties.advanced_settings:
            sbox = box.box()
            row = sbox.row()
            row.prop(context.scene.ppbr_properties, "change_bsdf_settings", text="Change BSDF Settings")
            if  scene.ppbr_properties.change_bsdf_settings:
                row = sbox.row()
                row.prop(scene.ppbr_properties, "specular", slider=True, text="Specular")
                row = sbox.row()
                row.prop(scene.ppbr_properties, "roughness", slider=True, text="Roughness")
                
        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("object.setproceduralpbr", text="Set Procedural PBR")

class FixWorldOperator(Operator):
    bl_idname = "object.fix_world"
    bl_label = "Fix World"

    def execute(self, context):
        Materials.fix_world()
        return {'FINISHED'}
    
class CreateSkyOperator(Operator):
    bl_idname = "object.create_sky"
    bl_label = "Create Sky"

    def execute(self, context):
        Materials.create_sky()
        return {'FINISHED'}
        
class UpgradeMaterialsOperator(Operator):
    bl_idname = "object.upgrade_materials"
    bl_label = "Upgrade Materials"

    def execute(self, context):
        Materials.upgrade_materials()
        return {'FINISHED'}

class FixMaterialsOperator(Operator):
    bl_idname = "object.fix_materials"
    bl_label = "Fix Materials"

    def execute(self, context):
        Materials.fix_materials()
        return {'FINISHED'}
    
class SetProceduralPBROperator(Operator):
    bl_idname = "object.setproceduralpbr"
    bl_label = "Set Procedural PBR"

    def execute(self, context):
        Materials.setproceduralpbr()
        return {'FINISHED'}

#

# Optimization
class OptimizationProperties(bpy.types.PropertyGroup):

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

    set_render_settings: BoolProperty(
        name="Set Render Settings",
        default=False,
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

        box = layout.box()
        row = box.row()
        row.prop(bpy.context.scene.optimizationproperties, "use_camera_culling", text="Use Camera Culling")
        if bpy.context.scene.optimizationproperties.use_camera_culling == True:
            row = box.row()
            row.prop(bpy.context.scene.optimizationproperties, "camera_culling_settings", text="Camera Culling Settings", icon=("TRIA_DOWN" if bpy.context.scene.optimizationproperties.camera_culling_settings else "TRIA_RIGHT"))

            # Camera Culling Settings
            if bpy.context.scene.optimizationproperties.camera_culling_settings == True:
                sbox = box.box()
                row = sbox.row()
                row.label(text="Camera Culling Type:", icon="CAMERA_DATA")
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
        row.prop(bpy.context.scene.optimizationproperties, "set_render_settings", text="Set Render Settings")
        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("object.optimization", text="Optimize")

class OptimizeOperator(Operator):
    bl_idname = "object.optimization"
    bl_label = "Optimize"

    def execute(self, context):
        Optimize.Optimize()
        return {'FINISHED'}
#
    
# Utils

class UtilsProperties(bpy.types.PropertyGroup):

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

        box = layout.box()
        row = box.row()
        row.label(text="Rendering", icon="RESTRICT_RENDER_OFF")
        if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
            
            row = box.row()
            row.prop(bpy.context.scene.utilsproperties, "cs_settings", toggle=True, text="Contact Shadows Settings", icon=("TRIA_DOWN" if bpy.context.scene.utilsproperties.cs_settings else "TRIA_RIGHT"))
            if bpy.context.scene.utilsproperties.cs_settings == True:
                sbox = box.box()
                row = sbox.row()
                row.label(text="Selection Mode:", icon="LIGHT_DATA")
                row = sbox.row()
                row.prop(bpy.context.scene.utilsproperties, "cshadowsselection", text='cshadowsselection', expand=True)
                row = sbox.row()
                row.prop(bpy.context.scene.utilsproperties, "distance")
                row = sbox.row()
                row.prop(bpy.context.scene.utilsproperties, "bias", slider=True)
                row = sbox.row()
                row.prop(bpy.context.scene.utilsproperties, "thickness", slider=True)
                
            row = box.row()
            row.scale_y = Big_Button_Scale
            row.operator("object.cshadows", text="Turn On Contact Shadows")
        
        row = box.row()
        row.operator("object.sleppafterrender", text="Sleep After Render")

        box = layout.box()
        row = box.row()
        row.label(text="Materials", icon="MATERIAL")
        row = box.row()
        row.operator("object.convertdbsdf2pbsdf", text="Convert DBSDF 2 PBSDF")
        row = box.row()
        row.prop(bpy.context.scene.utilsproperties, "enchant_settings", toggle=True, text="Enchant Settings", icon=("TRIA_DOWN" if bpy.context.scene.utilsproperties.enchant_settings else "TRIA_RIGHT"))
        if bpy.context.scene.utilsproperties.enchant_settings == True:
            sbox = box.box()
            row = sbox.row()
            row.prop(bpy.context.scene.utilsproperties, "divider")
            row = sbox.row()
            row.prop(bpy.context.scene.utilsproperties, "camera_strenght")
            row = sbox.row()
            row.prop(bpy.context.scene.utilsproperties, "non_camera_strenght")
        row = box.row()
        row.scale_y = Big_Button_Scale
        row.operator("object.enchant", text="Enchant Objects")

        box = layout.box()
        row = box.row()
        row.label(text="Mesh", icon="MESH_DATA")
        row = box.row()
        row.operator("object.fixautosmooth", text="Fix Shade Auto Smooth")

        box = layout.box()
        row = box.row()
        row.label(text="Rigging", icon="ARMATURE_DATA")
        row = box.row()
        row.prop(bpy.context.scene.utilsproperties, "vertex_group_name", text="Vertex Group Name")
        row = box.row()
        row.operator("object.assingvertexgroup", text="Assign Vertex Group")


class CShadowsOperator(Operator):
    bl_idname = "object.cshadows"
    bl_label = "Contact Shadows"

    def execute(self, context):
        UProperties = bpy.context.scene.utilsproperties
        CShadows(UProperties)
        return {'FINISHED'}
    
class SleepAfterRenderOperator(Operator):
    bl_idname = "object.sleppafterrender"
    bl_label = "Sleep After Render"

    def execute(self, context):
        sleep_detector()
        return {'FINISHED'}

class ConvertDBSDF2PBSDFOperator(Operator):
    bl_idname = "object.convertdbsdf2pbsdf"
    bl_label = "Convert DBSDF 2 PBSDF"

    def execute(self, context):
        ConvertDBSDF2PBSDF()
        return {'FINISHED'}
    
class EnchantOperator(Operator):
    bl_idname = "object.enchant"
    bl_label = "Enchant Object"

    def execute(self, context):
        Enchant()
        return {'FINISHED'}
    
class FixAutoSmoothOperator(Operator):
    bl_idname = "object.fixautosmooth"
    bl_label = "Fix Shade Auto Smooth"

    def execute(self, context):
        FixAutoSmooth()
        return {'FINISHED'}
    
class AssingVertexGroupOperator(Operator):
    bl_idname = "object.assingvertexgroup"
    bl_label = "Assing Vertex Group"

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

        box = layout.box()
        row = box.row()
        row.prop(context.scene, "selected_asset", text="Selected Asset:")
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

classes = [PPBRProperties, RecreateSky, CreateSkyProperties, WorldAndMaterialsPanel, CreateSkyOperator, FixWorldOperator, SetProceduralPBROperator, FixMaterialsOperator, UpgradeMaterialsOperator, OptimizationProperties, OptimizationPanel, OptimizeOperator, UtilsProperties, UtilsPanel, 
           CShadowsOperator, SleepAfterRenderOperator, ConvertDBSDF2PBSDFOperator, EnchantOperator, FixAutoSmoothOperator, AssingVertexGroupOperator, AssetPanel, ImportAssetOperator]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.sky_properties = bpy.props.PointerProperty(type=CreateSkyProperties)
    bpy.types.Scene.ppbr_properties = bpy.props.PointerProperty(type=PPBRProperties)
    bpy.types.Scene.optimizationproperties = bpy.props.PointerProperty(type=OptimizationProperties)
    bpy.types.Scene.utilsproperties = bpy.props.PointerProperty(type=UtilsProperties)
    bpy.types.Scene.selected_asset = bpy.props.EnumProperty(
        items=[(name, data["Name"], "") for name, data in Assets.items()],
        description="Select Asset to Import",
    )

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.sky_properties
    del bpy.types.Scene.ppbr_properties
    del bpy.types.Scene.optimizationproperties
    del bpy.types.Scene.utils_properties
    del bpy.types.Scene.selected_asset


if __name__ == "__main__":
    register()

# TODO:
    # - Utils - Сделать удалятор пустых фейсов
    # - World & Materials - Сделать ветер