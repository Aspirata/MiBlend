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

def Absolute_Solver(error_code="None", data=None, err=None, error_name=None, description=None):

    def GetASText(error_code, text, data=None):
        if data != None:
            return Absolute_Solver_Errors[error_code][text].format(Data=data)
        else:
            return Absolute_Solver_Errors[error_code][text]

    if data != None:
        bpy.ops.wm.absolute_solver('INVOKE_DEFAULT', Error_Code = error_code, Error_Name = (error_name if error_code != None else GetASText(error_code, 'Error Name')), Description=(GetASText(error_code, 'Description')) if description == None else description.format(Data=data), Tech_Things = str(err) if err != None else "None")
    else:
        bpy.ops.wm.absolute_solver('INVOKE_DEFAULT', Error_Code = error_code, Error_Name = (error_name if error_code != None else GetASText(error_code, 'Error Name')), Description=(GetASText(error_code, 'Description')) if description == None else description, Tech_Things = str(err) if err != None else "None")
        
def checkconfig(name):
    if "const" in main_directory:
        return Preferences_List["Dev"][name]
    else:
        return Preferences_List["Default"][name]
    
def GetConnectedSocketTo(input, tag, material=None):
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
    resource_packs[default_pack] = {"path": (default_path), "enabled": True}

    default_pack = "Bare Bones 1.20.6"
    default_path = os.path.join(resource_packs_directory, default_pack)
    resource_packs[default_pack] = {"path": (default_path), "enabled": False}

    default_pack = "Better Emission"
    default_path = os.path.join(resource_packs_directory, default_pack)
    resource_packs[default_pack] = {"path": (default_path), "enabled": True}

    default_pack = "Embrace Pixels 2.1"
    default_path = os.path.join(resource_packs_directory, default_pack)
    resource_packs[default_pack] = {"path": (default_path), "enabled": True}
    
    if debug is not None:
        print(f"Default Pack: {default_pack} stored in {default_path}")

def find_image(image_name, root_folder):
    for dirpath, _, filenames in os.walk(root_folder):
        if image_name in filenames:
            return os.path.join(dirpath, image_name)
    
    for dirpath, _, files in os.walk(root_folder):
        for file in files:
            if file.endswith(('.zip', '.jar')):
                with zipfile.ZipFile(os.path.join(dirpath, file), 'r') as zip_ref:
                    for zip_info in zip_ref.infolist():
                        if os.path.basename(zip_info.filename) == image_name:
                            extract_path = os.path.join(main_directory, 'Resource Packs', os.path.splitext(file)[0])
                            extracted_file_path = zip_ref.extract(zip_info, extract_path)
                            return extracted_file_path
                        
    if root_folder.endswith(('.zip', '.jar')):
        with zipfile.ZipFile(root_folder, 'r') as zip_ref:
            for zip_info in zip_ref.infolist():
                if os.path.basename(zip_info.filename) == image_name:
                    extract_path = os.path.join(main_directory, 'Resource Packs', os.path.splitext(os.path.basename(root_folder))[0])
                    extracted_file_path = zip_ref.extract(zip_info, extract_path)
                    return extracted_file_path

    return None
                        
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