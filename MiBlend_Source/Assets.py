import bpy, os, json, traceback
from . import Data, MIB_API
from .MIB_API import dprint, create_node_group, get_selected_asset
from .Data import assets_directory
from .Utils.Absolute_Solver import trigger_absolute_solver

def append_asset(asset_data):
    asset_name = asset_data.get("Asset_name", "")
    asset_path = asset_data.get("File_path", "")
    asset_type = asset_data.get("Type", "")
    asset_collection = asset_data.get("Collection_name", "Root")

    try:
        dprint(f"Appending asset: {asset_name} ({asset_type})")
        if asset_type == "Rig" or asset_type == "Model":
            append_collection(asset_name, asset_collection, asset_path)

        elif asset_type == "Script":
            run_python_script(asset_name, asset_path)
        
        elif asset_type == "Compositor Node":
            append_cnode(asset_data)

        elif asset_type == "Geo Node":
            append_gnode(asset_data)
        
        elif asset_type == "Shader Node":
            append_snode(asset_data)
        
        elif asset_type == "Material":
            append_material(asset_data)
        
    except Exception:
        trigger_absolute_solver("e05", traceback.format_exc(), asset_name)

def append_collection(asset_name, asset_collection, asset_path):
    with bpy.data.libraries.load(asset_path, link=False) as (data_from, data_to):
        if asset_collection not in data_from.collections:
            trigger_absolute_solver("e05", data=asset_name, tech_things=f"Collection {asset_collection} not found")
            return
        
        data_to.collections = [asset_collection]

    for collection in data_to.collections:
        if bpy.context.active_object:
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.collection.children.link(collection)
        for obj in collection.objects:
            obj["MiBlend_ID"] = "Asset"
            if obj.type != "ARMATURE":
                continue
            
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            root_bone = next((bone for bone in obj.data.bones if bone.name.lower() == "root"), None)
            if not root_bone:
                continue
            
            cursor_location = bpy.context.scene.cursor.location
            obj.pose.bones[root_bone.name].matrix.translation = cursor_location

def run_python_script(name, path):
    properties = {key.replace('_property', ''): value for key, value in get_selected_asset().items() if 'property' in key}
    context = {}

    context.update({name: getattr(Data, name) 
                    for name in dir(Data) 
                    if not name.startswith('_')})

    context.update({name: getattr(MIB_API, name) 
                    for name in dir(MIB_API) 
                    if not name.startswith('_')})

    context["properties"] = properties

    with open(path, 'r') as file:
        script = file.read()

    exec(script, context)

def append_snode(asset_data):
    Node_name = asset_data.get("Node_name", "")
    Append_mode = asset_data.get("Append_mode", "Active Only")
    Blend_file = asset_data.get("File_path", "")
    Script_path = asset_data.get("File_path", "").replace(".blend", ".py")

    if os.path.isfile(Script_path):
        dprint(f"{Node_name} Script Found", is_deep=True, zone="uas")
        run_python_script(asset_data.get("Asset_name"), Script_path)

    elif Append_mode == "Every Selected":
        dprint(f"{Node_name} Script Not Found, using default algorithm", is_deep=True, zone="uas")
        for selected_object in bpy.context.selected_objects:
            if selected_object.type == "MESH":
                for index, material in enumerate(selected_object.data.materials):
                    if material is not None and material.use_nodes:
                        nodes_list = material.node_tree.nodes
                        avg_x = [node.location.x for node in nodes_list]
                        avg_y = [node.location.y for node in nodes_list]

                        create_node_group(material, Node_name, (sum(avg_x) / len(avg_x), sum(avg_y) / len(avg_y)), Blend_file, True)

    elif Append_mode == "Active Only":
        dprint(f"{Node_name} Script Not Found, using default algorithm", is_deep=True, zone="uas")
        active_obj = bpy.context.active_object
        if active_obj and active_obj.type == "MESH" and active_obj.active_material:
            current_material = active_obj.active_material
            if current_material is not None and current_material.use_nodes:
                nodes_list = current_material.node_tree.nodes
                avg_x = [node.location.x for node in nodes_list]
                avg_y = [node.location.y for node in nodes_list]

                create_node_group(current_material, Node_name, (sum(avg_x) / len(avg_x), sum(avg_y) / len(avg_y)), Blend_file, True)

