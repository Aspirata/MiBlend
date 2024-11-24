import bpy
import os

for selected_object in bpy.context.selected_objects:
    image_texture_node = None
    euvf_exists = False
    for material in selected_object.data.materials:
        for node in material.node_tree.nodes:
            if node.type == "BSDF_PRINCIPLED":
                image_texture_node = detect_texture_node(node)
            
            if node.type == "GROUP":
                if "Extrude UV Fixer" in node.node_tree.name:
                    euvf_exists = True
        
        if image_texture_node != None:
            if euvf_exists == False:
                vector_connection = GetConnectedSocketTo("Vector", image_texture_node)
                if "Extrude UV Fixer" not in bpy.data.node_groups:
                    with bpy.data.libraries.load(os.path.abspath(__file__).replace(".py", ".blend"), link=False) as (data_from, data_to):
                        data_to.node_groups = ["Extrude UV Fixer"]

                euvf_node = material.node_tree.nodes.new(type='ShaderNodeGroup')
                euvf_node.node_tree = bpy.data.node_groups["Extrude UV Fixer"]
                euvf_node.location = (image_texture_node.location.x - 200, image_texture_node.location.y - 220)

            if vector_connection:
                if vector_connection.node != euvf_node:
                    material.node_tree.links.new(vector_connection, euvf_node.inputs["Vector"])

            material.node_tree.links.new(euvf_node.outputs["Fixed UV"], image_texture_node.inputs["Vector"])