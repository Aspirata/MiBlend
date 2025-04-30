from .Data import *
from .Materials import Materials
from .Resource_Packs import *
from .Optimization import Optimize
from .Utils_tools import *
from bpy.types import Operator
from .Assets import *
from .Utils.Absolute_Solver import Call_AS
import shutil

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

    create_fog: EnumProperty(
        items=[('None', 'None', ''),
            ('Create Fog', 'Create Fog', 'l'), 
            ('Recreate Fog', 'Recreate Fog', '')],
        name="create_fog",
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

        Materials.recreate_env(self)

        return {'FINISHED'}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=560)
    
    def draw(self, context):
        layout = self.layout
        world = bpy.context.scene.world
            
        box = layout.box()
        row = box.row()

        if world is not None:
            for node in world.node_tree.nodes:
                if node.type == 'GROUP':
                    if "MiBlend Sky" in node.node_tree.name:
                        row.prop(self, "reset_settings")
                        row = box.row()

        row.prop(self, "create_sky", text='create_sky', expand=True)
        row = box.row()
        row.prop(self, "create_fog", text='create_fog', expand=True)
        row = box.row()
        row.prop(self, "create_clouds", text='create_clouds', expand=True)

class RemoveAttributeOperator(Operator):
    bl_idname = "special.remove_attribute"
    bl_label = "Remove Attribute"
    bl_options = {'REGISTER', 'UNDO'}

    attribute: bpy.props.StringProperty()

    def execute(self, context):
        attr_name = self.attribute
        
        if attr_name in bpy.context.scene:
            del bpy.context.scene[attr_name]
            self.report({'INFO'}, f"Attribute '{attr_name}' has been removed.")
        else:
            try:
                parts = attr_name.split(".")
                current = bpy.context.scene

                for part in parts[:-1]:
                    current = getattr(current, part)
                
                attr = getattr(current, parts[-1])
                attr.clear()
                return {'FINISHED'}
            except AttributeError as e:
                self.report({'WARNING'}, f"Failed to remove attribute '{attr_name}': {str(e)}")
            except TypeError as e:
                self.report({'WARNING'}, f"Failed to remove attribute '{attr_name}': {str(e)}")
            self.report({'WARNING'}, f"Attribute '{attr_name}' does not exist.")
        return {'FINISHED'}

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
            dprint(resource_packs[self.pack_name]["type"], is_deep=True, zone="rp")
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
    
class RemoveResourcePack(Operator):
    bl_idname = "resource_pack.remove"
    bl_label = "Remove Resource Pack"
    bl_options = {'REGISTER', 'UNDO'}

    pack_name: bpy.props.StringProperty()

    def execute(self, context):
        resource_packs = get_resource_packs()
        if self.pack_name in resource_packs:
            del resource_packs[self.pack_name]
            set_resource_packs(resource_packs)
        return {'FINISHED'}

class UpdateDefaultPack(Operator):
    bl_idname = "resource_pack.update_default_pack"
    bl_label = "Reload Default Packs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        update_default_pack()
        return {'FINISHED'}