def append_cnode(asset_data):
    Node_name = asset_data.get("Node_name", "")
    Blend_file = asset_data.get("File_path", "")
    Script_path = asset_data.get("File_path", "").replace(".blend", ".py")

    if Node_name not in bpy.data.node_groups:
        try:
            with bpy.data.libraries.load(Blend_file, link=False) as (data_from, data_to):
                data_to.node_groups = [Node_name]
        except Exception as error:
            trigger_absolute_solver("e05", error, Node_name)

    if os.path.isfile(Script_path):
        run_python_script(asset_data.get("Asset_name"), Script_path)
        dprint(f"{Node_name} Script Found", is_deep=True, zone="uas")
    else:
        dprint(f"{Node_name} Script Not Found, using default algorithm", is_deep=True, zone="uas")
        avg_x = []
        avg_y = []
        scene = bpy.context.scene
        if bpy.app.version >= (5, 0, 0):
            if not scene.compositing_node_group:
                tree = bpy.data.node_groups.new("New Compositor", "CompositorNodeTree")
                scene.compositing_node_group = tree
                rlayers = tree.nodes.new(type="CompositorNodeRLayers")
                output = tree.nodes.new(type='NodeGroupOutput')
                tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
                tree.links.new(output.inputs["Image"], rlayers.outputs["Image"])
                rlayers.location[0] -= 1.5 * rlayers.width
            else:
                tree = scene.compositing_node_group
        else:
            scene.use_nodes = True
            tree = scene.node_tree

        Node = None
        for node in tree.nodes:
            avg_x.append(node.location.x)
            avg_y.append(node.location.y)
            if node.type == 'GROUP':
                if Node_name in node.node_tree.name:
                    Node = node

        if Node is None:
            Node = tree.nodes.new('CompositorNodeGroup')
            Node.node_tree = bpy.data.node_groups[Node_name]
            Node.location = (sum(avg_x) / len(avg_x), sum(avg_y) / len(avg_y))

def append_gnode(asset_data):
    Node_name = asset_data.get("Node_name", "")
    Append_mode = asset_data.get("Append_mode", "Active Only")
    Blend_file = asset_data.get("File_path", "")
    Script_path = asset_data.get("File_path", "").replace(".blend", ".py")

    if Node_name not in bpy.data.node_groups:
        try:
            with bpy.data.libraries.load(Blend_file, link=False) as (data_from, data_to):
                data_to.node_groups = [Node_name]
        except Exception as error:
            trigger_absolute_solver("e05", error, Node_name)

    if os.path.isfile(Script_path):
        run_python_script(asset_data.get("Asset_name"), Script_path)
        dprint(f"{Node_name} Script Found", is_deep=True, zone="uas")

    elif Append_mode == "Every Selected":
        dprint(f"{Node_name} Script Not Found, using default algorithm", is_deep=True, zone="uas")
        for selected_object in bpy.context.selected_objects:
            geonodes_modifier = None
            if selected_object.type == "MESH":
                for modifier in selected_object.modifiers:
                    if modifier.type == "NODES":
                        if modifier.node_group == Node_name:
                            geonodes_modifier = modifier
                            break
            
                if geonodes_modifier is None:
                    geonodes_modifier = selected_object.modifiers.new(Node_name, type='NODES')
                    geonodes_modifier.node_group = bpy.data.node_groups.get(Node_name)

    elif Append_mode == "Active Only":
        dprint(f"{Node_name} Script Not Found, using default algorithm", is_deep=True, zone="uas")
        active_obj = bpy.context.active_object
        geonodes_modifier = None
        if active_obj and active_obj.type == "MESH":
            for modifier in selected_object.modifiers:
                if modifier.type == "NODES":
                    if modifier.node_group == Node_name:
                        geonodes_modifier = modifier
                        break
        
        if geonodes_modifier is None:
            geonodes_modifier = active_obj.modifiers.new(Node_name, type='NODES')
            geonodes_modifier.node_group = bpy.data.node_groups.get(Node_name)

