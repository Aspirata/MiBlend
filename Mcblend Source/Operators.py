from .Data import *
from .Materials import Materials
from .Resource_Packs import *
from .Optimization import Optimize
from .Utils_tools import *
from bpy.types import Operator
from .Assets import *

class RecreateEnvironment(Operator):
    bl_label = "Recreate Environment"
    bl_idname = "special.recreate_env"
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
        world = bpy.context.scene.world
        
        if bpy.context.preferences.addons[__package__].preferences.enable_warnings:
            box = layout.box()
            row = box.row()
            row.label(text="WARNING !", icon='ERROR')
            row = box.row()
            row.label(text="This option should be used with caution")
            
        box = layout.box()
        row = box.row()

        if world is not None:
            for node in world.node_tree.nodes:
                if node.type == 'GROUP':
                    if "Mcblend Sky" in node.node_tree.name:
                        row.prop(self, "reset_settings")
                        row = box.row()

        row.prop(self, "create_sky", text='create_sky', expand=True)
        row = box.row()
        row.prop(self, "create_clouds", text='create_clouds', expand=True)

class FixWorldOperator(Operator):
    bl_idname = "world.fix_world"
    bl_label = "Fix World"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.fix_world()
        return {'FINISHED'}
    
class ResourcePackToggleOperator(Operator):
    bl_idname = "resource_pack.toggle"
    bl_label = "Toggle Resource Pack"
    bl_options = {'REGISTER', 'UNDO'}

    pack_name: bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene
        resource_packs = get_resource_packs()
        if self.pack_name in resource_packs:
            resource_packs[self.pack_name]["enabled"] = not resource_packs[self.pack_name]["enabled"]
            set_resource_packs(resource_packs)
        return {'FINISHED'}

class MoveResourcePackUp(Operator):
    bl_idname = "resource_pack.move_up"
    bl_label = "Move Resource Pack Up"
    bl_options = {'REGISTER', 'UNDO'}

    pack_name: bpy.props.StringProperty()

    def execute(self, context):
        resource_packs = get_resource_packs()
        keys = list(resource_packs.keys())
        idx = keys.index(self.pack_name)
        if idx > 0:
            keys[idx], keys[idx - 1] = keys[idx - 1], keys[idx]
            reordered_packs = {k: resource_packs[k] for k in keys}
            set_resource_packs(reordered_packs)
        return {'FINISHED'}

class MoveResourcePackDown(Operator):
    bl_idname = "resource_pack.move_down"
    bl_label = "Move Resource Pack Down"
    bl_options = {'REGISTER', 'UNDO'}

    pack_name: bpy.props.StringProperty()

    def execute(self, context):
        resource_packs = get_resource_packs()
        keys = list(resource_packs.keys())
        idx = keys.index(self.pack_name)
        if idx < len(keys) - 1:
            keys[idx], keys[idx + 1] = keys[idx + 1], keys[idx]
            reordered_packs = {k: resource_packs[k] for k in keys}
            set_resource_packs(reordered_packs)
        return {'FINISHED'}

class ResourcePackOptions(Operator):
    bl_idname = "resource_pack.options"
    bl_label = "Resource Pack Option"
    bl_options = {'REGISTER', 'UNDO'}

    pack_name: bpy.props.StringProperty()

    def execute(self, context):
        resource_packs = get_resource_packs()
        option = context.scene.resource_properties.pack_options
        if option == "Remove":
            if self.pack_name in resource_packs:
                del resource_packs[self.pack_name]
                set_resource_packs(resource_packs)
        elif option == "Info":
            print(resource_packs[self.pack_name]["path"], resource_packs[self.pack_name]["type"])
        return {'FINISHED'}

class UpdateDefaultPack(Operator):
    bl_idname = "resource_pack.update_default_pack"
    bl_label = "Reload Default Packs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        update_default_pack()
        return {'FINISHED'}
    
class FixPacks(Operator):
    bl_idname = "resource_pack.fix"
    bl_label = "Fix Packs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if "resource_packs" not in bpy.context.scene:
            bpy.context.scene["resource_packs"] = {}
        update_default_pack()
        return {'FINISHED'}

