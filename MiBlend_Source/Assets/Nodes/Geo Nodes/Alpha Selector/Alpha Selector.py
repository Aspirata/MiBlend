import bpy
import os

for selected_object in bpy.context.selected_objects:
    if selected_object.type != "MESH":
        continue
    
    blend_file = get_selected_asset().get("File_path")
    
    geonodes_modifier = None
    image_texture_node = None
    texture = None
    material = selected_object.data.materials[0]
    for node in material.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            image_texture_node = detect_texture_node(node)
            if image_texture_node:
                texture = image_texture_node.image
                
    if image_texture_node:
        vector_connection = GetConnectedSocketTo("Vector", image_texture_node)
        euvf_node = create_node_group(material, "Extrude UV Fixer", (image_texture_node.location.x - 200, image_texture_node.location.y - 220), blend_file, True)

        if vector_connection:
            if vector_connection.node != euvf_node:
                material.node_tree.links.new(vector_connection, euvf_node.inputs["Vector"])

        material.node_tree.links.new(euvf_node.outputs["Fixed UV"], image_texture_node.inputs["Vector"])

    if texture:
        geonodes_modifier = add_modifier(selected_object, "Alpha Selector", "Alpha Selector", blend_file)

        geonodes_modifier["Socket_4"] = properties.get("Extrude")
        geonodes_modifier["Input_2"] = properties.get("Extrude Offset")
        geonodes_modifier["Socket_15"] = properties.get("Auto Detect Subdivision")
        geonodes_modifier["Input_5"] = clamp(0, properties.get("Subdivision"), 6)
        geonodes_modifier["Input_4"] = texture
        geonodes_modifier["Socket_10"] = selected_object.data.uv_layers.active.name