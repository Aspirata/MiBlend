import bpy, os, json, shutil, platform, subprocess
from .Materials import Materials
from .Resource_Packs import apply_resources, get_resource_packs, set_resource_packs, get_resource_path, update_default_pack
from .Optimization import Optimize
from .Utils_tools import *
from bpy.types import Operator
from bpy.props import BoolProperty, IntProperty, FloatProperty, StringProperty, EnumProperty
from .Assets import *
from .Utils.Absolute_Solver import Call_AS
from .Data import main_directory

class RecreateEnvironment(Operator):
    bl_label = "Recreate Environment"
    bl_idname = "special.recreate_env"
    bl_description = "Recreates the Environment with Options for Sky, Fog, and Clouds"
    bl_options = {'REGISTER', 'UNDO'}
    
    reset_settings: BoolProperty(
        name="Reset Settings",
        description="Resets the sky settings",
        default=False
    )

    create_sky: EnumProperty(
        items=[('None', 'None', ''),
            ('Create Sky', 'Create Sky', 'Reuses Already Imported Sky Material'), 
            ('Recreate Sky', 'Recreate Sky', 'Reappends Sky Material')],
        name="create_sky",
        description="Options for reusing imported sky assets or reimporting them",
        default='None'
    )

    create_fog: EnumProperty(
        items=[('None', 'None', ''),
            ('Create Fog', 'Create Fog', 'l'), 
            ('Recreate Fog', 'Recreate Fog', '')],
        name="create_fog",
        description="Options for reusing imported fog assets or reimporting them",
        default='None'
    )
    
    create_clouds: EnumProperty(
        items=[('None', 'None', ''),
            ('Create Clouds', 'Create Clouds', ''), 
            ('Recreate Clouds', 'Recreate Clouds', '')],
        name="create_clouds",
        description="Options for reusing imported cloud assets or reimporting them",
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
    bl_description = "Removes a Specified Attribute from the Scene"
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
    bl_description = "Fixes the World's Problems After Import"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.fix_world()
        return {'FINISHED'}
    
class ResourcePackToggleOperator(Operator):
    bl_idname = "resource_pack.toggle"
    bl_label = "Toggle Resource Pack"
    bl_description = "Toggles the Enabled State of a Resource Pack"
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
    bl_description = "Moves the Selected Resource Rack Up in the Priority List"
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
    bl_description = "Moves the Selected Resource Pack Down in the Priority List"
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
    bl_description = "Removes a Resource Pack from the List"
    bl_options = {'REGISTER', 'UNDO'}

    pack_name: bpy.props.StringProperty()

    def execute(self, context):
        resource_packs = get_resource_packs()
        is_default = resource_packs.get(self.pack_name, {}).get("is_default", False)
        if self.pack_name not in resource_packs:
            return {'CANCELLED'}

        if is_default:
            pack_path = resource_packs.get(self.pack_name, {}).get("path", "")
            try:
                if os.path.isdir(pack_path):
                    shutil.rmtree(pack_path)
                else:
                    os.remove(pack_path)
            except Exception as e:
                self.report({'ERROR'}, f"Failed to delete pack: {e}")
                return {'CANCELLED'}
            
            resource_packs_directory = get_resource_path()
            packs_info_path = os.path.join(resource_packs_directory, "packs_info.json")
            
            try:
                with open(packs_info_path, "r+", encoding="utf-8") as f:
                    data = json.load(f)
                    if self.pack_name in data:
                        del data[self.pack_name]
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
            except Exception as e:
                self.report({'ERROR'}, f"Failed to update packs_info.json: {e}")
                return {'CANCELLED'}
        
        else:
            del resource_packs[self.pack_name]
            
        set_resource_packs(resource_packs)
            
        return {'FINISHED'}

class UpdateDefaultPack(Operator):
    bl_idname = "resource_pack.update_default_pack"
    bl_label = "Reload Packs List"
    bl_description = "Reloads the Resource Packs List"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        update_default_pack()
        return {'FINISHED'}

class AddResourcePack(Operator):
    bl_idname = "resource_pack.add"
    bl_label = "Add Resource Pack"
    bl_description = "Adds a New Resource Pack to the List"
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

        update_default_pack()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class ApplyResourcePack(Operator):
    bl_idname = "resource_pack.apply"
    bl_label = "Apply Resource Packs"
    bl_description = "Applies Enabled Resource Packs in a Specified Order"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        apply_resources()
        return {'FINISHED'}

class CreateEnvOperator(Operator):
    bl_idname = "env.create_env"
    bl_label = "Create Environment"
    bl_description = "Creates a New Environment"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.create_env()
        return {'FINISHED'}
        
class UpgradeMaterialsOperator(Operator):
    bl_idname = "materials.replace_materials"
    bl_label = "Upgrade Materials"
    bl_description = "Deprecated Feature"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.replace_materials()
        return {'FINISHED'}

class FixMaterialsOperator(Operator):
    bl_idname = "materials.fix_materials"
    bl_label = "Fix Materials"
    bl_description = "Fixes Materials with Maximum Compatibility"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.fix_materials()
        return {'FINISHED'}
    
class SwapTexturesOperator(Operator):
    bl_idname = "materials.swap_textures"
    bl_label = "Swap Textures"
    bl_description = "Swapes Textures with Maximum Compatibility"
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
    bl_description = "Toggles Blender System Console"
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
    bl_description = "Copies the Text to your Clipboard"
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
    bl_description = "Applies Procedural PBR"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Materials.setproceduralpbr()
        return {'FINISHED'}

class OptimizeOperator(Operator):
    bl_idname = "optimization.optimization"
    bl_label = "Optimize"
    bl_description = "Deprecated Feature"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Optimize.Optimize()
        return {'FINISHED'}
    
class SetRenderSettingsOperator(Operator):
    bl_idname = "utils.setrendersettings"
    bl_label = "Set Render Settings"
    bl_description = "Deprecated Feature"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        current_preset = bpy.context.scene.miblend_properties.utils_properties.current_preset
        SetRenderSettings(current_preset)
        return {'FINISHED'}
    
class AssingVertexGroupOperator(Operator):
    bl_idname = "utils.assingvertexgroup"
    bl_label = "Assing Vertex Group"
    bl_description = "Deprecated Feature"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        VertexRiggingTool()
        return {'FINISHED'}

class ResetPropertiesOperator(Operator):
    bl_idname = "assets.reset_properties"
    bl_label = "Reset Properties"
    bl_description = "Resets Propreties to their Default Values"
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
    bl_description = "Overwrites the Asset's Properties Default Values"
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

class AddAsset(Operator):
    bl_idname = "assets.add_asset"
    bl_label = "Add Asset"
    bl_description = "Addes a MiBlend Ready Asset to the list"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(
        default="*.zip;*.json",
        options={'HIDDEN'},
    )
    
    filter_folder: bpy.props.BoolProperty(default=True, options={'HIDDEN'})
    filter_text: bpy.props.BoolProperty(default=True, options={'HIDDEN'})

    def execute(self, context):
        path = self.filepath
        json_file_path = None
        is_asset_persistent = True

        if path.endswith('.json'):
            is_asset_persistent = False
            json_file_path = path
            
        elif path.endswith('.zip'):
            extract_path = os.path.join(bpy.app.tempdir, "extracted_asset")

            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)
            os.makedirs(extract_path, exist_ok=True)
            
            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
                
            dprint(f"ZIP file extracted to {extract_path}", is_deep=True, zone="uas")
            
            for root, dirs, files in os.walk(extract_path):
                for file in files:
                    if file.endswith('.json'):
                        json_file_path = os.path.join(root, file)
                        break
        else:
            dprint("The provided path is neither a .json nor a .zip file.", is_deep=True, zone="uas")
            return {'CANCELLED'}

        if not os.path.isfile(json_file_path):
            dprint("No .json file found in the extracted content")
            return {'CANCELLED'}
            
        with open(json_file_path, 'r') as f:
            asset_data = json.load(f)

        file_path_in_json = os.path.dirname(asset_data.get("File_path", ""))
        
        if not file_path_in_json:
            dprint("File_path not specified in the JSON file")
            return {'CANCELLED'}

        if is_asset_persistent:
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
            temp_assets_path = bpy.context.scene.get("mib_options").get("temp_assets_paths")

            temp_assets_path_list = list(temp_assets_path)
            temp_assets_path_list.append(os.path.dirname(json_file_path))
            
            bpy.context.scene["mib_options"]["temp_assets_paths"] = temp_assets_path_list
            dprint(f"Using temporary asset in {os.path.dirname(json_file_path)}")

        update_assets()
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class RemoveAsset(Operator):
    bl_idname = "assets.remove_asset"
    bl_label = "Removes Temporal Asset from the List"
    bl_options = {'REGISTER', 'UNDO'}
   
    def execute(self, context):
        asset_props = context.scene.miblend_properties.assets_properties
        asset_items = asset_props.asset_items
        current_asset_index = asset_props.asset_index
        
        if current_asset_index < 0 or current_asset_index >= len(asset_items):
            return {'CANCELLED'}
        
        asset_dir = os.path.dirname(asset_items[current_asset_index]["File_path"])
        temp_assets_paths = context.scene["mib_options"]["temp_assets_paths"]
        temp_assets_paths_list = list(temp_assets_paths)
        
        if asset_dir in temp_assets_paths:
            temp_assets_paths_list.remove(asset_dir)
            
        context.scene["mib_options"]["temp_assets_paths"] = temp_assets_paths_list
        
        update_assets()
        return {'FINISHED'}