class AddResourcePack(Operator):
    bl_idname = "resource_pack.add"
    bl_label = "Add Resource Pack"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(subtype="DIR_PATH")
    Type: bpy.props.EnumProperty(items=[('Automatic', 'Automatic', ''), ('Texture & PBR', 'Texture & PBR', ''), ('Texture', 'Texture', ''), ('PBR', 'PBR', '')])

    def execute(self, context):
        resource_packs = get_resource_packs()

        resource_pack_type = self.Type
        if resource_pack_type == "Automatic":
            has_texture = False
            has_pbr = False
            resource_pack_type = "Texture & PBR"

            if os.path.isdir(self.filepath):
                for root, _, files in os.walk(self.filepath):
                    for file in files:
                        if file.endswith('.png'):
                            if any(suffix in file for suffix in ('_n', '_s', '_e')):
                                has_pbr = True
                            else:
                                has_texture = True

            elif self.filepath.endswith(('.zip', '.jar')):
                try:
                    with zipfile.ZipFile(self.filepath, 'r') as zip_ref:
                        for zip_info in zip_ref.infolist():
                            if zip_info.filename.endswith('.png'):
                                if any(suffix in zip_info.filename for suffix in ('_n', '_s', '_e')):
                                    has_pbr = True
                                else:
                                    has_texture = True
                                    
                except zipfile.BadZipFile:
                    print(f"Warning: '{self.filepath}' is not a valid zip file.")
            
            else: 
                for root, _, files in os.walk(os.path.dirname(self.filepath)):
                    for file in files:
                        if file.endswith('.png'):
                            if any(suffix in file for suffix in ('_n', '_s', '_e')):
                                has_pbr = True
                            else:
                                has_texture = True
            
            if has_texture and has_pbr:
                resource_pack_type = 'Texture & PBR'
            elif has_texture:
                resource_pack_type = 'Texture'
            elif has_pbr:
                resource_pack_type = 'PBR'

        if os.path.isdir(self.filepath) or self.filepath.endswith(('.zip', '.jar')):
            if os.path.exists(os.path.abspath(self.filepath)) and os.path.basename(self.filepath) != "":
                pack_name = os.path.basename(self.filepath)
                resource_packs[pack_name] = {"path": os.path.abspath(self.filepath), "type": resource_pack_type, "enabled": True}
            else:
                pack_name = os.path.basename(os.path.dirname(self.filepath))
                resource_packs[pack_name] = {"path": os.path.dirname(self.filepath), "type": resource_pack_type, "enabled": True}
        else:
            pack_name = os.path.basename(os.path.dirname(self.filepath))
            resource_packs[pack_name] = {"path": os.path.dirname(self.filepath), "type": resource_pack_type, "enabled": True}
        
        set_resource_packs(resource_packs)

        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class ApplyResourcePack(Operator):
    bl_idname = "resource_pack.apply"
    bl_label = "Apply Resource Packs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        start_time = time.time()
        Materials.apply_resources()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"apply_resources() took {elapsed_time:.4f} seconds to complete.")
        return {'FINISHED'}

class CreateEnvOperator(Operator):
    bl_idname = "env.create_env"
    bl_label = "Create Environment"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.create_env()
        return {'FINISHED'}
        
class UpgradeMaterialsOperator(Operator):
    bl_idname = "materials.upgrade_materials"
    bl_label = "Upgrade Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.upgrade_materials()
        return {'FINISHED'}

class FixMaterialsOperator(Operator):
    bl_idname = "materials.fix_materials"
    bl_label = "Fix Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.fix_materials()
        return {'FINISHED'}
    
class SwapTexturesOperator(Operator):
    bl_idname = "materials.swap_textures"
    bl_label = "Swap Textures"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        if os.path.isdir(self.filepath) or self.filepath.endswith('.zip'):
            Materials.swap_textures(os.path.abspath(self.filepath))
            self.report({'INFO'}, f"Selected Folder: {os.path.abspath(self.filepath)}")
        else:
            Materials.swap_textures(os.path.dirname(self.filepath))
            self.report({'INFO'}, f"Selected Folder: {os.path.dirname(self.filepath)}")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class OpenConsoleOperator(Operator):
    bl_idname = "special.open_console"
    bl_label = "Open Console"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            bpy.ops.wm.console_toggle()
        except RuntimeError:
            pass
        return {'FINISHED'}
    
class SetProceduralPBROperator(Operator):
    bl_idname = "ppbr.setproceduralpbr"
    bl_label = "Set Procedural PBR"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.setproceduralpbr()
        return {'FINISHED'}

class OptimizeOperator(Operator):
    bl_idname = "optimization.optimization"
    bl_label = "Optimize"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Optimize.Optimize()
        return {'FINISHED'}
    
class SetRenderSettingsOperator(Operator):
    bl_idname = "utils.setrendersettings"
    bl_label = "Set Render Settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        current_preset = bpy.context.scene.utilsproperties.current_preset
        SetRenderSettings(current_preset)
        return {'FINISHED'}
    
class EnchantOperator(Operator):
    bl_idname = "utils.enchant"
    bl_label = "Enchant Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Enchant()
        return {'FINISHED'}
    
class AssingVertexGroupOperator(Operator):
    bl_idname = "utils.assingvertexgroup"
    bl_label = "Assing Vertex Group"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        VertexRiggingTool()
        return {'FINISHED'}

class ImportAssetOperator(Operator):
    bl_idname = "assets.import_asset"
    bl_label = "Import Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        current_index = bpy.context.scene.assetsproperties.asset_index
        items = bpy.context.scene.assetsproperties.asset_items

        if current_index < 0 or current_index >= len(items):
            Absolute_Solver(error_name="Invalid Asset Index", description="Something went wrong with the asset index", mode="Full")
            return {'CANCELLED'}

        asset_name = items[current_index].name

        for category, assets in Assets.items():
            if asset_name in assets:
                append_asset(asset_name, category)
                break
        return {'FINISHED'}
    
class ManualAssetsUpdateOperator(Operator):
    bl_idname = "assets.update_assets"
    bl_label = "Reload Assets List"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        update_assets()
        return {'FINISHED'}