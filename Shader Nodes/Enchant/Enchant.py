import sys

addon_dir = os.path.dirname(os.path.abspath(__file__))
if addon_dir not in sys.path:
    sys.path.append(addon_dir)

from MCB_API import GetConnectedSocketTo, PBSDF_compability

current_index = bpy.context.scene.assetsproperties.asset_index
items = bpy.context.scene.assetsproperties.asset_items

current_asset = items[current_index]

json_file_path = current_asset.get("File_path", "") + ".json"

with open(json_file_path, 'r') as json_file:
    asset_data = json.load(json_file)

properties = {key.replace('_property', ''): value for key, value in current_asset.items() if 'property' in key.lower()}

active_obj = bpy.context.active_object
if active_obj and active_obj.active_material:
    current_material = active_obj.active_material
    if current_material.use_nodes:
            node_group = None
            PBSDF = None

            for node in current_material.node_tree.nodes:
                if node.type == 'GROUP':
                    if "Enchantment" in node.node_tree.name:
                        node_group = node

                if node.type == "BSDF_PRINCIPLED":
                    PBSDF = node

            if node_group == None:
                node_group = current_material.node_tree.nodes.new(type='ShaderNodeGroup')
                node_group.node_tree = bpy.data.node_groups["Enchantment"]
                node_group.location = (PBSDF.location.x - 200, PBSDF.location.y - 280)

            if socket := GetConnectedSocketTo(PBSDF_compability("Emission Color"), PBSDF):
                if socket.node != node_group:
                    current_material.node_tree.links.new(socket, node_group.inputs["Multiply Color"])
            
            if socket := GetConnectedSocketTo("Emission Strength", PBSDF):
                if socket.node != node_group:
                    current_material.node_tree.links.new(socket, node_group.inputs["Multiply"])
 
            current_material.node_tree.links.new(node_group.outputs[0], PBSDF.inputs[PBSDF_compability("Emission Color")])
            current_material.node_tree.links.new(node_group.outputs[1], PBSDF.inputs["Emission Strength"])
            
            node_group.inputs["Divider"].default_value = properties.get("Divider", asset_data["Divider_property"])
            node_group.inputs["Camera Strenght"].default_value = properties.get("Camera Strength", asset_data["Camera Strength_property"])
            node_group.inputs["Non-Camera Strenght"].default_value = properties.get("Non-Camera Strength", asset_data["Non-Camera Strength_property"])