class ImportAssetOperator(Operator):
    bl_idname = "assets.import_asset"
    bl_label = "Import Asset"
    bl_description = "Appends/Executes Selected Asset to the Scene"
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
    bl_description = "Reloads Assets List"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        update_assets()
        return {'FINISHED'}
    
class ClearIgnoredCodesOperator(Operator):
    bl_idname = "debug.clear_ignored_codes"
    bl_label = "Clear Ignored Codes"
    bl_description = "Cleares the List of Ignored Errors and Warnings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.miblend_properties.absolute_solver_properties.ignored_codes = ""
        return {'FINISHED'}

class SavePreferencesOperator(Operator):
    bl_idname = "preferences.save_preferences"
    bl_label = "Save Preferences"
    bl_description = "Saves Current Preferencies to settings_override.json"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_prefs = context.preferences.addons[__package__].preferences
        prefs_to_save: dict[str, Union[str, bool, int, float]] = {}
        settings_override_path = os.path.join(os.path.dirname(main_directory), "settings_override.json")
        system_props = {
            'rna_type', 'name', 'bl_idname', 'bl_label', 'bl_description', 
            'bl_options', 'bl_context', 'bl_region_type', 'bl_space_type'
        }
        
        for prop_id, prop in type(addon_prefs).bl_rna.properties.items():
            if prop_id in system_props or prop_id.startswith('_'):
                continue

            default_value = prop.default
            current_value = getattr(addon_prefs, prop_id)
            
            if current_value == default_value:
                continue
            
            prefs_to_save[prop_id] = current_value
        
        if not prefs_to_save and os.path.exists(settings_override_path):
            os.remove(settings_override_path)
            self.report({'INFO'}, "Settings reset to defaults")
        
        elif not prefs_to_save:
            self.report({'INFO'}, f"Saved 0 preferences")
            return {'CANCELLED'}
        
        os.makedirs(os.path.dirname(settings_override_path), exist_ok=True)
        
        with open(settings_override_path, "w", encoding="utf-8") as file:
            json.dump(prefs_to_save, file, indent=2, ensure_ascii=False)
        
        self.report({'INFO'}, f"Saved {len(prefs_to_save)} preference(s)")

        return {'FINISHED'}

