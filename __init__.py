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

# Fix World

class BumpBool(bpy.types.PropertyGroup):
    use_bump: bpy.props.BoolProperty(
        name="Use Bump",
        default=False,
        description="Enables Bump In Materials"
    )

class WorldPanel(bpy.types.Panel):
    bl_label = "World"
    bl_idname = "OBJECT_PT_fix_world"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.operator("object.fix_world", text="Fix World")
        box = layout.box()
        row = box.row()
        row.label(text="Procedural PBR", icon="NODE_MATERIAL")
        row = box.row()
        row.prop(context.scene.bump, "use_bump", text="Use Bump")
        row = box.row()
        row.operator("object.setproceduralpbr", text="Set Procedural PBR")
        row = box.row()
        #row.label(text="Sky", icon="OUTLINER_DATA_VOLUME")
        #row = box.row()

class FixWorldOperator(bpy.types.Operator):
    bl_idname = "object.fix_world"
    bl_label = "Fix World"

    def execute(self, context):
        Materials.fix_world()
        return {'FINISHED'}
    
class SetProceduralPBROperator(bpy.types.Operator):
    bl_idname = "object.setproceduralpbr"
    bl_label = "Set Procedural PBR"

    def execute(self, context):
        Materials.setproceduralpbr()
        return {'FINISHED'}
#
    
# Swap Texture-pack

#

# Fix Materials
class FixMaterialsPanel(bpy.types.Panel):
    bl_label = "Materials"
    bl_idname = "OBJECT_PT_fix_materials"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        row = box.row()
        row.operator("object.upgrade_materials", text="Upgrade Materials")
        row = box.row()
        row.operator("object.fix_materials", text="Fix Materials")
        
class FixMaterialsOperator(bpy.types.Operator):
    bl_idname = "object.fix_materials"
    bl_label = "Fix Materials"

    def execute(self, context):
        Materials.fix_materials()
        return {'FINISHED'}
    
class UpgradeMaterialsOperator(bpy.types.Operator):
    bl_idname = "object.upgrade_materials"
    bl_label = "Upgrade Materials"

    def execute(self, context):
        Materials.upgrade_materials()
        return {'FINISHED'}
#

# Optimization
class CameraCullingBool(bpy.types.PropertyGroup):
    use_camera_culling: bpy.props.BoolProperty(
        name="Use Camera Culling",
        default=True,
        description="Enables Camera Culling"
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

        layout.prop(context.scene, "selected_rig", text="Selected Rig:")
        row = layout.row()
        row.operator("object.import_asset", text="Import Asset")

class ImportAssetOperator(bpy.types.Operator):
    bl_idname = "object.import_asset"
    bl_label = "Import Asset"

    def execute(self, context):
        selected_rig_key = context.scene.selected_rig
        if selected_rig_key in Rigs:
            append_rig(Rigs[selected_rig_key])
        return {'FINISHED'}

def append_rig(rig_data):
    blend_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Assets", "Rigs", rig_data[".blend_name"])
    collection_name = rig_data["Collection_name"]

    with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
        data_to.collections = [collection_name]

    for collection in data_to.collections:
        bpy.context.collection.children.link(collection)
#

classes = [WorldPanel, FixWorldOperator, SetProceduralPBROperator, FixMaterialsPanel, FixMaterialsOperator, UpgradeMaterialsOperator, OptimizationPanel, OptimizeOperator, AssetPanel, ImportAssetOperator]

def register():
    bpy.utils.register_class(BumpBool)
    bpy.utils.register_class(CameraCullingBool)
    bpy.types.Scene.bump = bpy.props.PointerProperty(type=BumpBool)
    bpy.types.Scene.camera_culling = bpy.props.PointerProperty(type=CameraCullingBool)
    bpy.types.Scene.selected_rig = bpy.props.EnumProperty(
        items=[(name, data["Name"], "") for name, data in Rigs.items()],
        description="Select Rig to Import",
    )
    for cls in classes:
        bpy.utils.register_class(cls)
        

def unregister():
    bpy.utils.unregister_class(BumpBool)
    bpy.utils.unregister_class(CameraCullingBool)
    del bpy.types.Scene.bump
    del bpy.types.Scene.camera_culling
    del bpy.types.Scene.selected_rig
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