class AddResourcePack(Operator):
    bl_idname = "resource_pack.add"
    bl_label = "Add Resource Pack"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.zip;*/", options={'HIDDEN'})
    Mode: bpy.props.EnumProperty(items=[('temp', 'Temporarily', ''), ('perm', 'Permanently', '')])
    Type: bpy.props.EnumProperty(items=[('Automatic', 'Automatic', ''), ('Texture & PBR', 'Texture & PBR', ''), ('Texture', 'Texture', ''), ('PBR', 'PBR', '')])

    def execute(self, context):

        def check_suffix(file):
            parts = file.replace(".png", "").split('_')
            return parts[-1] in ("n", "s", "e")

        def define_type(filepath, self):
            resource_pack_type = self.Type

            if resource_pack_type == "Automatic":
                has_texture = False
                has_pbr = False
                resource_pack_type = "Texture & PBR"

                if os.path.isdir(filepath):
                    for root, _, files in os.walk(filepath):
                        for file in filter(lambda x: x.endswith('.png'), files):
                            if check_suffix(file):
                                has_pbr = True
                            else:
                                has_texture = True

                elif filepath.endswith(('.zip', '.jar')):
                    try:
                        with zipfile.ZipFile(filepath, 'r') as zip_ref:
                            for zip_info in filter(lambda x: x.filename.endswith('.png'), zip_ref.infolist()):
                                if check_suffix(zip_info.filename):
                                    has_pbr = True
                                else:
                                    has_texture = True
                                        
                    except zipfile.BadZipFile:
                        print(f"Warning: '{filepath}' is not a valid zip file.")
                
                else: 
                    for root, _, files in os.walk(os.path.dirname(filepath)):
                        for file in filter(lambda x: x.endswith('.png'), files):
                            if check_suffix(file):
                                has_pbr = True
                            else:
                                has_texture = True
                
                if has_texture and has_pbr:
                    resource_pack_type = 'Texture & PBR'
                elif has_texture:
                    resource_pack_type = 'Texture'
                elif has_pbr:
                    resource_pack_type = 'PBR'

            return resource_pack_type

        filepath = os.path.abspath(self.filepath)
        if os.path.isdir(filepath) or filepath.endswith(('.zip', '.jar')):
            if os.path.exists(filepath) and os.path.basename(filepath):
                pack_name = os.path.basename(filepath)
                pack_path = filepath
            else:
                pack_name = os.path.basename(os.path.dirname(filepath))
                pack_path = os.path.dirname(filepath)
        else:
            pack_name = os.path.basename(os.path.dirname(filepath))
            pack_path = os.path.dirname(filepath)

        if self.Mode == "temp":
            resource_packs = get_resource_packs()

            resource_packs[pack_name] = {
                "path": pack_path,
                "type": define_type(pack_path, self),
                "enabled": True,
                "is_default": False
            }

            dprint(resource_packs[pack_name]["type"], is_deep=True, zone="rp")
            if resource_packs[pack_name]["path"].endswith(('.zip', '.jar')) or os.path.isdir(resource_packs[pack_name]["path"]):
                set_resource_packs(resource_packs)
            else:
                Call_AS("e09", os.path.splitext(resource_packs[pack_name]["path"])[1])
                return {'CANCELLED'}
            
        elif self.Mode == "perm":
            resource_pack_directory = get_resource_path()
            destination = os.path.join(resource_pack_directory, pack_name)
            
            if os.path.exists(destination):
                if os.path.isdir(destination):
                    shutil.rmtree(destination)
                else:
                    os.remove(destination)
            
            if os.path.isdir(pack_path):
                shutil.copytree(pack_path, destination)
            else:
                shutil.copy2(pack_path, destination)
            
            with open(os.path.join(resource_pack_directory, 'packs_info.json'), 'r+') as f:
                data = json.load(f)
                data[pack_name] = {
                    "mc_version": "Unknown",
                    "pack_version": "Unknown",
                    "type": define_type(pack_path, self),
                }
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()

        update_assets()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class ApplyResourcePack(Operator):
    bl_idname = "resource_pack.apply"
    bl_label = "Apply Resource Packs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        apply_resources()
        return {'FINISHED'}

class CreateEnvOperator(Operator):
    bl_idname = "env.create_env"
    bl_label = "Create Environment"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.create_env()
        return {'FINISHED'}
        
class UpgradeMaterialsOperator(Operator):
    bl_idname = "materials.replace_materials"
    bl_label = "Upgrade Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.replace_materials()
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
            return {'CANCELLED'}
        return {'FINISHED'}

class CopyToClipboardOperator(Operator):
    bl_idname = "special.copy_to_clipboard"
    bl_label = "Copy to Clipboard"
    bl_options = {'REGISTER', 'UNDO'}
    
    text: StringProperty()

    def execute(self, context):
        try:
            bpy.context.window_manager.clipboard = self.text
        except RuntimeError:
            return {'CANCELLED'}
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
        current_preset = bpy.context.scene.miblend_properties.utils_properties.current_preset
        SetRenderSettings(current_preset)
        return {'FINISHED'}
    
class AssingVertexGroupOperator(Operator):
    bl_idname = "utils.assingvertexgroup"
    bl_label = "Assing Vertex Group"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        VertexRiggingTool()
        return {'FINISHED'}

class ResetPropertiesOperator(Operator):
    bl_idname = "assets.reset_properties"
    bl_label = "Reset Properties"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            current_asset = get_selected_asset()

            properties = {key: value for key, value in current_asset.items() if '_property' in key}

            file_path = current_asset.get("File_path", "")
            json_file_path = file_path.replace(os.path.splitext(file_path)[-1], ".json")
            
            with open(json_file_path, 'r') as json_file:
                asset_data = json.load(json_file)

            for key, value in properties.items():
                if key in asset_data:
                    current_asset[key] = asset_data.get(key, value)
            return {'FINISHED'}
        
        except Exception as error:
            if not os.path.isfile(json_file_path):
                Call_AS("e03", error, json_file_path)
            else:
                Call_AS("n00", error)
            return {'CANCELLED'}

