import bpy


for selected_object in bpy.context.selected_objects:
    if selected_object.type != "MESH":
        continue
    
    geonodes_modifier = None
    image_texture_node = None
    texture = None
    uv_layer = selected_object.data.uv_layers.active

    if not selected_object.data.materials or not uv_layer:
        continue

    material = selected_object.data.materials[0]
    if not material or not material.use_nodes or not material.node_tree:
        continue

    pbsf_node = next((node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if not pbsf_node:
        continue

    image_texture_node = detect_texture_node(pbsf_node)
    if not image_texture_node:
        continue

    texture = image_texture_node.image
    if not texture:
        continue

    blend_file = get_selected_asset().get("File_path")
    geonodes_modifier = add_modifier(selected_object, "Alpha Faces Deleter", "Alpha Faces Deleter", blend_file)

    if properties.get("Solidify"):
        solidify_modifier = add_modifier(selected_object, "SOLIDIFY", "Solidify")
        solidify_modifier.thickness = properties.get("Solidify Thickness")
        solidify_modifier.use_even_offset = True

    if bpy.app.version >= (5, 2, 0):
        geonodes_modifier.properties.inputs.Socket_10.value = texture
        geonodes_modifier.properties.inputs.Socket_12.value = properties.get("Auto Detect Subdivision")
        geonodes_modifier.properties.inputs.Socket_13.value = int(clamp(0.0, float(properties.get("Subdivision")), 6.0))
        geonodes_modifier.properties.inputs.Socket_2.value = uv_layer.name
    else:
        geonodes_modifier["Socket_10"] = texture
        geonodes_modifier["Socket_12"] = properties.get("Auto Detect Subdivision")
        geonodes_modifier["Socket_13"] = int(clamp(0.0, float(properties.get("Subdivision")), 6.0))
        geonodes_modifier["Socket_2"] = uv_layer.name
