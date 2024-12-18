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
    parts = texture_name.split(".")
    if len(parts) > 1 and parts[-1].isdigit():
        texture_name.replace(parts[-1], "")

    return texture_name.replace(".png", "").lower().replace("-", "_").split("_") if split else texture_name.replace(".png", "").lower().replace("-", "_")

def format_material_name(material_name, split=True):
    parts = material_name.split(".")
    if len(parts) > 1 and parts[-1].isdigit():
        material_name.replace(parts[-1], "")
    
    return material_name.lower().replace("-", "_").split("_") if split else material_name.lower().replace("-", "_")

def dprint(message):
    if bpy.context.preferences.addons[__package__].preferences.dev_tools and bpy.context.preferences.addons[__package__].preferences.dprint:
        print(message)

def isdublicate(text, original_text=None):
    parts = text.split(".")
    return len(parts) > 1 and parts[-1].isdigit() and (text.replace("." + str(parts[-1]), "") == original_text if original_text != None else True)

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

def EmissionMode(PBSDF, texture_name):
        from .Data import Emissive_Materials

        def TextureIn(Array, texture):
            for texture_name in Array:
                if texture_name == format_texture_name(texture, split=False):
                    return True
            return False
        
        Preferences = bpy.context.preferences.addons[__package__].preferences
                
        if Preferences.emissiondetection == 'Automatic & Manual' and (PBSDF.inputs["Emission Strength"].default_value != 0 or TextureIn(Emissive_Materials.keys(), texture_name)):
            return 1

        if Preferences.emissiondetection == 'Automatic' and PBSDF.inputs["Emission Strength"].default_value != 0:
            return 2
        
        if Preferences.emissiondetection == 'Manual' and TextureIn(Emissive_Materials.keys(), texture_name):
            return 3

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
        
        return major_c and minor_c and patch_c
    
    except:
        version_parts = blender_version.split(" ")
        operator = version_parts[0]
        major, minor, patch = version_parts[1].lower().split(".")
        version = (int(major), int(minor), int(patch))

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