class SavePropertiesOperator(Operator):
    bl_idname = "assets.save_properties"
    bl_label = "Save Properties"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            current_asset = get_selected_asset()

            properties = {key: value for key, value in current_asset.items() if 'property' in key.lower()}

            file_path = current_asset.get("File_path", "")
            json_file_path = file_path.replace(os.path.splitext(file_path)[-1], ".json")
        
            with open(json_file_path, 'r') as json_file:
                asset_data = json.load(json_file)

            for key, value in properties.items():
                if key in asset_data:
                    asset_data[key] = value

            with open(json_file_path, 'w') as json_file:
                json.dump(asset_data, json_file, indent=4)
            
            self.report({'INFO'}, f"Properties saved to {json_file_path}")
            return {'FINISHED'}
        
        except Exception as error:
            if not os.path.isfile(json_file_path):
                Call_AS("e03", error, json_file_path)
            else:
                Call_AS("n00", error)
            return {'CANCELLED'}
    
class RemoveAsset(Operator):
    bl_idname = "assets.remove_asset"
    bl_label = "Add Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            NotImplemented
            return {'FINISHED'}
        
        except Exception as error:
            if not os.path.isfile(json_file_path):
                Call_AS("e03", error, json_file_path)
            else:
                Call_AS("n00", error)
            return {'CANCELLED'}

