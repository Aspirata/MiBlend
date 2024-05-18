import bpy
import os
from bpy.types import Panel, Operator

Assets = {
    "SRE V2.0": {
        "Name": "SRE V2.0",
        "Type": "Rigs",
        "Blender Version": "4.x.x",
        ".blend_name": "Simple_edit_V2.0.blend",
        "Collection_name": "SRE rig"
    },

    "SRE V2.0b732": {
        "Name": "SRE V2.0b732",
        "Type": "Rigs",
        "Blender Version": "3.6.x",
        ".blend_name": "Simple_edit_V2.0b732.blend",
        "Collection_name": "SRE rig"
    },

    "Creeper": {
        "Name": "Creeper",
        "Type": "Rigs",
        "Blender Version": "4.x.x",
        ".blend_name": "Creeper.blend",
        "Collection_name": "Creeper"
    },

    "Allay": {
        "Name": "Allay Rig",
        "Type": "Rigs",
        "Blender Version": "4.x.x",
        ".blend_name": "Allay.blend",
        "Collection_name": "Simple Allay"
    },

    "Axolotl": {
        "Name": "Axolotl Rig",
        "Type": "Rigs",
        "Blender Version": "4.x.x",
        ".blend_name": "Axolotl.blend",
        "Collection_name": "Axolotl"
    },

    "Warden": {
        "Name": "Warden",
        "Type": "Rigs",
        "Blender Version": "4.x.x",
        ".blend_name": "Warden.blend",
        "Collection_name": "Warden"
    }
}

# Assets
class AssetPanel(Panel):
    bl_label = "Assets"
    bl_idname = "OBJECT_PT_assets"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'

    def draw(self, context):
        layout = self.layout

        self.bl_options = {'HIDE_HEADER'}

        box = layout.box()
        row = box.row()
        row.prop(context.scene, "selected_asset", text="Selected Asset")
        row = box.row()
        row.scale_y = 1.4
        row.operator("object.import_asset", text="Import Asset")

class ImportAssetOperator(Operator):
    bl_idname = "object.import_asset"
    bl_label = "Import Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
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
class AssetPanel(bpy.types.Panel):
    bl_label = "Assets"
    bl_idname = "OBJECT_PT_assets"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mcblend'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        
        self.bl_options = {'HIDE_HEADER'}

        # Выпадающее меню для выбора категории активов
        layout.prop(context.scene, "asset_category", text="Asset Category")

        # Список активов
        row = layout.row()
        row.template_list("ASSET_UL_items", "", context.scene, "asset_items", context.scene, "asset_index")

        # Кнопки
        row = layout.row(align=True)
        row.operator("object.import_asset", text="Import Asset")

# Список активов
class ASSET_UL_items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = "OBJECT_DATAMODE"
        layout.label(text=item.name, icon=custom_icon)

# Регистрация классов и свойств
def register():
    bpy.utils.register_class(AssetPanel)
    bpy.utils.register_class(ImportAssetOperator)
    bpy.utils.register_class(ASSET_UL_items)

    bpy.types.Scene.asset_category = bpy.props.EnumProperty(
        name="Category",
        items=[
            ('ALL', "All Assets", ""),
            ('CATEGORY_1', "Category 1", ""),
            ('CATEGORY_2', "Category 2", "")
        ],
        default='ALL'
    )
    bpy.types.Scene.asset_items = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.Scene.asset_index = bpy.props.IntProperty(default=0)
    bpy.types.Scene.selected_asset = bpy.props.StringProperty()

    # Пример данных для активов
    items = bpy.context.scene.asset_items
    items.clear()
    for name in Assets.keys():
        item = items.add()
        item.name = name

def unregister():
    bpy.utils.unregister_class(AssetPanel)
    bpy.utils.unregister_class(ImportAssetOperator)
    bpy.utils.unregister_class(ASSET_UL_items)
    del bpy.types.Scene.asset_category
    del bpy.types.Scene.asset_items
    del bpy.types.Scene.asset_index
    del bpy.types.Scene.selected_asset

if __name__ == "__main__":
    register()