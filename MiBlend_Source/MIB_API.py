from .Data import *
from .Utils.Absolute_Solver import Call_AS
from typing import Optional, Union
import time
import sys
import re

def PBSDF_compability(Input: str) -> str:
    if blender_version("< 4.0.0"):
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

def is_unix_system() -> bool:
    return "linux" in sys.platform or "darwin" in sys.platform

def clamp(min_value: Union[int, float], value: Union[int, float], max_value: Union[int, float]) -> Union[int, float]:
    return max(min_value, min(value, max_value))

def is_mesh(object: object) -> bool:
    return object.type == "MESH"

def get_selected_asset() -> dict:
    current_index = bpy.context.scene.miblend_properties.assets_properties.asset_index
    items = bpy.context.scene.miblend_properties.assets_properties.asset_items
    
    try:
        return items[current_index]
    except Exception as error:
        if current_index < 0 or current_index >= len(items):
            Call_AS("e08", traceback.format_exc())
        else:
            Call_AS("n00", traceback.format_exc())

# Checks if the version_name is a valid version number and returns the formatted version number else returns None
def mc_version_formatter(version_name: str) -> Optional[str]:
    try:
        version_parts = re.split(r'[ -]', version_name)
        for part in version_parts:
            if not any(char.isalpha() for char in part) and re.match(r'^\d{1}\.\d{1,2}(?:\.\d{1,2})?$', part):
                return part
        return None
    except Exception as error:
        Call_AS("n00", error)

# Checks if material_or_texture_name in Array return (True, item in the list) else (False, None)
# Array filters: " ; " - not, " " - and
def name_in(Array: list, material_or_texture_name: str, is_texture=False, mode="in") -> tuple[bool, Optional[str]]:
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
            else:
                dprint(f"Keyword: {item} not in {name}", is_deep=True)

    dprint(f"Keyword: None in {name}", is_deep=True)
    return (False, None)

def get_resource_path() -> str:
    Preferences = bpy.context.preferences.addons[__package__].preferences
    if Preferences.dev_tools and os.path.exists(Preferences.dev_packs_path) and Preferences.enable_custom_packs_path:
        resource_packs_directory = Preferences.dev_packs_path
    else:
        resource_packs_directory = os.path.join(main_directory, "Resource Packs")
    
    return resource_packs_directory

def override_setting(setting_name: str, default_value: Union[str, bool, int, float]) -> Union[str, bool, int, float]:
    settings_override_path = os.path.join(os.path.dirname(main_directory), "settings_override.json")
    if os.path.exists(settings_override_path):
        with open(settings_override_path, "r") as file:
            data = json.load(file)
            return data.get(setting_name, default_value)
    
    return default_value

def get_pack_info_properties(pack: str =None) -> dict:
    resource_packs_directory = get_resource_path()
    if not os.path.exists(resource_packs_directory):
        return {}
    
    with open(os.path.join(resource_packs_directory, "packs_info.json"), "r") as file:
        data = json.load(file)
        
        if pack is None:
            return data.keys()
        
        return data.get(pack, {})
    return pack_info

def is_code_ignored(code: str) -> bool:
    return code in bpy.context.scene.miblend_properties.absolute_solver_properties.ignored_codes.split()

def EmissionMode(PBSDF: object, texture_name: str) -> int:

    Preferences = bpy.context.preferences.addons[__package__].preferences
    
    if Preferences.emissiondetection == 'Combined' and (PBSDF.inputs["Emission Strength"].default_value != 0 or name_in(Emissive_Materials.keys(), texture_name, True)[0]):
        return 1

    elif Preferences.emissiondetection == 'Automatic' and PBSDF.inputs["Emission Strength"].default_value != 0:
        return 2
    
    elif Preferences.emissiondetection == 'Manual' and name_in(Emissive_Materials.keys(), texture_name, True)[0]:
        return 3
    
    return 0

def add_modifier(object: object, modifier_type_or_node_group: str, modifier_name: str ="", file: str = nodes_file) -> object:
    # Check if modifier already exists
    if modifier_name:
        existing_modifier = object.modifiers.get(modifier_name)
        if existing_modifier:
            return existing_modifier

    # Handle built-in Blender modifiers
    if modifier_type_or_node_group.isupper():
        existing_modifier = next((mod for mod in object.modifiers if mod.type == modifier_type_or_node_group), None)
        if existing_modifier:
            return existing_modifier
        
        name = modifier_name if modifier_name else modifier_type_or_node_group
        modifier = object.modifiers.new(name, type=modifier_type_or_node_group)
    
    # Handle geometry node groups
    else:
        existing_modifier = next((mod for mod in object.modifiers if mod.type == "NODES" and mod.node_group.name == modifier_type_or_node_group), None)
        if existing_modifier:
            return existing_modifier
        
        if modifier_type_or_node_group not in bpy.data.node_groups:
            try:
                with bpy.data.libraries.load(file, link=False) as (data_from, data_to):
                    data_to.node_groups = [modifier_type_or_node_group]
            except Exception as error:
                Call_AS("e03", file, error)

        name = modifier_name if modifier_name else modifier_type_or_node_group
        modifier = object.modifiers.new(name, type='NODES')
        modifier.node_group = bpy.data.node_groups[modifier_type_or_node_group]
    
    return modifier

