import bpy

interpolate = properties.get("Force Interpolation")
frametime = properties.get("Frametime")
randomize_speed = properties.get("Randomize Speed")

def process_material():
    selected_object = bpy.context.active_object
    Texture_Animator = None
    ITexture_Animator = None
    texture_node = None
    
    if not is_mesh(selected_object) or not selected_object.active_material:
        return

    material = selected_object.active_material

    if not material.use_nodes:
        return

    try:
        textures_list = [node for node in material.node_tree.nodes if node.type == "TEX_IMAGE" or (node.type == "GROUP" and "Animated; " in node.node_tree.name)]
        for texture_node in textures_list:
            if texture_node.type == "GROUP":
                ITexture_Animator = texture_node
                image_texture = find_node(ITexture_Animator, "TEX_IMAGE").image
            else:
                Texture_Animator = texture_node.inputs["Vector"].links[0].from_node if texture_node.inputs["Vector"].is_linked else None
                image_texture = texture_node.image
        

        if randomize_speed:
            add_modifier(selected_object, "Random Face Value")
            
        if interpolate:
            if Texture_Animator:
                material.node_tree.nodes.remove(Texture_Animator)

            if not ITexture_Animator:
                ITexture_Animator = material.node_tree.nodes.new(type='ShaderNodeGroup')
                ITexture_Animator.location = texture_node.location

                if f"Animated; {image_texture.name.replace('.png', '')}" in bpy.data.node_groups:
                    Current_node_tree = bpy.data.node_groups[f"Animated; {image_texture.name.replace('.png', '')}"]
                    ITexture_Animator.node_tree = Current_node_tree
                else:
                    if "Texture Animator" not in bpy.data.node_groups:
                        with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                            data_to.node_groups = ["Texture Animator"]
                    
                    with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                        data_to.node_groups = ["Texture Animator"]

                    bpy.data.node_groups[f"Texture Animator.001"].name = f"Animated; {image_texture.name.replace('.png', '')}"
                    ITexture_Animator.node_tree = bpy.data.node_groups[f"Animated; {image_texture.name.replace('.png', '')}"]
                    for node in ITexture_Animator.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            node.image = image_texture

                if texture_node is not None:
                    for socket in GetConnectedSocketFrom("Color", texture_node):
                        material.node_tree.links.new(ITexture_Animator.outputs["Color"], socket)
                
                    for socket in GetConnectedSocketFrom("Alpha", texture_node):
                        material.node_tree.links.new(ITexture_Animator.outputs["Alpha"], socket)
                    
                    vector_connection = GetConnectedSocketTo("Vector", texture_node)

                    if vector_connection is not None and vector_connection.node != ITexture_Animator:
                        material.node_tree.links.new(vector_connection, ITexture_Animator.inputs["Vector"])

                    material.node_tree.nodes.remove(texture_node)

            ITexture_Animator.inputs["Frames"].default_value = int(image_texture.size[1] / image_texture.size[0])
            ITexture_Animator.inputs["Frametime"].default_value = frametime
            ITexture_Animator.inputs["Interpolate"].default_value = True
            ITexture_Animator.inputs["Randomize Speed"].default_value = randomize_speed
        else:
            if ITexture_Animator:
                texture_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')
                texture_node.location = ITexture_Animator.location
                texture_node.image = image_texture
                texture_node.interpolation = "Closest"

                for socket in GetConnectedSocketFrom("Color", ITexture_Animator):
                    material.node_tree.links.new(texture_node.outputs["Color"], socket)
                
                for socket in GetConnectedSocketFrom("Alpha", ITexture_Animator):
                    material.node_tree.links.new(texture_node.outputs["Alpha"], socket)

                material.node_tree.nodes.remove(ITexture_Animator)
            
            if not Texture_Animator:
                Texture_Animator = create_node_group(material, "Texture Animator", (texture_node.location.x - 200, texture_node.location.y - 60))

            vector_connection = GetConnectedSocketTo("Vector", texture_node)

            if vector_connection is not None and vector_connection.node != Texture_Animator:
                material.node_tree.links.new(vector_connection, Texture_Animator.inputs["Vector"])

            material.node_tree.links.new(Texture_Animator.outputs["Current Frame"], texture_node.inputs["Vector"])

            Texture_Animator.inputs["Frames"].default_value = int(image_texture.size[1] / image_texture.size[0])
            Texture_Animator.inputs["Frametime"].default_value = frametime
            Texture_Animator.inputs["Interpolate"].default_value = False
            Texture_Animator.inputs["Randomize Speed"].default_value = randomize_speed
    except:
        pass
    
    if not Texture_Animator and not ITexture_Animator:
        nodes_list = material.node_tree.nodes
        avg_x = [node.location.x for node in nodes_list]
        avg_y = [node.location.y for node in nodes_list]
        Texture_Animator = create_node_group(material, "Texture Animator", (sum(avg_x) / len(avg_x), sum(avg_y) / len(avg_y)), exists_check=True)
        Texture_Animator.inputs["Frametime"].default_value = frametime
        Texture_Animator.inputs["Interpolate"].default_value = interpolate
        Texture_Animator.inputs["Randomize Speed"].default_value = randomize_speed

process_material()