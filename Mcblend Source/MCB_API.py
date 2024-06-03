from .Data import *

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

def InitOnStart():
    
    if "resource_packs" not in bpy.context.scene:
        bpy.context.scene["resource_packs"] = {}

    items = bpy.context.scene.assetsproperties.asset_items
    items.clear()
    for category, assets in Assets.items():
        for key in assets.keys():
            item = items.add()
            item.name = key
                        
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

def get_resource_packs(scene, debug=None):
    if debug is not None:
        print(f"Resource Packs: {scene['resource_packs']}")

    return scene["resource_packs"]

def set_resource_packs(scene, resource_packs, debug=None):
    scene["resource_packs"] = resource_packs

    if debug is not None:
        print(f"Resource Packs: {scene['resource_packs']}")

def update_default_pack(scene, debug=None):
    resource_packs = scene["resource_packs"]

    default_pack = "Minecraft 1.20.1"
    default_path = r"C:\Users\const\OneDrive\Документы\GitHub\Mcblend\Minecraft Assets"
    resource_packs[default_pack] = {"path": default_path, "enabled": True}
    
    if debug is not None:
        print(f"Default Pack: {resource_packs[default_pack]}")

def find_image(image_name, root_folder):
        # Check in the directory
        for dirpath, _, filenames in os.walk(root_folder):
            if image_name in filenames:
                return os.path.join(dirpath, image_name)
        
        # Check in zip files within the directory
        for root, _, files in os.walk(root_folder):
            for file in files:
                if file.endswith('.zip'):
                    with zipfile.ZipFile(os.path.join(root, file), 'r') as zip_ref:
                        for zip_info in zip_ref.infolist():
                            if os.path.basename(zip_info.filename) == image_name:
                                return zip_ref.extract(zip_info, os.path.join(root_folder, 'temp'))
        
        # Check if root folder is a zip file
        if root_folder.endswith('.zip'):
            with zipfile.ZipFile(root_folder, 'r') as zip_ref:
                for zip_info in zip_ref.infolist():
                    if os.path.basename(zip_info.filename) == image_name:
                        return zip_ref.extract(zip_info, os.path.join(os.path.dirname(root_folder), 'temp'))

        return None