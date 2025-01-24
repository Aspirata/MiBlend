from .Data import *
from .Utils.Absolute_Solver import Call_AS
from typing import Optional, Union
import time
import sys
import re

def PBSDF_compability(Input: str) -> str:
    if blender_version("3.x.x"):
        return {
            "Subsurface Weight": "Subsurface",
            "Subsurface Radius": "Subsurface Color",

            "Specular IOR Level": "Specular",

            "Transmission Weight": "Transmission",

            "Coat Weight": "Coat",
            "Sheen Weight": "Sheen",

            "Emission Color": "Emission",
        }.get(Input, Input)
    return Input

def clamp(min_value: Union[int, float], value: Union[int, float], max_value: Union[int, float]):
    return max(min_value, min(value, max_value))

def is_mesh(object):
    return object.type == "MESH"

def mc_version_formatter(version_name: str) -> Optional[str]:
    try:
        version_parts = re.split(r'[ -]', version_name)
        for part in version_parts:
            if not any(char.isalpha() for char in part) and re.match(r'^\d{1}\.\d{1,2}(?:\.\d{1,2})?$', part):
                return part
        return None
    except Exception as error:
        Call_AS("n00", error)

def name_in(Array: list, material_or_texture_name: str, is_texture=False, mode="in") -> Optional[tuple[bool, str]]:
    if is_texture:
        name = format_texture_name(material_or_texture_name)
    else:
        name = format_material_name(material_or_texture_name)

    for item in Array:
        old_item = item
        if ";" in item:
            anti_keywords = item.split(" ; ")[1].split()
            if any(anti_keyword in name for anti_keyword in anti_keywords):
                dprint(f"Anti-Keyword: {anti_keywords} in {name}", is_deep=True)
                continue
            item = item.split(" ; ")[0]
        
        if " " in item:
            if all(keyword in name for keyword in item.split()):
                dprint(f"Keyword: {item} in {name}", is_deep=True)
                return (True, old_item)
        elif mode == "==":
            if any(item == name_part for name_part in name):
                dprint(f"Keyword: {item} in {name}", is_deep=True)
                return (True, old_item)
        else:
            if any(item in name_part for name_part in name):
                dprint(f"Keyword: {item} in {name}", is_deep=True)
                return (True, old_item)

    dprint(f"Keyword: None in {name}", is_deep=True)
    return (False, None)

def get_resource_path() -> str:
    Preferences = bpy.context.preferences.addons[__package__].preferences
    if Preferences.dev_tools and os.path.exists(Preferences.dev_packs_path) and Preferences.enable_custom_packs_path:
        resource_packs_directory = Preferences.dev_packs_path
    else:
        resource_packs_directory = os.path.join(main_directory, "Resource Packs")
    
    return resource_packs_directory

def override_setting(setting_name: str, default_value: str) -> bool:
    settings_override_path = os.path.join(os.path.dirname(main_directory), "settings_override.json")
    if os.path.exists(settings_override_path):
        with open(settings_override_path, "r") as file:
            data = json.load(file)
            return data.get(setting_name, default_value)
    
    return default_value

def get_pack_info_properties(pack: str =None) -> dict:
    resource_packs_directory = get_resource_path()
    with open(os.path.join(resource_packs_directory, "packs_info.json"), "r") as file:
        data = json.load(file)
        
        if pack is None:
            return data.keys()
        
        pack_list = data.get(pack, {})
        pack_info = {"mc_version": pack_list.get("mc_version", None), "pack_version": pack_list.get("pack_version", None), "type": pack_list.get("type", None), "link": pack_list.get("link", None)}
    return pack_info

