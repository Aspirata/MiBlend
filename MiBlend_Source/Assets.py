from .Data import *
from .MIB_API import *
from .Utils.Absolute_Solver import Absolute_Solver

def append_snode(asset_data):
    Node_name = asset_data.get("Node_name", "")
    Append_mode = asset_data.get("Append_mode", "Active Only")
    Blend_file = asset_data.get("File_path", "")
    Script_path = asset_data.get("File_path", "").replace(".blend", ".py")

    if os.path.isfile(Script_path):
        run_python_script(asset_data.get("Asset_name"), Script_path)
        dprint(f"{Node_name} Script Found")

    elif Append_mode == "Every Selected":
        dprint(f"{Node_name} Script Not Found, using default algorithm")
        for selected_object in bpy.context.selected_objects:
            slot = 0
            if selected_object.material_slots:
                for material in selected_object.data.materials:
                    slot += 1
                    if material is not None and material.use_nodes:
                        if Node_name not in bpy.data.node_groups:
                            try:
                                with bpy.data.libraries.load(Blend_file, link=False) as (data_from, data_to):
                                    data_to.node_groups = [Node_name]
                            except:
                                Absolute_Solver("009", Node_name, traceback.format_exc())

                        Node = material.node_tree.nodes.new(type='ShaderNodeGroup')
                        Node.node_tree = bpy.data.node_groups[Node_name]
                    else:
                        Absolute_Solver("m002", slot)
            else:
                Absolute_Solver("m003", selected_object)

    elif Append_mode == "Active Only":
        dprint(f"{Node_name} Script Not Found, using default algorithm")
        active_obj = bpy.context.active_object
        if active_obj and active_obj.active_material:
            current_material = active_obj.active_material
            if current_material.use_nodes:
                if Node_name not in bpy.data.node_groups:
                    try:
                        with bpy.data.libraries.load(Blend_file, link=False) as (data_from, data_to):
                            data_to.node_groups = [Node_name]
                    except:
                        Absolute_Solver("009", Node_name, traceback.format_exc())

                Node = current_material.node_tree.nodes.new(type='ShaderNodeGroup')
                Node.node_tree = bpy.data.node_groups[Node_name]

def append_gnode(asset_data):
    Node_name = asset_data.get("Node_name", "")
    Append_mode = asset_data.get("Append_mode", "Active Only")
    Blend_file = asset_data.get("File_path", "")
    Script_path = asset_data.get("File_path", "").replace(".blend", ".py")

    if os.path.isfile(Script_path):
        run_python_script(asset_data.get("Asset_name"), Script_path)
        dprint(f"{Node_name} Script Found")

    elif Append_mode == "Every Selected":
        dprint(f"{Node_name} Script Not Found, using default algorithm")
        for selected_object in bpy.context.selected_objects:
            slot = 0
            if selected_object.material_slots:
                for material in selected_object.data.materials:
                    slot += 1
                    if material is not None and material.use_nodes:
                        if Node_name not in bpy.data.node_groups:
                            try:
                                with bpy.data.libraries.load(Blend_file, link=False) as (data_from, data_to):
                                    data_to.node_groups = [Node_name]
                            except:
                                Absolute_Solver("009", Node_name, traceback.format_exc())

                        Node = material.node_tree.nodes.new(type='ShaderNodeGroup')
                        Node.node_tree = bpy.data.node_groups[Node_name]
                    else:
                        Absolute_Solver("m002", slot)
            else:
                Absolute_Solver("m003", selected_object)

    elif Append_mode == "Active Only":
        dprint(f"{Node_name} Script Not Found, using default algorithm")
        active_obj = bpy.context.active_object
        if active_obj and active_obj.active_material:
            current_material = active_obj.active_material
            if current_material.use_nodes:
                if Node_name not in bpy.data.node_groups:
                    try:
                        with bpy.data.libraries.load(Blend_file, link=False) as (data_from, data_to):
                            data_to.node_groups = [Node_name]
                    except:
                        Absolute_Solver("009", Node_name, traceback.format_exc())

                Node = current_material.node_tree.nodes.new(type='ShaderNodeGroup')
                Node.node_tree = bpy.data.node_groups[Node_name]