def append_material(asset_data):
    Append_mode = asset_data.get("Append_mode", "Active Only")
    Blend_file = asset_data.get("File_path", "")
    Material_name = asset_data.get("Material_name", "")
    Script_path = asset_data.get("File_path", "").replace(".blend", ".py")

    if Material_name not in bpy.data.materials:
        try:
            with bpy.data.libraries.load(Blend_file, link=False) as (data_from, data_to):
                data_to.materials = Material_name
        except Exception as error:
            trigger_absolute_solver("e05", error, Material_name)
    
    if os.path.isfile(Script_path):
        run_python_script(asset_data.get("Asset_name"), Script_path)
        dprint(f"{Material_name} Script Found", is_deep=True, zone="uas")

    elif Append_mode == "Active Only":
        dprint(f"{Material_name} Script Not Found, using default algorithm", is_deep=True, zone="uas")
        active_obj = bpy.context.active_object
        if active_obj and active_obj.material_slots:
            active_obj.data.materials[0] = bpy.data.materials.get(Material_name)

def update_assets():
    items = bpy.context.scene.miblend_properties.assets_properties.asset_items
    items.clear()
    assets_list = []

    directories_to_scan = [assets_directory]

    temp_assets_paths = bpy.context.scene.get("mib_options", {}).get("temp_assets_paths", [])
    temp_assets_path_list = list(temp_assets_paths)

    if len(temp_assets_path_list) > 0:
        directories_to_scan.extend(temp_assets_path_list)

    dprint(f"Scanning {directories_to_scan}", is_deep=True, zone="uas")

    for directory in directories_to_scan:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if not file.endswith(".json"):
                    continue
                
                json_path = os.path.join(root, file)
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        asset_data = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    dprint(f"Error reading JSON file {json_path}: {e}", is_deep=True, zone="uas")
                    continue

                try:
                    format_version = asset_data.get("Format_version")
                    if format_version == "dev":
                        continue

                    asset_name = asset_data.get("Asset_name")
                    asset_author = asset_data.get("Author")
                    asset_tags = asset_data.get("Tags", [])
                    
                    asset_file_path = os.path.splitext(os.path.basename(json_path))[0]
                    if asset_tags and asset_tags[0] == "Script":
                        asset_file_path = os.path.join(root, asset_file_path + ".py")
                    else:
                        asset_file_path = os.path.join(root, asset_file_path + ".blend")

                    if format_version != "test":
                        if not asset_name:
                            dprint("Asset_name is not defined", is_deep=True, zone="uas")
                            continue
                        if not asset_author:
                            dprint("Author is not defined", is_deep=True, zone="uas")
                            continue
                        if not asset_tags:
                            dprint("Tags are not defined", is_deep=True, zone="uas")
                            continue
                        if not asset_file_path:
                            dprint("File_path is not defined", is_deep=True, zone="uas")
                            continue
                        if not os.path.isfile(asset_file_path):
                            dprint(f"Cannot find the asset file: {asset_file_path}", is_deep=True, zone="uas")
                            continue

                    asset_info = {}
                    for key, value in asset_data.items():
                        if key not in ["Format_version"]:
                            asset_info[key] = value

                    asset_info["Type"] = asset_tags[0]
                    asset_info["File_path"] = asset_file_path

                    if any('property' in key for key in asset_info):
                        asset_info["has_properties"] = True

                    assets_list.append(asset_info)
                    
                except Exception as error:
                    trigger_absolute_solver("e06", error, asset_data.get("Asset_name"))
                        
    for asset in sorted(assets_list, key=lambda x: x.get("Asset_name", "")):
        item = items.add()
        for key, value in asset.items():
            item[key] = value

    # Tags
    current_states = {tag.name: tag.enabled for tag in bpy.context.scene.miblend_properties.assets_properties.tags}
    tags = bpy.context.scene.miblend_properties.assets_properties.tags
    tags.clear()
    
    unique_tags = set()
    for asset in items:
        asset_tags = asset.get("Tags", [])
        unique_tags.update(asset_tags)

    unique_tags = sorted(unique_tags)

    for tag in unique_tags:
        item = tags.add()
        item.name = tag
        item.enabled = current_states.get(tag, False)