def EmissionMode(PBSDF, texture_name: str) -> int:

    Preferences = bpy.context.preferences.addons[__package__].preferences
    
    if Preferences.emissiondetection == 'Automatic & Manual' and (PBSDF.inputs["Emission Strength"].default_value != 0 or name_in(Emissive_Materials.keys(), texture_name)[0]):
        return 1

    elif Preferences.emissiondetection == 'Automatic' and PBSDF.inputs["Emission Strength"].default_value != 0:
        return 2
    
    elif Preferences.emissiondetection == 'Manual' and name_in(Emissive_Materials.keys(), texture_name)[0]:
        return 3
    
    return 0

def create_node_group(place, node_tree_name : str, location : tuple = (0, 0), file : str = nodes_file, name : str ="", exists_check : bool = False):
    if exists_check:
        for node in place:
            if node.type == "GROUP" and node.node_tree.name == node_tree_name:
                return node
        
    if node_tree_name not in bpy.data.node_groups:
        try:
            with bpy.data.libraries.load(file, link=False) as (data_from, data_to):
                data_to.node_groups = [node_tree_name]
        except Exception as error:
            Call_AS("e03", file, error)

    group_node = place.new(type='ShaderNodeGroup')
    if name != "":
        group_node.name = name
    
    group_node.node_tree = bpy.data.node_groups[node_tree_name]
    group_node.location = location

    return group_node

def detect_obj_type(obj_name: str = "", mat_name: str = "") -> str:

    if "item" in obj_name or "item" in mat_name or bpy.data.objects[obj_name].get("MiBlend ID", None) == "item": # Add check in the pack_info.json
        dprint(f"{obj_name}; {mat_name} is an item", is_deep=True, zone="rp")
        return "item"
    
    elif "block" in obj_name or "block" in mat_name or bpy.data.objects[obj_name].get("MiBlend ID", None) == "block":
        dprint(f"{obj_name}; {mat_name} is a block", is_deep=True, zone="rp")
        return "block"
    
    elif "entity" in obj_name or "entity" in mat_name or bpy.data.objects[obj_name].get("MiBlend ID", None) == "entity":
        dprint(f"{obj_name}; {mat_name} is a entity", is_deep=True, zone="rp")
        return "entity"
    
    dprint(f"{obj_name}; {mat_name} is unknown", is_deep=True, zone="rp")
    return "unknown"

def format_texture_name(texture_name: str, split: bool =True) -> str:
    if split:
        return detect_duplicate_index(texture_name).replace(".png", "").lower().replace("-", "_").split("_")
    else:
        return detect_duplicate_index(texture_name).replace(".png", "").lower().replace("-", "_")

def format_material_name(material_name: str, split: bool =True) -> str:
    if split:
        return detect_duplicate_index(material_name).lower().replace("-", "_").split("_")
    else:
        return detect_duplicate_index(material_name).lower().replace("-", "_")

def dprint(*messages: str, is_deep: bool =False, zone: str =None, separate: bool =False):
    try:
        Preferences = bpy.context.preferences.addons[__package__].preferences
        zones_dict = {"uas": Preferences.uas_debug_mode, "rp": Preferences.rp_debug_mode, "fw": Preferences.fw_debug_mode, "fm": Preferences.fm_debug_mode, "ui": Preferences.ui_debug_mode}
        
        if not Preferences.dev_tools or not Preferences.dprint:
            return
        
        if zone and zones_dict.get(zone, False) == False:
            return
            
        if is_deep and not Preferences.deep_debug:
            return
            
        if separate:
            for message in messages:
                print(message)
        else:
            print(*messages)
            
    except Exception as e:
        print(f"Debug print error: {str(e)}")

def isduplicate(text: str, original_text: str=None) -> bool:
    parts = text.split(".")
    if len(parts) > 1 and parts[-1].isdigit():
        base_text = text.replace(f".{parts[-1]}", "")
        if original_text:
            return base_text == original_text
        else:
            return True
    return False

def detect_duplicate_index(text: str, original_text: str=None):
    parts = text.split(".")
    if len(parts) > 1 and parts[-1].isdigit():
        base_text = text.replace(f".{parts[-1]}", "")
        if original_text:
            if base_text == original_text:
                return base_text
        else:
            return base_text
    return text

