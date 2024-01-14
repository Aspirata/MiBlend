import bpy
import os
from .Data import *
from bpy.types import Panel, Operator
from .Materials import Materials
from .Optimization import Optimize

bl_info = {
    "name": "Mcblend",
    "author": "Aspirata",
    "version": (0, 0, 1),
    "blender": (4, 0, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}
# World & Materials

class BumpBool(bpy.types.PropertyGroup):
    use_bump: bpy.props.BoolProperty(
        name="Use Bump",
        default=False,
        description="Enables Bump In Materials"
    )

class WorldAndMaterialsPanel(bpy.types.Panel):
    bl_label = "World & Materials"
    bl_idname = "OBJECT_PT_fix_materials"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        box = layout.box()
        row = box.row()
        row.label(text="World", icon="WORLD_DATA")
        row = box.row()
        row.operator("object.fix_world", text="Fix World")
        
        box = layout.box()
        row = box.row()
        row.label(text="Sky", icon="OUTLINER_DATA_VOLUME")
        row = box.row()
        row.operator("object.create_sky", text="Create Sky")
        
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
        row.prop(context.scene.bump, "use_bump", text="Use Bump")
        row = box.row()
        row.operator("object.setproceduralpbr", text="Set Procedural PBR")

class FixWorldOperator(bpy.types.Operator):
    bl_idname = "object.fix_world"
    bl_label = "Fix World"

    def execute(self, context):
        Materials.fix_world()
        return {'FINISHED'}
    
class CreateSkyOperator(bpy.types.Operator):
    bl_idname = "object.create_sky"
    bl_label = "Create Sky"

    def execute(self, context):
        Materials.create_sky()
        return {'FINISHED'}
        
class UpgradeMaterialsOperator(bpy.types.Operator):
    bl_idname = "object.upgrade_materials"
    bl_label = "Upgrade Materials"

    def execute(self, context):
        Materials.upgrade_materials()
        return {'FINISHED'}

class FixMaterialsOperator(bpy.types.Operator):
    bl_idname = "object.fix_materials"
    bl_label = "Fix Materials"

    def execute(self, context):
        Materials.fix_materials()
        return {'FINISHED'}
    
class SetProceduralPBROperator(bpy.types.Operator):
    bl_idname = "object.setproceduralpbr"
    bl_label = "Set Procedural PBR"

    def execute(self, context):
        Materials.setproceduralpbr()
        return {'FINISHED'}

#

# Optimization
class CameraCullingBool(bpy.types.PropertyGroup):
    use_camera_culling: bpy.props.BoolProperty(
        name="Use Camera Culling",
        default=True,
        description="Enables Camera Culling"
    )

class RenderSettingsBool(bpy.types.PropertyGroup):
    set_render_settings: bpy.props.BoolProperty(
        name="Set Render Settings",
        default=False,
        description=""
    )

class OptimizationPanel(bpy.types.Panel):
    bl_label = "Optimization"
    bl_idname = "OBJECT_PT_optimization"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.prop(context.scene.camera_culling, "use_camera_culling", text="Use Camera Culling")
        row = box.row()
        row.prop(context.scene.render_settings, "set_render_settings", text="Set Render Settings")
        row = box.row()
        row.operator("object.optimization", text="Optimize")

class OptimizeOperator(bpy.types.Operator):
    bl_idname = "object.optimization"
    bl_label = "Optimize"

    def execute(self, context):
        Optimize.Optimize()
        return {'FINISHED'}
#

# Assets
class AssetPanel(bpy.types.Panel):
    bl_label = "Assets"
    bl_idname = "OBJECT_PT_assets"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene, "selected_asset", text="Selected Asset:")
        row = layout.row()
        row.operator("object.import_asset", text="Import Asset")

class ImportAssetOperator(bpy.types.Operator):
    bl_idname = "object.import_asset"
    bl_label = "Import Asset"

    def execute(self, context):
        selected_asset_key = context.scene.selected_asset
        if selected_asset_key in Assets:
            append_asset(Assets[selected_asset_key])
        return {'FINISHED'}

def append_asset(asset_data):
    blend_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Assets", asset_data["Type"], asset_data[".blend_name"])
    collection_name = asset_data["Collection_name"]

    with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
        data_to.collections = [collection_name]

    for collection in data_to.collections:
        bpy.context.collection.children.link(collection)
#

classes = [BumpBool, WorldAndMaterialsPanel, CreateSkyOperator, FixWorldOperator, SetProceduralPBROperator, FixMaterialsOperator, UpgradeMaterialsOperator, CameraCullingBool, RenderSettingsBool, OptimizationPanel, OptimizeOperator, AssetPanel, ImportAssetOperator]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.bump = bpy.props.PointerProperty(type=BumpBool)
    bpy.types.Scene.camera_culling = bpy.props.PointerProperty(type=CameraCullingBool)
    bpy.types.Scene.render_settings = bpy.props.PointerProperty(type=RenderSettingsBool)
    bpy.types.Scene.selected_asset = bpy.props.EnumProperty(
        items=[(name, data["Name"], "") for name, data in Assets.items()],
        description="Select Asset to Import",
    )    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.bump
    del bpy.types.Scene.camera_culling
    del bpy.types.Scene.render_settings
    del bpy.types.Scene.selected_asset

if __name__ == "__main__":
    register()

# TODO
    # - Починить Set render settings
    # - Починить Create Sky
    # - Починить bump