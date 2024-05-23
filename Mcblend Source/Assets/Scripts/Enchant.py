import bpy

UAS_API = {
    "divider": {
        "Type": float
    }
}

def Enchant():
    for selected_object in bpy.context.selected_objects:
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                if material != None:
                    node_group = None
                    PBSDF = None

                    for node in material.node_tree.nodes:
                        if node.type == 'GROUP':
                            if "Enchantment" in node.node_tree.name:
                                node_group = node

                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node

                    if node_group == None:
                        if "Enchantment" not in bpy.data.node_groups:
                            try:
                                with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                                    data_to.node_groups = ["Enchantment"]
                            except:
                                CEH("004")

                        node_group = material.node_tree.nodes.new(type='ShaderNodeGroup')
                        node_group.node_tree = bpy.data.node_groups["Enchantment"]
                        node_group.location = (PBSDF.location.x - 200, PBSDF.location.y - 280)

                    for node in material.node_tree.nodes:
                        if node.type == "BSDF_PRINCIPLED":
                            for link in node.inputs["Emission Strength"].links:                                            
                                if link.from_node.name != node_group.name:                                                
                                    for output in link.from_node.outputs:
                                        for link_out in output.links:
                                            if link_out.to_socket.node.name == node.name:                                                                                                                    
                                                material.node_tree.links.new(link_out.from_socket, node_group.inputs["Multiply"]) 
                                                break
                            
                            if blender_version("4.x.x"):
                                for link in node.inputs["Emission Color"].links:                                            
                                    if link.from_node.name != node_group.name:                                                
                                        for output in link.from_node.outputs:
                                            for link_out in output.links:
                                                if link_out.to_socket.node.name == node.name:                                                                                                                    
                                                    material.node_tree.links.new(link_out.from_socket, node_group.inputs["Multiply Color"]) 
                                                    break
                            else:
                                for link in node.inputs["Emission"].links:                                            
                                    if link.from_node.name != node_group.name:                                                
                                        for output in link.from_node.outputs:
                                            for link_out in output.links:
                                                if link_out.to_socket.node.name == node.name:                                                                                                                    
                                                    material.node_tree.links.new(link_out.from_socket, node_group.inputs["Multiply Color"]) 
                                                    break

                    if blender_version("4.x.x"):                        
                        material.node_tree.links.new(node_group.outputs[0], PBSDF.inputs["Emission Color"])
                    else:
                        material.node_tree.links.new(node_group.outputs[0], PBSDF.inputs["Emission"])
                    
                    material.node_tree.links.new(node_group.outputs[1], PBSDF.inputs["Emission Strength"])
                    node_group.inputs["Divider"].default_value = bpy.context.scene.render.fps/30 * bpy.context.scene.utilsproperties.divider
                    node_group.inputs["Camera Strenght"].default_value = bpy.context.scene.utilsproperties.camera_strenght
                    node_group.inputs["Non-Camera Strenght"].default_value = bpy.context.scene.utilsproperties.non_camera_strenght
                else:
                    CEH("m002")
        else:
            CEH("m003")