def is_gray(name: str, is_material: bool =False, mode: str ="all"):

    if mode == "all":
        return (name_in(gray_blocks.get("vegetation"), name, not is_material) or name_in(gray_blocks.get("redstone"), name, not is_material) or name_in(gray_blocks.get("water"), name, not is_material))[0]
    elif mode == "vegetation":
        return name_in(gray_blocks.get("vegetation"), name, not is_material)[0]
    elif mode == "redstone":
        return name_in(gray_blocks.get("redstone"), name, not is_material)[0]
    elif mode == "water":
        return name_in(gray_blocks.get("water"), name, not is_material)[0]
    return False

def detect_texture_node(PBSDF):

    def get_all_linked_nodes(PBSDF):
        linked_nodes = []
        for input_name, input_socket in PBSDF.inputs.items():
            if input_socket.is_linked:
                for link in input_socket.links:
                    linked_nodes.append(link.from_node)
                    linked_nodes.extend(get_all_linked_nodes(link.from_node))
        return linked_nodes

    def get_linked_nodes(PBSDF, input_name):
        linked_nodes = []
        if input_name in PBSDF.inputs and PBSDF.inputs[input_name].is_linked:
            for link in PBSDF.inputs[input_name].links:
                linked_nodes.append(link.from_node)
                linked_nodes.extend(get_all_linked_nodes(link.from_node))
        return linked_nodes

    def traverse_nodes(PBSDF, input_name, visited=None):
        if visited is None:
            visited = set()
        
        if PBSDF in visited:
            return visited
        
        visited.add(PBSDF)
        
        linked_nodes = get_linked_nodes(PBSDF, input_name)
        for linked_node in linked_nodes:
            traverse_nodes(linked_node, input_name, visited)
        
        return visited
    
    connected_nodes = traverse_nodes(PBSDF, "Base Color")
    for n in connected_nodes:
        if n.type == "GROUP":
            if "Animated;" in n.node_tree.name:
                return n
                
        if n.type == "TEX_IMAGE" and n.image:
            return n
        
def detect_image_texture(PBSDF):

    def get_all_linked_nodes(PBSDF):
        linked_nodes = []
        for input_name, input_socket in PBSDF.inputs.items():
            if input_socket.is_linked:
                for link in input_socket.links:
                    linked_nodes.append(link.from_node)
                    linked_nodes.extend(get_all_linked_nodes(link.from_node))
        return linked_nodes

    def get_linked_nodes(PBSDF, input_name):
        linked_nodes = []
        if input_name in PBSDF.inputs and PBSDF.inputs[input_name].is_linked:
            for link in PBSDF.inputs[input_name].links:
                linked_nodes.append(link.from_node)
                linked_nodes.extend(get_all_linked_nodes(link.from_node))
        return linked_nodes

    def traverse_nodes(PBSDF, input_name, visited=None):
        if visited is None:
            visited = set()
        
        if PBSDF in visited:
            return visited
        
        visited.add(PBSDF)
        
        linked_nodes = get_linked_nodes(PBSDF, input_name)
        for linked_node in linked_nodes:
            traverse_nodes(linked_node, input_name, visited)
        
        return visited
    
    connected_nodes = traverse_nodes(PBSDF, "Base Color")
    for n in connected_nodes:
        if n.type == "GROUP":
            if "Animated;" in n.node_tree.name:
                return bpy.data.images.get(n.node_tree.name.replace("Animated; ", "") + ".png")
                
        if n.type == "TEX_IMAGE" and n.image:
            return n.image