def get_collections(data: object = None) -> list:
    collections_list = []

    if not data:
        data = bpy.data

    def add_collection(collection, level=0):
        collections_list.append((collection.name, level))
        for child in collection.children:
            add_collection(child, level + 1)

    for collection in data.collections:
        add_collection(collection)

    return collections_list

def create_node_group(place: object, node_tree_name: str, location: tuple = (0, 0), file: str = nodes_file, exists_check: bool = False, name: str ="") -> object:
    # Check for existing node group if requested
    if exists_check:
        existing_node = next((node for node in place.node_tree.nodes if node.type == "GROUP" and node.node_tree.name == node_tree_name), None)
        if existing_node:
            return existing_node
    
    # Load node group if not already in data
    if node_tree_name not in bpy.data.node_groups:
        try:
            with bpy.data.libraries.load(file, link=False) as (data_from, data_to):
                data_to.node_groups = [node_tree_name]
        except Exception as error:
            Call_AS("e03", file, error)

    # Create and configure new node
    group_node = place.node_tree.nodes.new(type='ShaderNodeGroup')
    if name:
        group_node.name = name
    
    group_node.node_tree = bpy.data.node_groups[node_tree_name]
    group_node.location = location

    return group_node

def detect_obj_type(obj_name: str = "", mat_name: str = "") -> str:
    obj = bpy.data.objects.get(obj_name)
    if obj is None or not is_mesh(obj):
        dprint(f"Object {obj_name} not found", is_deep=True, zone="rp")
        return "unknown"

    miblend_id = obj.get("MiBlend ID", "")
    obj_name_lower = obj_name.lower()
    mat_name_lower = mat_name.lower()
    exporter = detect_world_exporter(obj)

    if "entity" in obj_name_lower or "entity" in mat_name_lower or miblend_id == "entity":
        dprint(f"{obj_name}; {mat_name} is an entity", is_deep=True, zone="rp")
        return "entity"

    elif exporter != "unknown" or "block" in obj_name_lower or "block" in mat_name_lower or miblend_id == "block":
        dprint(f"{obj_name}; {mat_name} is a block", is_deep=True, zone="rp")
        return "block"

    elif "item" in obj_name_lower or "item" in mat_name_lower or miblend_id == "item":
        dprint(f"{obj_name}; {mat_name} is an item", is_deep=True, zone="rp")
        return "item"
    
    dprint(f"{obj_name}; {mat_name} is unknown", is_deep=True, zone="rp")
    return "unknown"

def format_texture_name(texture_name: str, split: bool =True) -> str:
    if split:
        return format_duplicate_name(texture_name).replace(".png", "").lower().replace("-", "_").split("_")
    else:
        return format_duplicate_name(texture_name).replace(".png", "").lower().replace("-", "_")

def format_material_name(material_name: str, split: bool =True) -> str:
    if split:
        return format_duplicate_name(material_name).lower().replace("-", "_").split("_")
    else:
        return format_duplicate_name(material_name).lower().replace("-", "_")

def find_node(place: object, type_or_node_group_name: str) -> Optional[object]:
    nodes_list = place.node_tree.nodes
    if type_or_node_group_name.isupper():
        matching_node = next((node for node in nodes_list if node.type == type_or_node_group_name), None)
    else:
        matching_node = next((node for node in nodes_list if node.type == "GROUP" and node.node_tree.name == type_or_node_group_name), None)
    
    return matching_node

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
        
        print(*messages, sep="\n" if separate else "")
            
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

def format_duplicate_name(text: str, original_text: str=None) -> str:
    parts = text.split(".")
    if len(parts) > 1 and parts[-1].isdigit():
        base_text = text.replace(f".{parts[-1]}", "")
        if original_text:
            if base_text == original_text:
                return base_text
        else:
            return base_text
    return text