def run_python_script(name, path):
    try:
        with open(path, 'r') as file:
            exec(file.read())
    except:
        Absolute_Solver("009", name, traceback.print_exc())

def append_asset(asset_data):
    asset_name = asset_data.get("Asset_name")
    asset_path = asset_data.get("File_path", "")
    asset_type = asset_data.get("Type", "")

    try:
        if asset_type == "Rig" or asset_type == "Model":
            with bpy.data.libraries.load(asset_path + ".blend", link=False) as (data_from, data_to):
                data_to.collections = [asset_data.get("Collection_name")]

            for collection in data_to.collections:
                if collection:
                    bpy.context.collection.children.link(collection)

        elif asset_type == "Script":
            run_python_script(asset_name, asset_path)
        
        elif asset_type == "Shader Node":
            append_snode(asset_data)
        
    except:
        Absolute_Solver(tech_things=traceback.format_exc(), data=asset_name, error_name="Bad Asset Import", description=f"Can't Import {asset_name} Asset")

def update_assets():
    items = bpy.context.scene.assetsproperties.asset_items
    items.clear()
    assets_list = []

    directories_to_scan = [assets_directory]
    
    temp_assets_paths = bpy.context.scene.get("mib_options", {}).get("temp_assets_paths", {})
    directories_to_scan.extend(temp_assets_paths.values())

    for directory in directories_to_scan:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".json"):
                    json_path = os.path.join(root, file)
                    with open(json_path, 'r') as f:
                        asset_data = json.load(f)
    
                    try:
                        format_version = asset_data.get("Format_version")

                        if format_version == "dev":
                            continue 

                        asset_name = asset_data.get("Asset_name")
                        asset_tags = asset_data.get("Tags", [])

                        if asset_tags[0] != "Script":
                            asset_file_path = os.path.join(root, os.path.basename(asset_data.get("File_path", "")) + ".blend")
                        else:
                            asset_file_path = os.path.join(root, os.path.basename(asset_data.get("File_path", "")) + ".py")

                        if format_version != "test":
                            if not asset_name:
                                dprint("Asset_name is not defined")
                                continue
                            if not asset_file_path:
                                dprint("File_path is not defined")
                                continue
                            if not os.path.isfile(asset_file_path):
                                dprint(f"Cannot find the asset file: {asset_file_path}")
                                continue
                            if not asset_tags:
                                dprint("Tags are not defined")
                                continue

                        asset_info = {}
                        for key, value in asset_data.items():
                            if key not in ["Format_version"]:
                                asset_info[key] = value

                        asset_info["Type"] = asset_tags[0]
                        asset_info["File_path"] = asset_file_path

                        if any('property' in key.lower() for key in asset_info):
                            asset_info["has_properties"] = True

                        assets_list.append(asset_info)
                    except:
                        Absolute_Solver("u008", asset_data.get("Asset_name"), traceback.format_exc())

    for asset in sorted(assets_list, key=lambda x: x["Asset_name"]):
        item = items.add()
        for key, value in asset.items():
            item[key] = value

    # Tags
    current_states = {tag.name: tag.enabled for tag in bpy.context.scene.assetsproperties.tags}

    tags = bpy.context.scene.assetsproperties.tags
    tags.clear()
    unique_tags = set()

    for asset in items:
        asset_tags = asset.get("Tags", [])
        unique_tags.update(asset_tags)

    unique_tags.add("All")
    unique_tags = sorted(unique_tags)

    for tag in unique_tags:
        item = tags.add()
        item.name = tag
        item.enabled = current_states.get(tag, tag == "All")