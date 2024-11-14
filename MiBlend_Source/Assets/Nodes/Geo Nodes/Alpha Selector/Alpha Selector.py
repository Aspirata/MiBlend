import bpy

for selected_object in bpy.context.selected_objects:
    geonodes_modifier = None
    image_texture_node = None
    for node in selected_object.data.materials[0].node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            texture = detect_texture_node(node).image

    if selected_object.type == "MESH" and texture is not None:
        for modifier in selected_object.modifiers:
            if modifier.type == "NODES":
                if modifier.node_group == "Alpha Selector":
                    geonodes_modifier = modifier
                    break
    
        if geonodes_modifier is None:
            geonodes_modifier = selected_object.modifiers.new("Alpha Selector", type='NODES')
            geonodes_modifier.node_group = bpy.data.node_groups.get("Alpha Selector")

        geonodes_modifier["Input_4"] = texture
        geonodes_modifier["Socket_4"] = properties.get("Extrude")
        geonodes_modifier["Input_2"] = properties.get("Extrude Offset")
        geonodes_modifier["Socket_15"] = properties.get("Auto Detect Subdivision")
        geonodes_modifier["Input_5"] = properties.get("Subdivision")