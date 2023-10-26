import bpy
#from .Materials import Materials

bl_info = {
    "name": "Mcblend",
    "author": "Aspirata",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
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
        row.operator("object.fix_materials", text="Fix Materials")

class FixMaterialsOperator(bpy.types.Operator):
    bl_idname = "object.fix_materials"
    bl_label = "Fix Materials"

    def execute(self, context):
        Materials.fix_materials()
        return {'FINISHED'}
#

# Optimization
class OptimizationPanel(bpy.types.Panel):
    bl_label = "Optimization"
    bl_idname = "OBJECT_PT_optimization"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "use_optimization", text="Use Optimization")
        row = layout.row()
        row.operator("object.optimization", text="Optimize")

class OptimizeOperator(bpy.types.Operator):
    bl_idname = "object.optimization"
    bl_label = "Optimize"

    def execute(self, context):
        Optimize()
        return {'FINISHED'}
#

classes = [FixWorldPanel, FixWorldOperator, FixMaterialsPanel, FixMaterialsOperator, OptimizationPanel,OptimizeOperator]
def register():
    bpy.types.Scene.use_optimization = bpy.props.BoolProperty(
        name="Use Optimization",
        default=False,  # Установите значение по умолчанию
    )
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    del bpy.types.Scene.use_optimization
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()