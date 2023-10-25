import bpy
import Mcblend.Materials

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

class UpgradeMaterialsPanel(bpy.types.Panel):
    bl_label = "Materials"
    bl_idname = "OBJECT_PT_upgrade_materials"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.upgrade_materials", text="Fix Materials")

class UpgradeMaterialsOperator(bpy.types.Operator):
    bl_idname = "object.upgrade_materials"
    bl_label = "Upgrade Materials"

    def execute(self, context):
        Materials.fix_materials()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(UpgradeMaterialsPanel)
    bpy.utils.register_class(UpgradeMaterialsOperator)

def unregister():
    bpy.utils.unregister_class(UpgradeMaterialsPanel)
    bpy.utils.unregister_class(UpgradeMaterialsOperator)

if __name__ == "__main__":
    register()