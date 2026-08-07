import bpy

active_obj = bpy.context.active_object
if active_obj and active_obj.active_material:
    current_material = active_obj.active_material
    if current_material.use_nodes:
        PBSDF = next((node for node in current_material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
        if PBSDF:
            node_group = create_node_group(current_material, "Enchantment", (PBSDF.location.x - 200, PBSDF.location.y - 280), get_selected_asset().get("File_path"), True)
            if node_group:
                if socket := get_connected_socket_to("Emission Color", PBSDF):
                    if socket.node != node_group:
                        current_material.node_tree.links.new(socket, node_group.inputs["Multiply Color"])

                if socket := get_connected_socket_to("Emission Strength", PBSDF):
                    if socket.node != node_group:
                        current_material.node_tree.links.new(socket, node_group.inputs["Multiply"])

                current_material.node_tree.links.new(node_group.outputs[0], PBSDF.inputs["Emission Color"])
                current_material.node_tree.links.new(node_group.outputs[1], PBSDF.inputs["Emission Strength"])

                node_group.inputs["Divider"].default_value = properties.get("Divider")
                node_group.inputs["Camera Strenght"].default_value = properties.get("Camera Strength")
                node_group.inputs["Non-Camera Strenght"].default_value = properties.get("Non-Camera Strength")
