from .Data import *

def PBSDF_compability(Input):
    if Input == "Subsurface Weight" and blender_version("< 4.0.0"):
        return "Subsurface"
    
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

def EmissionMode(PBSDF, material):
        from .Data import Emissive_Materials
        
        Preferences = bpy.context.preferences.addons[__package__].preferences
                
        if Preferences.emissiondetection == 'Automatic & Manual' and (PBSDF.inputs["Emission Strength"].default_value != 0 or MaterialIn(Emissive_Materials.keys(), material, "==")):
            debugger(Emissive_Materials.keys())
            return 1

        if Preferences.emissiondetection == 'Automatic' and PBSDF.inputs["Emission Strength"].default_value != 0:
            return 2
        
        if Preferences.emissiondetection == 'Manual' and MaterialIn(Emissive_Materials.keys(), material, "=="):
            return 3

def debugger(message):
    if bpy.context.preferences.addons[__package__].preferences.dev_tools:
        print(message)

def GetConnectedSocketFrom(output, tag, material=None):
    try:
        to_sockets = []
        if material is not None:
            for node in material.node_tree.nodes:
                if node.type == tag:
                    output_socket = node.outputs[output]
                    for link in output_socket.links:
                        to_node = link.to_node
                        to_sockets.append(link.to_socket)
            return to_sockets
        
        else:
            output_socket = tag.outputs[output]
            for link in output_socket.links:
                to_node = link.to_node
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

def GetConnectedSocketTo(input, tag, material=None):
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

def blender_version(blender_version, debug=None):
    
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