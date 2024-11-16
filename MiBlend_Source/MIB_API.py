from MiBlend_Source.Data import *
from MiBlend_Source.Utils.Absolute_Solver import Absolute_Solver
from typing import Optional
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

def safe_check(condition):
    try:
        return condition
    except:
        return False

def convert_to_linux(path):
    if sys.platform.startswith('linux'):
        return path.replace("\\", "/")
    return path

def MaterialIn(Array, material, mode="in"):
    for material_part in format_material_name(material.name):
        for keyword in Array:
            if mode == "==":
                return keyword == material_part
            else:
                return keyword in material_part
    return False

def detect_obj_type(obj_name: str = "", mat_name: str = "") -> str:

    if "item" in obj_name or "item" in mat_name or bpy.data.objects[obj_name].get("MiBlend ID", None) == "item":
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

def format_texture_name(texture_name):
    parts = texture_name.split(".")
    if len(parts) > 1 and parts[-1].isdigit():
        texture_name.replace(parts[-1], "")

    return texture_name.replace(".png", "").lower().replace("-", "_").split("_")

def format_material_name(material_name):
    parts = material_name.split(".")
    if len(parts) > 1 and parts[-1].isdigit():
        material_name.replace(parts[-1], "")
    
    return material_name.lower().replace("-", "_").split(".")

def dprint(message):
    if bpy.context.preferences.addons[__package__].preferences.dev_tools and bpy.context.preferences.addons[__package__].preferences.dprint:
        print(message)

def isdublicate(text, original_text=None):
    parts = text.split(".")
    return len(parts) > 1 and parts[-1].isdigit() and (text.replace("." + str(parts[-1]), "") == original_text if original_text != None else True)

def detect_texture_node(node):

    def get_all_linked_nodes(node):
        linked_nodes = []
        for input_name, input_socket in node.inputs.items():
            if input_socket.is_linked:
                for link in input_socket.links:
                    linked_nodes.append(link.from_node)
                    linked_nodes.extend(get_all_linked_nodes(link.from_node))
        return linked_nodes

    def get_linked_nodes(node, input_name):
        linked_nodes = []
        if input_name in node.inputs and node.inputs[input_name].is_linked:
            for link in node.inputs[input_name].links:
                linked_nodes.append(link.from_node)
                linked_nodes.extend(get_all_linked_nodes(link.from_node))
        return linked_nodes

    def traverse_nodes(node, input_name, visited=None):
        if visited is None:
            visited = set()
        
        if node in visited:
            return visited
        
        visited.add(node)
        
        linked_nodes = get_linked_nodes(node, input_name)
        for linked_node in linked_nodes:
            traverse_nodes(linked_node, input_name, visited)
        
        return visited
    
    connected_nodes = traverse_nodes(node, "Base Color")
    for n in connected_nodes:
        if n.type == "TEX_IMAGE" and n.image:
            return n

def SeparateMeshByMaterial(obj, materal = None):
    obj_name = obj.name

    if len(obj.material_slots) <= 1 or not obj.material_slots:
        return

    if materal:
        return NotImplemented
    
        for i, material in enumerate(obj.data.materials):
            bpy.ops.object.material_slot_select()
            bpy.ops.mesh.separate(type=mode)
            
            if i > 0:
                new_obj = bpy.data.objects.get(obj_name + f".{i:03}")
            else:
                new_obj = bpy.data.objects.get(obj_name)
                
            new_obj.name = f"{material.name} | {obj_name}"

    else:
        # Making new collection
        new_collection = bpy.data.collections.new(obj_name.split("__")[0])
        obj.users_collection[-1].children.link(new_collection)

        for col in obj.users_collection:
            col.objects.unlink(obj)
        
        new_collection.objects.link(obj)
        #

        bpy.ops.mesh.separate(type="MATERIAL")
        
        # Changing object names to material names
        for new_obj in new_collection.objects:
            if new_obj in bpy.context.selected_objects and obj_name in new_obj.name:
                new_obj.name = new_obj.material_slots[0]
                
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.update()

