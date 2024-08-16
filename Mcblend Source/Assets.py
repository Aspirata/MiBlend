from genericpath import isfile
from .Data import *
from .MCB_API import *
import sys
from .Utils.Absolute_Solver import Absolute_Solver

def append_snode(asset_data):
    Node_name = asset_data.get("Node_name", "")
    Script_path = asset_data.get("Script_path", "")

    if Node_name not in bpy.data.node_groups:
        try:
            with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                data_to.node_groups = [Node_name]
        except:
            Absolute_Solver("009", Node_name, traceback.format_exc())
    
    if os.isfile(Script_path):
        run_python_script(Script_path)
    else:
        for selected_object in bpy.context.selected_objects:
            slot = 0
            if selected_object.material_slots:
                for material in selected_object.data.materials:
                    slot += 1
                    if material is not None and material.use_nodes:
                        Node = material.node_tree.nodes.new(type='ShaderNodeGroup')
                        Node.node_tree = bpy.data.node_groups[Node_name]
                        #Node.location = (PBSDF.location.x - 170, PBSDF.location.y - 110)
                    else:
                        Absolute_Solver("m002", slot)
            else:
                Absolute_Solver("m003", selected_object)

def run_python_script(file_path):
    def import_all_from_module(module_name, module_path=None):
        if module_path:
            if module_path not in sys.path:
                sys.path.append(module_path)
        module = __import__(module_name, fromlist=['*'])
        return {name: getattr(module, name) for name in dir(module) if not name.startswith('__')}

    try:
        global_context = {'__name__': '__main__'}
        additional_globals = import_all_from_module('Data', os.path.join(os.path.dirname(__file__)))
        
        if additional_globals:
            global_context.update(additional_globals)
        
        with open(file_path, 'r') as file:
            exec(file.read(), global_context)
    except:
        Absolute_Solver(tech_things=traceback.print_exc(), data=file_path, error_name="Bad Script Execution", description="Can't Execute Script from {Data}")

def append_asset(asset_data):
    asset_name = asset_data.get("Asset_name")
    asset_path = asset_data.get("File_path", "")
    asset_type = asset_data.get("Type", "")

    try:
        if asset_type == "Rig":
            with bpy.data.libraries.load(asset_path, link=False) as (data_from, data_to):
                data_to.collections = [asset_data.get("Collection_name")]

            for collection in data_to.collections:
                if collection:
                    bpy.context.collection.children.link(collection)

        elif asset_type == "Script":
            run_python_script(asset_path)
        
        elif asset_type == "Shader Node":
            append_snode(asset_data)
        
    except:
        Absolute_Solver(tech_things=traceback.format_exc(), data=asset_name, error_name="Bad Asset Import", description=f"Can't Import {asset_name} Asset")

def update_assets():
    items = bpy.context.scene.assetsproperties.asset_items
    items.clear()

    assets_list = []
    for root, dirs, files in os.walk(assets_directory):
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
                    asset_file_path = os.path.join(root, os.path.basename(asset_data.get("File_path", "")))
                    asset_tags = asset_data.get("Tags", [])

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