def SeparateMeshByMaterial(obj, material = None):
    obj_name = obj.name

    if bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.select_all(action='DESELECT')

    if len(obj.material_slots) <= 1 or not obj.material_slots:
        return

    if material:
        if bpy.data.collections.get(obj_name.split('__')[0].replace("Main | ", "")) is None:
            new_collection = bpy.data.collections.new(obj_name.split("__")[0].replace("Main | ", ""))
            obj.users_collection[-1].children.link(new_collection)

            for col in obj.users_collection:
                col.objects.unlink(obj)

            new_collection.objects.link(obj)

        for i, mat in enumerate(obj.data.materials):
            if mat == material:
                bpy.context.object.active_material_index = i
                break

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.material_slot_select()
        bpy.ops.mesh.separate(type="SELECTED")
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = bpy.context.view_layer.objects.get(obj_name)
        if not obj.name.startswith("Main | "):
            obj.name = f"Main | {obj_name}"
        bpy.ops.object.material_slot_remove()
        new_obj = bpy.context.selected_objects[-1]
        bpy.context.view_layer.objects.active = new_obj
        bpy.ops.object.material_slot_remove_unused()
        new_obj.name = f"{material.name} | {obj_name.replace('Main | ', '')}"
    else:
        new_collection = bpy.data.collections.new(obj_name.split("__")[0].replace("Main | ", ""))
        obj.users_collection[-1].children.link(new_collection)

        for col in obj.users_collection:
            col.objects.unlink(obj)

        new_collection.objects.link(obj)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.separate(type="MATERIAL")
        bpy.ops.object.mode_set(mode='OBJECT')

        for new_obj in new_collection.objects:
            if new_obj in bpy.context.selected_objects and obj_name in new_obj.name:
                new_obj.name = f"{new_obj.material_slots[0].material.name} | {obj_name.replace('Main | ', '')}"

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.update()

    return new_obj

def Perf_Time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time > 0.001 and bpy.context.preferences.addons[__package__].preferences.dev_tools and bpy.context.preferences.addons[__package__].preferences.perf_time:
            dprint(f"{func.__name__}() took {end_time - start_time:.4f} seconds to complete.")
    return wrapper

def GetConnectedSocketFrom(output: str, node):
    try:
        output_socket = node.outputs.get(output)

        if not output_socket:
            return None
        
        if not output_socket.is_linked:
            return None
        
        return [link.to_socket for link in output_socket.links]
    except Exception as error:
        Call_AS("n00", error)

def GetConnectedSocketTo(input: Union[str, int], node):
    try:
        if isinstance(input, int):
            if input >= len(node.inputs):
                return None
            else:
                input_socket = node.inputs[input]
        else:
            input_socket = node.inputs.get(input, None)
        
        if not input_socket:
            return None
        
        if not input_socket.is_linked:
            return None
        
        link = input_socket.links[0]
        return link.from_socket
    except Exception as error:
        Call_AS("n00", error)

def RemoveLinksFrom(sockets):
    try:
        for socket in sockets:
            for link in socket.links:
                socket.node.id_data.links.remove(link)
    except:
        for link in sockets.links:
            sockets.node.id_data.links.remove(link)

def blender_version(blender_version: str) -> bool:
    try:
        version_parts = blender_version.split(" ")
        if len(blender_version.split()) != 1:
            
            operator = version_parts[0]
            major, minor, patch = version_parts[1].lower().split(".")
            version = (int(major), int(minor), int(patch))
            return {
                '<': bpy.app.version < version,
                '<=': bpy.app.version <= version,
                '>': bpy.app.version > version,
                '>=': bpy.app.version >= version,
                '==': bpy.app.version == version,
            }.get(operator, False)
        else:
            version_parts = blender_version.lower().split(".")
            major, minor, patch = version_parts
            major_c = bpy.app.version[0] == int(major) if major != "x" else True
            minor_c = bpy.app.version[1] == int(minor) if minor != "x" else True
            patch_c = bpy.app.version[2] == int(patch) if patch != "x" else True
            return major_c and minor_c and patch_c
    except ValueError:
        return False