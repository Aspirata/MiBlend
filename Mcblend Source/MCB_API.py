from .Data import *

def InitOnStart():

    if "resource_packs" not in bpy.context.scene:
        bpy.context.scene["resource_packs"] = {}
        update_default_pack()
        
    items = bpy.context.scene.assetsproperties.asset_items
    items.clear()
    for category, assets in Assets.items():
        for key in assets.keys():
            item = items.add()
            item.name = key

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

def Absolute_Solver(error_code="None", data=None, tech_things="None", error_name=None, description=None, mode=None):
    Preferences = bpy.context.preferences.addons[__package__].preferences
    try:
        def GetASText(error_code, text):
            try:
                return Absolute_Solver_Errors[error_code][text]
            except:
                return None
        
        if error_code != None:
            error_name = GetASText(error_code, "Error Name")
        
        if description == None:
            description = GetASText(error_code, 'Description')

        try:
            mode = Absolute_Solver_Errors[error_code]["Mode"]
        except:
            mode = "Smart"

        if mode == Preferences.as_mode and Preferences.as_mode != "None":
            bpy.ops.special.absolute_solver('INVOKE_DEFAULT', Error_Code = error_code, Error_Name = error_name, Description = description.format(Data=data), Tech_Things = str(tech_things))
            
    except:
        bpy.ops.special.absolute_solver('INVOKE_DEFAULT', Error_Code = "000", Error_Name = GetASText("000", "Error Name"), Description = GetASText("000", 'Description', error_code if error_code != None else error_name), Tech_Things = str(traceback.format_exc()))

def checkconfig(name):
    if "const" in main_directory:
        return Preferences_List["Dev"][name]
    else:
        return Preferences_List["Default"][name]

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

def get_resource_packs(debug=None):
    if debug is not None:
        print(f"Resource Packs: {bpy.context.scene['resource_packs']}")

    return bpy.context.scene["resource_packs"]

def set_resource_packs(resource_packs, debug=None):
    bpy.context.scene["resource_packs"] = resource_packs

    if debug is not None:
        print(f"Resource Packs: {bpy.context.scene['resource_packs']}")

def update_default_pack(debug=None):
    resource_packs = bpy.context.scene["resource_packs"]

    default_pack = "Minecraft 1.20.6"
    default_path = os.path.join(resource_packs_directory, default_pack)
    resource_packs[default_pack] = {"path": (default_path), "type": "Texture", "enabled": True}

    default_pack = "Bare Bones 1.20.6"
    default_path = os.path.join(resource_packs_directory, default_pack)
    resource_packs[default_pack] = {"path": (default_path),"type": "Texture", "enabled": False}

    default_pack = "Better Emission"
    default_path = os.path.join(resource_packs_directory, default_pack)
    resource_packs[default_pack] = {"path": (default_path), "type": "PBR", "enabled": True}

    default_pack = "Embrace Pixels 2.1"
    default_path = os.path.join(resource_packs_directory, default_pack)
    resource_packs[default_pack] = {"path": (default_path), "type": "PBR", "enabled": True}
    
    if debug is not None:
        print(f"Default Pack: {default_pack} stored in {default_path}")
                        
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

        if debug != None:
            print(f"------\nmajor = {major} \nmajor_c = {major_c} \nminor = {minor} \nminor_c = {minor_c} \npatch = {patch} \npatch_c = {patch_c}\n------")
        
        return major_c and minor_c and patch_c
    
    except:
        version_parts = blender_version.split(" ")
        operator = version_parts[0]
        major, minor, patch = version_parts[1].lower().split(".")
        version = (int(major), int(minor), int(patch))
        
        if debug != None:
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