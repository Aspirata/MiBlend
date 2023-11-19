import bpy
#import Materials
#import Optimize
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
class FixWorldPanel(bpy.types.Panel):
    bl_label = "World"
    bl_idname = "OBJECT_PT_fix_world"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.fix_world", text="Fix World")

class FixWorldOperator(bpy.types.Operator):
    bl_idname = "object.fix_world"
    bl_label = "Fix World"

    def execute(self, context):
        Materials.fix_world()
        return {'FINISHED'}
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
        
        row = layout.row()
        row.operator("object.upgrade_materials", text="Upgrade Materials")
        
        
        row = layout.row()
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
        name="Use Camea Culling",
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
        layout.prop(context.scene.mcblend, "use_camera_culling", text="Use Camera Culling")
        row = layout.row()
        row.operator("object.optimization", text="Optimize")

class OptimizeOperator(bpy.types.Operator):
    bl_idname = "object.optimization"
    bl_label = "Optimize"

    def execute(self, context):
        Optimize.Optimize()
        return {'FINISHED'}
#

classes = [FixWorldPanel, FixWorldOperator, FixMaterialsPanel, FixMaterialsOperator, UpgradeMaterialsOperator, OptimizationPanel, OptimizeOperator]

def register():
    bpy.utils.register_class(CameraCullingBool)
    bpy.types.Scene.mcblend = bpy.props.PointerProperty(type=CameraCullingBool)
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    del bpy.types.Scene.mcblend
    bpy.utils.unregister_class(BoolProperties)
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()