class ResetPreferencesOperator(Operator):
    bl_idname = "preferences.reset_preferences"
    bl_label = "Reset Preferences"
    bl_description = "Resets MiBlend Preferencies to their Default Values"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_prefs = context.preferences.addons[__package__].preferences
        system_props = {
            'rna_type', 'name', 'bl_idname', 'bl_label', 'bl_description', 
            'bl_options', 'bl_context', 'bl_region_type', 'bl_space_type'
        }
        
        for prop_id, prop in type(addon_prefs).bl_rna.properties.items():
            if prop_id in system_props or prop_id.startswith('_'):
                continue
            
            setattr(addon_prefs, prop_id, prop.default)
        return {'FINISHED'}

class TriggerASErrorOperator(Operator):
    bl_idname = "debug.trigger_as_error"
    bl_label = "Trigger AS Error"
    bl_description = "Triggers e00"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if "e-1" in context.scene.miblend_properties.absolute_solver_properties.ignored_codes:
            self.report({'ERROR'}, f"You're ignoring this error dumbass")
        elif bpy.context.preferences.addons[str(__package__).split(".")[0]].preferences.show_warnings:
            self.report({'ERROR'}, f"You can't see warnings because you've disabled them dumbass")
        else:
            Call_AS("e-1")
        return {'FINISHED'}

class OpenMiBlendFolder(Operator):
    bl_idname = "debug.open_miblend_folder"
    bl_label = "Open MiBlend Folder"
    bl_description = "Opens MiBlend Folder in your File Explorer"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        folder_path = os.path.abspath(os.path.dirname(__file__))
        if platform.system() == "Windows":
            os.startfile(folder_path)
        elif platform.system() == "Darwin":
            subprocess.call(["open", folder_path])
        else:
            subprocess.call(["xdg-open", folder_path])
        return {'FINISHED'}