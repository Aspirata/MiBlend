from MiBlend_Source.Data import *
from MiBlend_Source.Utils.Absolute_Solver import Absolute_Solver
from typing import Optional, Union
import time
import sys

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

def clamp(min_value, value, max_value):
    return max(min_value, min(value, max_value))

def MaterialIn(Array, material, mode="in"):
    material_name = format_material_name(material.name)
    for item in Array:
        if ";" in item:
            anti_keywords = item.split(" ; ")[1].split()
            if any(anti_keyword in material_name for anti_keyword in anti_keywords):
                continue
            item = item.split(" ; ")[0]
        
        if " " in item:
            for keyword in item.split():
                dprint(keyword, material_name, keyword in material_name)
            if all(keyword in material_name for keyword in item.split()):
                return (True, item)
        elif mode == "==":
            for material_part in material_name:
                dprint(item, material_part, item == material_part)

            if any(item == material_part for material_part in material_name):
                return (True, item)
        else:
            for material_part in material_name:
                dprint(item, material_part, item in material_part)

            if any(item in material_part for material_part in material_name):
                return (True, item)

    return (False, None)

def TextureIn(Array, texture, mode="=="):
    texture_name = format_texture_name(texture)
    for item in Array:
        if ";" in item:
            anti_keywords = item.split(" ; ")[1].split()
            if any(anti_keyword in texture_name for anti_keyword in anti_keywords):
                continue
            item = item.split(" ; ")[0]
        
        if " " in item:
            if all(keyword in texture_name for keyword in item.split()):
                return (True, item)
        elif mode == "==":
            if any(item == texture_part for texture_part in texture_name):
                return (True, item)
        else:
            if any(item in texture_part for texture_part in texture_name):
                return (True, item)

    return False
def EmissionMode(PBSDF, texture_name):
        from .Data import Emissive_Materials

        Preferences = bpy.context.preferences.addons[__package__].preferences
                
        if Preferences.emissiondetection == 'Automatic & Manual' and (PBSDF.inputs["Emission Strength"].default_value != 0 or TextureIn(Emissive_Materials.keys(), texture_name)):
            return 1

        elif Preferences.emissiondetection == 'Automatic' and PBSDF.inputs["Emission Strength"].default_value != 0:
            return 2
        
        elif Preferences.emissiondetection == 'Manual' and TextureIn(Emissive_Materials.keys(), texture_name):
            return 3

def create_node_group(place, node_tree_name : str, location : tuple = (0, 0), file : str = nodes_file, name : str ="", exists_check : bool = False):
    if exists_check:
        for node in place:
            if node.type == "GROUP" and node.node_tree.name == node_tree_name:
                return node
        
    if node_tree_name not in bpy.data.node_groups:
        try:
            with bpy.data.libraries.load(file, link=False) as (data_from, data_to):
                data_to.node_groups = [node_tree_name]
        except:
            Absolute_Solver("004", "Nodes", traceback.format_exc())

    group_node = place.new(type='ShaderNodeGroup')
    if name != "":
        group_node.name = name
    
    group_node.node_tree = bpy.data.node_groups[node_tree_name]
    group_node.location = location

    return group_node

def detect_obj_type(obj_name: str = "", mat_name: str = "") -> str:

    if "item" in obj_name or "item" in mat_name or bpy.data.objects[obj_name].get("MiBlend ID", None) == "item": # Add check in the pack_info.json
        #dprint(f"{obj_name}; {mat_name} is an item")
        return "item"
    
    elif "block" in obj_name or "block" in mat_name or bpy.data.objects[obj_name].get("MiBlend ID", None) == "block":
        #dprint(f"{obj_name}; {mat_name} is a block")
        return "block"
    
    elif "entity" in obj_name or "entity" in mat_name or bpy.data.objects[obj_name].get("MiBlend ID", None) == "entity":
        #dprint(f"{obj_name}; {mat_name} is a entity")
        return "entity"
    
    dprint(f"{obj_name}; {mat_name} is unknown")
    return "unknown"

def format_texture_name(texture_name, split=True):
    if split:
        return detect_duplicate_index(texture_name).replace(".png", "").lower().replace("-", "_").split("_")
    else:
        return detect_duplicate_index(texture_name).replace(".png", "").lower().replace("-", "_")

def format_material_name(material_name, split=True):
    if split:
        return detect_duplicate_index(material_name).lower().replace("-", "_").split("_")
    else:
        return detect_duplicate_index(material_name).lower().replace("-", "_")

def dprint(*messages, separate=False):
    if bpy.context.preferences.addons[__package__].preferences.dev_tools and bpy.context.preferences.addons[__package__].preferences.dprint:
        if separate:
            for message in messages:
                print(message)
        else:
            print(*messages)

def isduplicate(text, original_text=None):
    parts = text.split(".")
    if len(parts) > 1 and parts[-1].isdigit():
        base_text = text.replace(f".{parts[-1]}", "")
        if original_text:
            return base_text == original_text
        else:
            return True
    return False

def detect_duplicate_index(text, original_text=None):
    parts = text.split(".")
    if len(parts) > 1 and parts[-1].isdigit():
        base_text = text.replace(f".{parts[-1]}", "")
        if original_text:
            if base_text == original_text:
                return base_text
        else:
            return base_text
    return text

def isgray(name, is_material=False, mode="all"):
    name_parts = format_texture_name(name) if not is_material else format_material_name(name)
    if mode == "all":
        if any(part in name_parts for part in ("grass", "water", "leaves", "lily", "vine", "fern")) and all(part not in name_parts for part in ("cherry", "side", "azalea", "snow", "mushroom")) or \
            ("redstone" in name_parts and "dust" in name_parts) or ("pink" in name_parts and "stem" in name_parts):
            return True
    elif mode == "vegetation":
        if any(part in name_parts for part in ("grass", "leaves", "lily", "vine", "fern")) and all(part not in name_parts for part in ("cherry", "side", "azalea", "snow", "mushroom")):
            return True
    elif mode == "redstone":
        if "redstone" in name_parts and "dust" in name_parts:
            return True
    elif mode == "water":
        if "water" in name_parts:
            return True
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
    except:
        Absolute_Solver("005", __name__, traceback.format_exc())

def GetConnectedSocketTo(input: Union[str, int], node):
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