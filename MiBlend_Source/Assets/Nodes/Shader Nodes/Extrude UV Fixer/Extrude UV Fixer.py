import bpy
import os

for selected_object in bpy.context.selected_objects:
    image_texture_node = None
    for material in selected_object.data.materials:
        for node in material.node_tree.nodes:
            if node.type == "BSDF_PRINCIPLED":
                image_texture_node = detect_texture_node(node)
        
        if image_texture_node:
            vector_connection = get_connected_socket_to("Vector", image_texture_node)
            euvf_node = create_node_group(material, "Extrude UV Fixer", (image_texture_node.location.x - 200, image_texture_node.location.y - 220), get_selected_asset().get("File_path").replace(".py", ".blend"), True)
            
            if vector_connection and vector_connection.node != euvf_node:
                material.node_tree.links.new(vector_connection, euvf_node.inputs["Vector"])
            
            material.node_tree.links.new(euvf_node.outputs["Fixed UV"], image_texture_node.inputs["Vector"])