def EmissionMode(PBSDF, material):
        from .Data import Emissive_Materials
        
        Preferences = bpy.context.preferences.addons[__package__].preferences
                
        if Preferences.emissiondetection == 'Automatic & Manual' and (PBSDF.inputs["Emission Strength"].default_value != 0 or MaterialIn(Emissive_Materials.keys(), material, "==")):
            return 1

        if Preferences.emissiondetection == 'Automatic' and PBSDF.inputs["Emission Strength"].default_value != 0:
            return 2
        
        if Preferences.emissiondetection == 'Manual' and MaterialIn(Emissive_Materials.keys(), material, "=="):
            return 3

def Full_Perf_Time(func): # Not Implemented
    total_time = 0
    call_count = 0

    def wrapper(*args, **kwargs):
        nonlocal total_time, call_count
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        total_time += elapsed_time
        call_count += 1
        
    def print_final_stats():
        dprint(f"---------------- \nName: {func.__name__}() \nTotal Time: {total_time:.4f} \nAvg Time: {total_time / call_count} \n ----------------")

    atexit.register(print_final_stats)
    
    wrapper.total_time = lambda: total_time
    wrapper.call_count = lambda: call_count
    wrapper.average_time = lambda: total_time / call_count if call_count > 0 else 0

    return wrapper

def Perf_Time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time > 0.001 and bpy.context.preferences.addons[__package__].preferences.dev_tools and bpy.context.preferences.addons[__package__].preferences.perf_time:
            dprint(f"{func.__name__}() took {end_time - start_time:.4f} seconds to complete.")
    return wrapper

def GetConnectedSocketFrom(output, tag: str, material=None):
    try:
        to_sockets = []
        if material is not None:
            for node in material.node_tree.nodes:
                if node.type == tag:
                    output_socket = node.outputs[output]
                    for link in output_socket.links:
                        to_sockets.append(link.to_socket)
            return to_sockets
        
        else:
            output_socket = tag.outputs[output]
            for link in output_socket.links:
                to_sockets.append(link.to_socket)
            return to_sockets
    except:
        Absolute_Solver("005", __name__, traceback.format_exc())

def RemoveLinksFrom(sockets):
    try:
        for socket in sockets:
            for link in socket.links:
                socket.node.id_data.links.remove(link)
    except:
        for link in sockets.links:
            sockets.node.id_data.links.remove(link)

def GetConnectedSocketTo(input, tag: str, material=None):
    try:
        if material is not None:
            for node in material.node_tree.nodes:
                if node.type == tag:
                    input_socket = node.inputs[input]
                    for link in input_socket.links:
                        from_node = link.from_node
                        for output in from_node.outputs:
                            for link in output.links:
                                if link.to_socket.name == input_socket.name:
                                    return link.from_socket
        else:
            input_socket = tag.inputs[input]
            for link in input_socket.links:
                from_node = link.from_node
                for output in from_node.outputs:
                    for link in output.links:
                        if link.to_socket.name == input_socket.name:
                            return link.from_socket
    except:
        Absolute_Solver("005", __name__, traceback.format_exc())

def blender_version(blender_version: str) -> bool:
    
    try:
        version_parts = blender_version.lower().split(".")
        major, minor, patch = version_parts

        if major != "x":
            major_c = bpy.app.version[0] == int(major)
        else:
            major_c = True
            
        if minor != "x":
            minor_c = bpy.app.version[1] == int(minor)
        else:
            minor_c = True
            
        if patch != "x":
            patch_c = bpy.app.version[2] == int(patch)
        else:
            patch_c = True

        # print(f"------\nmajor = {major} \nmajor_c = {major_c} \nminor = {minor} \nminor_c = {minor_c} \npatch = {patch} \npatch_c = {patch_c}\n------")
        
        return major_c and minor_c and patch_c
    
    except:
        version_parts = blender_version.split(" ")
        operator = version_parts[0]
        major, minor, patch = version_parts[1].lower().split(".")
        version = (int(major), int(minor), int(patch))
        
        # print(f"{bpy.app.version} {operator} {version}")

        if operator == '<':
            return bpy.app.version < version
        elif operator == '<=':
            return bpy.app.version <= version
        elif operator == '>':
            return bpy.app.version > version
        elif operator == '>=':
            return bpy.app.version >= version
        elif operator == '==':
            return bpy.app.version == version
        else:
            return False