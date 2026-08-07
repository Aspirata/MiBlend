active_obj = bpy.context.active_object
if active_obj and active_obj.active_material:
    current_material = active_obj.active_material
    if current_material.use_nodes:
        PBSDF = next((node for node in current_material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
        if PBSDF:
            node_group = create_node_group(current_material, "Cracks Overlay", (PBSDF.location.x - 170, PBSDF.location.y), get_selected_asset().get("File_path"), True)
            if node_group:
                base_color_connection = get_connected_socket_to("Base Color", PBSDF)
                if not base_color_connection or base_color_connection.node != node_group:
                    if base_color_connection:
                        current_material.node_tree.links.new(base_color_connection, node_group.inputs["Color"])
                    current_material.node_tree.links.new(node_group.outputs["Color"], PBSDF.inputs["Base Color"])

                alpha_connection = get_connected_socket_to("Alpha", PBSDF)
                if not alpha_connection or alpha_connection.node != node_group:
                    if alpha_connection:
                        current_material.node_tree.links.new(alpha_connection, node_group.inputs["Alpha"])
                    current_material.node_tree.links.new(node_group.outputs["Alpha"], PBSDF.inputs["Alpha"])
