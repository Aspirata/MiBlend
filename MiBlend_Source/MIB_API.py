from MiBlend_Source.Data import *
from MiBlend_Source.Utils.Absolute_Solver import Absolute_Solver
import time

def PBSDF_compability(Input: str) -> str:
    if Input == "Subsurface Weight" and blender_version("< 4.0.0"):
        return "Subsurface"
    
    if Input == "Subsurface Radius" and blender_version("< 4.0.0"):
        return "Subsurface Color"
    
    if Input == "Specular IOR Level" and blender_version("< 4.0.0"):
        return "Specular"
    
    if Input == "Transmission Weight" and blender_version("< 4.0.0"):
        return "Transmission"

    if Input == "Coat Weight" and blender_version("< 4.0.0"):
        return "Coat"
    
    if Input == "Sheen Weight" and blender_version("< 4.0.0"):
        return "Sheen"
    
    if Input == "Emission Color" and blender_version("< 4.0.0"):
        return "Emission"
    return Input

def MaterialIn(Array, material, mode="in"):
    for material_part in material.name.lower().replace("-", ".").split("."):
        for keyword in Array:
            if mode == "==":
                if keyword == material_part:
                    return True
            else:
                if keyword in material_part:
                    return True

    return False

def SeparateMeshBy(mode, obj, materal = None):
    obj = bpy.context.active_object

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')

    if mode == "SELECTED" and materal:
        for i, material in enumerate(obj.data.materials):
            bpy.ops.object.material_slot_select()
            bpy.ops.mesh.separate(type=mode)
            
            if i > 0:
                new_obj = bpy.data.objects.get(obj.name + f".{i:03}")
            else:
                new_obj = bpy.data.objects.get(obj.name)
                
            new_obj.name = f"{material.name} | {obj.name}"

    elif mode == "MATERIAL":
        bpy.ops.mesh.separate(type=mode)
            
    bpy.ops.object.mode_set(mode='OBJECT')

def EmissionMode(PBSDF, material):
        from .Data import Emissive_Materials
        
        Preferences = bpy.context.preferences.addons[__package__].preferences
                
        if Preferences.emissiondetection == 'Automatic & Manual' and (PBSDF.inputs["Emission Strength"].default_value != 0 or MaterialIn(Emissive_Materials.keys(), material, "==")):
            return 1

        if Preferences.emissiondetection == 'Automatic' and PBSDF.inputs["Emission Strength"].default_value != 0:
            return 2
        
        if Preferences.emissiondetection == 'Manual' and MaterialIn(Emissive_Materials.keys(), material, "=="):
            return 3

def format_texture_name(texture_name):
    return texture_name.lower().replace("-", "_").split("_")

def format_material_name(material_name):
    return material_name.lower().replace("-", "_").split(".")

def dprint(message):
    if bpy.context.preferences.addons[__package__].preferences.dev_tools and bpy.context.preferences.addons[__package__].preferences.dprint:
        print(message)

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

def blender_version(blender_version: str, debug=None) -> bool:
    
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

        if debug is not None:
            print(f"------\nmajor = {major} \nmajor_c = {major_c} \nminor = {minor} \nminor_c = {minor_c} \npatch = {patch} \npatch_c = {patch_c}\n------")
        
        return major_c and minor_c and patch_c
    
    except:
        version_parts = blender_version.split(" ")
        operator = version_parts[0]
        major, minor, patch = version_parts[1].lower().split(".")
        version = (int(major), int(minor), int(patch))
        
        if debug is not None:
            print(f"{bpy.app.version} {operator} {version}")

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