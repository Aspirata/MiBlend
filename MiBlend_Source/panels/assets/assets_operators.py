import os
import json
import zipfile
import shutil
import traceback
import bpy
from bpy.types import Operator
from . import assets_logic
from ..absolute_solver.absolute_solver_logic import trigger_absolute_solver
from ...resources.data import assets_directory
from ...mib_utils import dprint, get_selected_asset


class MIBLEND_OT_import_asset(Operator):
    bl_idname = "miblend.import_asset"
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
        
            assets_logic.append_asset(asset_data)

            return {'FINISHED'}
        except Exception:
            trigger_absolute_solver("n00", traceback.format_exc())
            return {'CANCELLED'}


class MIBLEND_OT_update_assets(Operator):
    bl_idname = "miblend.update_assets"
    bl_label = "Reload Assets List"
    bl_description = "Reloads Assets List"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        assets_logic.update_assets()
        return {'FINISHED'}


class MIBLEND_OT_add_asset(Operator):
    bl_idname = "miblend.add_asset"
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

        assets_logic.update_assets()
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MIBLEND_OT_remove_asset(Operator):
    bl_idname = "miblend.remove_asset"
    bl_label = "Removes Temporal Asset from the List"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
   
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
        
        assets_logic.update_assets()
        return {'FINISHED'}


class MIBLEND_OT_save_properties(Operator):
    bl_idname = "miblend.save_properties"
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
                trigger_absolute_solver("e03", error, json_file_path)
            else:
                trigger_absolute_solver("n00", error)
            return {'CANCELLED'}


class MIBLEND_OT_reset_properties(Operator):
    bl_idname = "miblend.reset_properties"
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
                trigger_absolute_solver("e03", error, json_file_path)
            else:
                trigger_absolute_solver("n00", error)
            return {'CANCELLED'}
