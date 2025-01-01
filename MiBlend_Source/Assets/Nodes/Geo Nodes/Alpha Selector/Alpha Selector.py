import bpy
import os

for selected_object in bpy.context.selected_objects:
    geonodes_modifier = None
    image_texture_node = None
    texture = None
    euvf_exists = False
    material = selected_object.data.materials[0]
    for node in material.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            image_texture_node = detect_texture_node(node)
            if image_texture_node != None:
                texture = image_texture_node.image
        
        if node.type == "GROUP":
            if "Extrude UV Fixer" in node.node_tree.name:
                euvf_exists = True
                euvf_node = node
                
    if image_texture_node != None:
        vector_connection = GetConnectedSocketTo("Vector", image_texture_node)

        if euvf_exists == False:
            if "Extrude UV Fixer" not in bpy.data.node_groups:
                with bpy.data.libraries.load(os.path.join(assets_directory, "Nodes", "Shader Nodes", "Extrude UV Fixer", "Extrude UV Fixer.blend"), link=False) as (data_from, data_to):
                    data_to.node_groups = ["Extrude UV Fixer"]

            euvf_node = material.node_tree.nodes.new(type='ShaderNodeGroup')
            euvf_node.node_tree = bpy.data.node_groups["Extrude UV Fixer"]
            euvf_node.location = (image_texture_node.location.x - 200, image_texture_node.location.y - 220)

        if vector_connection:
            if vector_connection.node != euvf_node:
                material.node_tree.links.new(vector_connection, euvf_node.inputs["Vector"])

        material.node_tree.links.new(euvf_node.outputs["Fixed UV"], image_texture_node.inputs["Vector"])

    if selected_object.type == "MESH" and texture is not None:
        for modifier in selected_object.modifiers:
            if modifier.type == "NODES":
                if modifier.node_group.name == "Alpha Selector":
                    geonodes_modifier = modifier
                    break
    
        if geonodes_modifier is None:
            geonodes_modifier = selected_object.modifiers.new("Alpha Selector", type='NODES')
            geonodes_modifier.node_group = bpy.data.node_groups.get("Alpha Selector")

        geonodes_modifier["Socket_4"] = properties.get("Extrude")
        geonodes_modifier["Input_2"] = properties.get("Extrude Offset")
        geonodes_modifier["Socket_15"] = properties.get("Auto Detect Subdivision")
        geonodes_modifier["Input_5"] = properties.get("Subdivision")
        geonodes_modifier["Input_4"] = texture
        geonodes_modifier["Socket_10"] = selected_object.data.uv_layers.active.name