def is_gray(name: str, is_material: bool =False, mode: str ="all") -> bool:
    #dprint(f'{format_material_name(name)} vegetation: {name_in(gray_blocks.get("vegetation"), name, not is_material)} \nrednstone: {name_in(gray_blocks.get("redstone"), name, not is_material)} \nwater: {name_in(gray_blocks.get("water"), name, not is_material)}', is_deep=True, zone="fw")
    result = False
    if mode == "all":
        result = name_in(gray_blocks.get("vegetation"), name, not is_material)[0]
        result += name_in(gray_blocks.get("redstone"), name, not is_material)[0]
        result += name_in(gray_blocks.get("water"), name, not is_material)[0]
    elif mode == "vegetation":
        result = name_in(gray_blocks.get("vegetation"), name, not is_material)[0]
    elif mode == "redstone":
        result = name_in(gray_blocks.get("redstone"), name, not is_material)[0]
    elif mode == "water":
        result = name_in(gray_blocks.get("water"), name, not is_material)[0]
    
    return bool(result)

def detect_texture_node(PBSDF: object) -> object:

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
        
def get_nodes_list(material_or_node_group: object, is_recursive: bool =False) -> list:
    nodes_list = []
    
    if hasattr(material_or_node_group, 'use_nodes') and not material_or_node_group.use_nodes:
        return []

    for node in material_or_node_group.node_tree.nodes:
        nodes_list.append(node)
        if node.type == 'GROUP' and node.node_tree and is_recursive:
            nodes_list.extend(get_nodes_list(node))

    return nodes_list
        
def detect_image_texture(PBSDF: object) -> object:

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

def detect_world_exporter(world_obj: object) -> str:
    exporter = "unknown"

    if not world_obj.data.materials:
        return exporter
        
    for mat in world_obj.data.materials:
        mat_name = mat.name
        if mat_name.startswith("MAT_"):
            exporter = "miex"
            break
        elif "MWO" in mat_name or mat_name.count('-') == 0:
            exporter = "mineways"
            break
        elif mat_name.count('-') == 1:
            exporter = "jmc2obj"
            break
    
    dprint(f"Detected {exporter} exporter for {world_obj.name}", is_deep=True)
    return exporter

def SeparateMeshByMaterial(obj: object, material: object = None) -> object:
    try:
        obj_name = obj.name if obj.name.split('__')[0] else "World" + obj.name
        new_obj = None

        # Ensure we're in object mode
        if bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Early return if separation not needed
        if len(obj.material_slots) <= 1 or not obj.material_slots:
            return obj

        # Setup selection
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Create collection if needed
        collection_name = obj_name.split('__')[0].replace("Main | ", "") or "World"
        collection = bpy.data.collections.get(collection_name)
        if not collection:
            collection = bpy.data.collections.new(collection_name)
            obj.users_collection[-1].children.link(collection)
            
            # Move object to new collection
            for col in obj.users_collection:
                col.objects.unlink(obj)
            collection.objects.link(obj)

        if material:
            # Separate specific material
            for i, mat in enumerate(obj.data.materials):
                if mat == material:
                    bpy.context.object.active_material_index = i
                    break

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.object.material_slot_select()
            bpy.ops.mesh.separate(type="SELECTED")
            bpy.ops.object.mode_set(mode='OBJECT')

            # Find separated object
            new_obj = next((o for o in bpy.context.selected_objects if o != obj), None)
            if new_obj:
                # Clean up original object
                bpy.context.view_layer.objects.active = obj
                if not obj.name.startswith("Main | "):
                    obj.name = f"Main | {obj_name}"
                bpy.ops.object.material_slot_remove()

                # Setup new object
                bpy.context.view_layer.objects.active = new_obj
                bpy.ops.object.material_slot_remove_unused()
                new_obj.name = f"{material.name} | {obj_name.replace('Main | ', '')}"

        else:
            # Separate all materials
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.separate(type="MATERIAL")
            bpy.ops.object.mode_set(mode='OBJECT')

            # Rename separated objects
            for new_obj in collection.objects:
                if new_obj in bpy.context.selected_objects and obj_name in new_obj.name:
                    mat_name = new_obj.material_slots[0].material.name if new_obj.material_slots else "Unknown"
                    new_obj.name = f"{mat_name} | {obj_name.replace('Main | ', '')}"

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.update()
        
        return new_obj

    except Exception as error:
        Call_AS("n00", str(error))
        return None

def Perf_Time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time > 0.001 and bpy.context.preferences.addons[__package__].preferences.dev_tools and bpy.context.preferences.addons[__package__].preferences.perf_time:
            dprint(f"{func.__name__}() took {end_time - start_time:.4f} seconds to complete.")
    return wrapper

def GetConnectedSocketFrom(output: str, node: object) -> list:
    try:
        output_socket = node.outputs.get(output)

        if not output_socket:
            return None
        
        if not output_socket.is_linked:
            return None
        
        return [link.to_socket for link in output_socket.links]
    except Exception as error:
        Call_AS("n00", error)

def GetConnectedSocketTo(input: Union[str, int], node: object) -> Optional[object]:
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

def RemoveLinksFrom(sockets: object):
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