class AddAsset(Operator):
    bl_idname = "assets.add_asset"
    bl_label = "Add Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        path = self.filepath
        json_file_path = None
        asset_type = 'Presistent'

        if path.endswith('.json'):
            asset_type = 'Scene Only'
            json_file_path = path
        elif path.endswith('.zip'):
            extract_path = os.path.join(bpy.app.tempdir, "extracted_asset")

            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)
            os.makedirs(extract_path, exist_ok=True)

            if path.endswith('.zip'):
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                dprint(f"ZIP file extracted to {extract_path}", is_deep=True, zone="uas")
            else:
                dprint("The provided path is neither a directory nor a ZIP file.", is_deep=True, zone="uas")
                return {'CANCELLED'}
        else:
            dprint(f"Unknown File {os.path.basename(path)}", is_deep=True, zone="uas")
            
        if asset_type == "Presistent":
            for root, dirs, files in os.walk(extract_path):
                for file in files:
                    if file.endswith('.json'):
                        json_file_path = os.path.join(root, file)
                        break
                if json_file_path:
                    break

        if os.path.isfile(json_file_path):
            with open(json_file_path, 'r') as f:
                asset_data = json.load(f)

            file_path_in_json = os.path.dirname(asset_data.get("File_path", ""))
            
            if asset_type == 'Scene Only':
                temp_assets_path = bpy.context.scene.get("mib_options").get("temp_assets_paths")
    
                temp_assets_path_list = list(temp_assets_path)
                temp_assets_path_list.append(os.path.dirname(json_file_path))
                
                bpy.context.scene["mib_options"]["temp_assets_paths"] = temp_assets_path_list
                dprint(f"Using temporary asset in {os.path.dirname(json_file_path)}")

            elif file_path_in_json:
                destination_path = os.path.join(assets_directory, file_path_in_json)
                os.makedirs(destination_path, exist_ok=True)

                for item in os.listdir(extract_path):
                    src_path = os.path.join(extract_path, item)
                    dst_path = os.path.join(destination_path, item)

                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src_path, dst_path)

                dprint(f"Persistent asset files successfully copied to {destination_path}")
            else:
                dprint("File_path not specified in the JSON file")
        else:
            dprint("No .json file found in the extracted content")

        update_assets()
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class CreateAsset(Operator):
    bl_idname = "assets.create_asset"
    bl_label = "Create Asset"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    asset_name: bpy.props.StringProperty(name="Asset Name", default="NewAsset")

    asset_type: bpy.props.EnumProperty(
        name="Asset Type",
        items=[
            ('COLLECTION', "Collection", "Export a collection"),
            ('NODE_GROUP', "Node Group", "Export a node group"),
            ('MATERIAL', "Material", "Export a material")
        ],
        default='COLLECTION',
        update=lambda self, ctx: self.update_asset_list(ctx)
    )

    # Заглушка для EnumProperty
    asset_choice: bpy.props.EnumProperty(name="Asset Choice", items=lambda self, ctx: [("NONE", "None Available", "No assets found")])

    def update_asset_list(self, context):
        """Обновляет список доступных коллекций, нодов или материалов"""
        if self.asset_type == 'COLLECTION':
            items = [(coll.name, coll.name, "") for coll in bpy.data.collections]
        elif self.asset_type == 'NODE_GROUP':
            items = [(ng.name, ng.name, "") for ng in bpy.data.node_groups]
        elif self.asset_type == 'MATERIAL':
            items = [(mat.name, mat.name, "") for mat in bpy.data.materials]
        else:
            items = []

        if not items:
            items = [("NONE", "None Available", "No assets found")]

        # Пересоздаём EnumProperty
        def items_callback(self, context):
            return items

        if "asset_choice" in self.__annotations__:
            del self.__annotations__["asset_choice"]  # Удаляем аннотацию

        self.__annotations__["asset_choice"] = bpy.props.EnumProperty(
            name="Asset Choice",
            description="Choose an asset",
            items=items_callback
        )

        # Присваиваем первый доступный элемент
        self.asset_choice = items[0][0]

    def execute(self, context):
        if not self.filepath.endswith(".blend"):
            self.report({'ERROR'}, "Please select a .blend file")
            return {'CANCELLED'}

        if self.asset_choice == "NONE":
            self.report({'ERROR'}, f"No {self.asset_type.lower()} found to export.")
            return {'CANCELLED'}

        # Директория хранения ассетов
        assets_root = bpy.context.preferences.addons[__name__].preferences.assets_path  # Указать путь
        asset_folder = os.path.join(assets_root, "Rigs", self.asset_name)

        if os.path.exists(asset_folder):
            shutil.rmtree(asset_folder)
        os.makedirs(asset_folder, exist_ok=True)

        # Копирование .blend файла
        blend_dst_path = os.path.join(asset_folder, f"{self.asset_name}.blend")
        shutil.copy2(self.filepath, blend_dst_path)

        # Создание JSON файла
        json_data = {
            "Format_version": "10",
            "Asset_name": self.asset_name,
            "Author": "Aspirata",
            "File_path": f"Rigs\\{self.asset_name}\\{self.asset_name}",
            "Collection_name": self.asset_choice if self.asset_type == "COLLECTION" else "",
            "Node_group": self.asset_choice if self.asset_type == "NODE_GROUP" else "",
            "Material": self.asset_choice if self.asset_type == "MATERIAL" else "",
            "Tags": ["Rig", "Simple"] if self.asset_type == "COLLECTION" else ["NodeGroup"] if self.asset_type == "NODE_GROUP" else ["Material"]
        }

        json_path = os.path.join(asset_folder, f"{self.asset_name}.json")
        with open(json_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)

        self.report({'INFO'}, f"Asset '{self.asset_name}' created successfully")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.update_asset_list(context)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "asset_name")
        layout.prop(self, "asset_type")
        layout.prop(self, "asset_choice")

    def check(self, context):
        return True

class ImportAssetOperator(Operator):
    bl_idname = "assets.import_asset"
    bl_label = "Import Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            asset_data = get_selected_asset()
            File_path = asset_data.get("File_path", "")
            
            if not os.path.isfile(File_path):
                dprint(f"{File_path} isn't a file") # Replace with AS
                return {'CANCELLED'}
        
            append_asset(asset_data)

            return {'FINISHED'}
        except Exception as error:
            Call_AS("n00", traceback.format_exc())
            return {'CANCELLED'}
    
class ManualAssetsUpdateOperator(Operator):
    bl_idname = "assets.update_assets"
    bl_label = "Reload Assets List"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        update_assets()
        return {'FINISHED'}
    
class ClearIgnoredCodesOperator(Operator):
    bl_idname = "debug.clear_ignored_codes"
    bl_label = "Clear Ignored Codes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.miblend_properties.absolute_solver_properties.ignored_codes = ""
        return {'FINISHED'}

class TriggerASErrorOperator(Operator):
    bl_idname = "debug.trigger_as_error"
    bl_label = "Trigger AS Error"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        Call_AS("e-1")
        return {'FINISHED'}