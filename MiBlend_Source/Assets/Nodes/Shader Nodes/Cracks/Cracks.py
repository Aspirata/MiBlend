active_obj = bpy.context.active_object
if active_obj and active_obj.active_material:
    current_material = active_obj.active_material
    if current_material.use_nodes:
        PBSDF = None
        co_node = None

        for node in current_material.node_tree.nodes:
            if node.type == "BSDF_PRINCIPLED":
                PBSDF = node

        node_group = create_node_group(current_material, "Cracks Overlay", (PBSDF.location.x - 170, PBSDF.location.y), get_selected_asset().get("File_path"), True)

        if GetConnectedSocketTo("Base Color", PBSDF).node != node_group:
            current_material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), co_node.inputs["Color"])
            current_material.node_tree.links.new(co_node.outputs["Color"], PBSDF.inputs["Base Color"])

        if GetConnectedSocketTo("Alpha", PBSDF).node != node_group:
            current_material.node_tree.links.new(GetConnectedSocketTo("Alpha", PBSDF), co_node.inputs["Alpha"])
            current_material.node_tree.links.new(co_node.outputs["Alpha"], PBSDF.inputs["Alpha"])