import bpy
import os
import shutil
import json
import zipfile
from bpy.types import Operator
from .resource_packs_logic import get_resource_packs, set_resource_packs, update_default_pack, apply_resources, get_resource_path
from ...mib_utils import dprint
from ..absolute_solver.absolute_solver_logic import trigger_absolute_solver


class MIBLEND_OT_toggle_resource_pack(Operator):
    bl_idname = "miblend.toggle_resource_pack"
    bl_label = "Toggle Resource Pack"
    bl_description = "Toggles the Enabled State of a Resource Pack"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    pack_name: bpy.props.StringProperty()

    def execute(self, context):
        resource_packs = get_resource_packs()
        if self.pack_name in resource_packs:
            resource_packs[self.pack_name]["enabled"] = not resource_packs[self.pack_name]["enabled"]
            dprint(resource_packs[self.pack_name]["type"], is_deep=True, zone="rp")
            set_resource_packs(resource_packs)
        return {'FINISHED'}


class MIBLEND_OT_move_resource_pack_up(Operator):
    bl_idname = "miblend.move_resource_pack_up"
    bl_label = "Move Resource Pack Up"
    bl_description = "Moves the Selected Resource Pack Up in the Priority List"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

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


class MIBLEND_OT_move_resource_pack_down(Operator):
    bl_idname = "miblend.move_resource_pack_down"
    bl_label = "Move Resource Pack Down"
    bl_description = "Moves the Selected Resource Pack Down in the Priority List"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

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
    

class MIBLEND_OT_remove_resource_pack(Operator):
    bl_idname = "miblend.remove_resource_pack"
    bl_label = "Remove Resource Pack"
    bl_description = "Removes a Resource Pack from the List"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

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


class MIBLEND_OT_update_default_pack(Operator):
    bl_idname = "miblend.update_default_pack"
    bl_label = "Reload Packs List"
    bl_description = "Reloads the Resource Packs List"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        update_default_pack()
        return {'FINISHED'}


class MIBLEND_OT_add_resource_pack(Operator):
    bl_idname = "miblend.add_resource_pack"
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
                trigger_absolute_solver("e09", data=os.path.splitext(resource_packs[pack_name]["path"])[1])
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


class MIBLEND_OT_apply_resource_pack(Operator):
    bl_idname = "miblend.apply_resource_pack"
    bl_label = "Apply Resource Packs"
    bl_description = "Applies Enabled Resource Packs in a Specified Order"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        apply_resources()
        return {'FINISHED'}
