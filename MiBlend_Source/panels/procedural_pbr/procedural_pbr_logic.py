import bpy
from ..absolute_solver.absolute_solver_logic import trigger_absolute_solver
from ...mib_utils import (get_preferences, is_code_ignored, name_in, perf_time, 
                        detect_texture_node, detect_image_texture, 
                        is_emissive, GetConnectedSocketTo, create_node_group, 
                        add_modifier, RemoveLinksFrom)
from ...resources.data import nodes_file, EMISSIVE_MATERIALS


SSS_Materials = ["leaves", "grass", "tulip", "oxeye daisy", "dandelion", "poppy", "blue orchid", "torchflower", "lily of the valley", "cornflower", "allium", "azure bluet", "azalea", "cactus", "wheat", "hay", "wildflowers"]
TRANSLUCENT_MATERIALS = ["leaves", "glass"]
METALLIC_MATERIALS = ["iron", "gold", "emerald", "copper ; torch", "diamond", "netherite", "minecart", "lantern ; jack", "chain", "anvil", "clock", "cauldron", "spyglass", "rail"]
REFLECTIVE_MATERIALS = ["glass", "ender", "amethyst", "water", "emerald", "quartz", "concrete", "ice"]


@perf_time
def set_procedural_pbr():
    Preferences = get_preferences()
        
    for selected_object in bpy.context.selected_objects:
        if selected_object.type != "MESH" and not is_code_ignored("w01") and Preferences.show_warnings:
            trigger_absolute_solver("w01", data=selected_object)
            continue
        elif selected_object.type != "MESH":
            continue

        for slot, material in enumerate(selected_object.data.materials):
            if material is None or not material.use_nodes:
                continue
            
            PBSDF = None
            image = None
            bump_node = None
            proughness_node = None
            pspecular_node = None
            better_animate_node = None
            PNormals = None
            vector_connection = None
            image_difference_X = 1
            image_difference_Y = 1
            Current_node_tree = None
            PProperties = bpy.context.scene.miblend_properties.procedural_pbr_properties
            

            for node in material.node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    PBSDF = node
                    image_texture_node = detect_texture_node(node)
                    image = detect_image_texture(node)

                elif node.type == "BUMP":
                    bump_node = node

                elif node.type == "GROUP":
                    if "PNormals" in node.node_tree.name:
                        PNormals = node
                        Current_node_tree = node.node_tree

                    elif "Procedural Emission & Animation" in node.node_tree.name:
                        better_animate_node = node
                
                elif node.type == "MAP_RANGE":
                    if "Procedural Roughness Node" in node.label:
                        proughness_node = node
                    
                    elif "Procedural Specular Node" in node.label:
                        pspecular_node = node

            if not PBSDF:
                continue

            base_color_connection = GetConnectedSocketTo("Base Color", PBSDF)

            # Use Normals
            if PProperties.use_normals:
                if PProperties.normals_selector == 'Bump' and base_color_connection:
                    if PNormals:
                        material.node_tree.nodes.remove(PNormals)

                    if bump_node is None:
                        bump_node = material.node_tree.nodes.new(type='ShaderNodeBump')
                        bump_node.location = (PBSDF.location.x - 180, PBSDF.location.y - 132)
                        material.node_tree.links.new(base_color_connection, bump_node.inputs['Height'])
                        material.node_tree.links.new(bump_node.outputs['Normal'], PBSDF.inputs['Normal'])

                    bump_node.inputs[0].default_value = PProperties.bump_strength
                    if bpy.app.version >= (4, 4, 1):
                        bump_node.inputs["Filter Width"].default_value = 1.0
                    
                    if bpy.app.version >= (4, 5, 0):
                        bump_node.inputs["Distance"].default_value = 1.0

                elif image_texture_node and image:
                    if bump_node:
                        material.node_tree.nodes.remove(bump_node)

                    if image_texture_node.type == "GROUP":
                        vector_connection = image_texture_node.outputs["Current Frame"]
                    else:
                        vector_connection = GetConnectedSocketTo("Vector", image_texture_node)
                    
                    group_name = f"PNormals; {image.name[:63]}"
                    
                    if PNormals is None:
                        PNormals = material.node_tree.nodes.new(type='ShaderNodeGroup')
                        group_name = f"PNormals; {image.name[:63]}"

                        if group_name in bpy.data.node_groups:
                            Current_node_tree = bpy.data.node_groups[group_name]
                        else:
                            with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                                data_to.node_groups = ["PNormals"]
                            bpy.data.node_groups["PNormals"].name = group_name
                            Current_node_tree = bpy.data.node_groups[group_name]

                        PNormals.node_tree = Current_node_tree
                        PNormals.location = (PBSDF.location.x - 180, PBSDF.location.y - 132)

                    for node in Current_node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            node.image = image
                    
                    PNormals.node_tree.name = group_name
                    
                    if image.size[0] > image.size[1]:
                        image_difference_X = image.size[1] / image.size[0]

                    if image.size[0] < image.size[1]:
                        image_difference_Y = image.size[0] / image.size[1]

                    PNormals.inputs["Size"].default_value = PProperties.pnormals_size
                    PNormals.inputs["Blur"].default_value = PProperties.pnormals_blur
                    PNormals.inputs["Strength"].default_value = PProperties.pnormals_strength
                    PNormals.inputs["Exclude"].default_value = PProperties.pnormals_exclude
                    PNormals.inputs["Min"].default_value = PProperties.pnormals_min
                    PNormals.inputs["Max"].default_value = PProperties.pnormals_max
                    PNormals.inputs["Size X Multiplier"].default_value = PProperties.pnormals_size_x_multiplier * image_difference_X
                    PNormals.inputs["Size Y Multiplier"].default_value = PProperties.pnormals_size_y_multiplier * image_difference_Y

                    material.node_tree.links.new(PNormals.outputs['Normal Map'], PBSDF.inputs['Normal'])

                    if vector_connection:
                        material.node_tree.links.new(vector_connection, PNormals.inputs['Vector'])

            elif PProperties.revert_normals:   
                if bump_node:
                    material.node_tree.nodes.remove(bump_node)
                
                if PNormals:
                    material.node_tree.nodes.remove(PNormals)

            # Change PBSDF Settings                                
            if PProperties.change_bsdf:
                PBSDF.inputs["Roughness"].default_value = PProperties.roughness
                PBSDF.inputs["Specular IOR Level"].default_value = PProperties.specular

            # Use SSS                            
            if PProperties.use_sss and (name_in(SSS_Materials, material.name)[0] or PProperties.sss_skip):
                PBSDF.subsurface_method = PProperties.sss_type

                if PProperties.connect_texture:
                    material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), PBSDF.inputs["Subsurface Radius"])
                else:
                    RemoveLinksFrom(PBSDF.inputs["Subsurface Radius"])

                PBSDF.inputs["Subsurface Weight"].default_value = PProperties.sss_weight
                PBSDF.inputs["Subsurface Scale"].default_value = PProperties.sss_scale

                PBSDF.inputs["Subsurface Radius"].default_value = (1,1,1)
            elif not PProperties.use_sss and PProperties.revert_sss:
                PBSDF.inputs["Subsurface Weight"].default_value = 0

            # Use Translucency
            if PProperties.use_translucency and name_in(TRANSLUCENT_MATERIALS, material.name)[0]:
                PBSDF.inputs["Transmission Weight"].default_value = PProperties.translucency
            elif not PProperties.use_translucency and PProperties.revert_translucency:
                PBSDF.inputs["Transmission Weight"].default_value = 0

            # Make Metals                            
            if PProperties.make_metal and name_in(METALLIC_MATERIALS, material.name)[0]:
                PBSDF.inputs["Metallic"].default_value = PProperties.metal_metallic
                PBSDF.inputs["Roughness"].default_value = PProperties.metal_roughness
                
            # Make Reflections                            
            if PProperties.make_reflections and name_in(REFLECTIVE_MATERIALS, material.name)[0]:
                PBSDF.inputs["Roughness"].default_value = PProperties.reflections_roughness

            # Make Better Emission and Animate Textures
            if PProperties.procedural_emission_and_animation and base_color_connection and image and is_emissive(PBSDF, image.name):
                is_valid, item = name_in(EMISSIVE_MATERIALS.keys(), material.name)

                if is_valid and PProperties.custom_peaa_config:
                    material_properties = EMISSIVE_MATERIALS[item]
                    if material_properties:
                        if not better_animate_node:
                            better_animate_node = create_node_group(material, "Procedural Emission & Animation", (PBSDF.location.x - 200, PBSDF.location.y - 265))

                        if PProperties.randomize:
                            add_modifier(selected_object, "Random Face Value")

                        current_section = None
                        for input_socket in better_animate_node.inputs:
                            if input_socket.name in material_properties:
                                current_section = input_socket.name
                            elif current_section and current_section in material_properties:
                                input_socket.default_value = material_properties.get(current_section, {}).get(input_socket.name, input_socket.default_value)

                        Better_Emission_Dict = material_properties.get("Procedural Emission", {})
                        if Better_Emission_Dict:
                            better_animate_node.inputs["Procedural Emission"].default_value = bool(PProperties.procedural_emission_and_animation and material_properties.get("Procedural Emission", False))
                            better_animate_node.inputs["Camera Strength"].default_value = PProperties.camera_strength
                            better_animate_node.inputs["Non-Camera Strength"].default_value = PProperties.non_camera_strength

                        Procedural_Animation_Dict = material_properties.get("Procedural Animation", {})
                        if PProperties.procedural_animation and material_properties.get("Procedural Animation", False):
                            better_animate_node.inputs["Procedural Animation"].default_value = bool(PProperties.procedural_animation and material_properties.get("Procedural Animation", False))
                            better_animate_node.inputs["Randomize"].default_value = PProperties.randomize and Procedural_Animation_Dict.get("Randomize", False)

                        if GetConnectedSocketTo("Emission Color", PBSDF) is None:
                            material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), PBSDF.inputs["Emission Color"])

                        emit_socket = GetConnectedSocketTo("Emission Strength", PBSDF)
                        if emit_socket and emit_socket.node != better_animate_node:
                            material.node_tree.links.new(emit_socket, better_animate_node.inputs["Multiply"])
                            
                        material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), better_animate_node.inputs["Emission Color"])
                        material.node_tree.links.new(better_animate_node.outputs["Emission Strength"], PBSDF.inputs["Emission Strength"])

                elif not PProperties.custom_peaa_config:
                    if not better_animate_node:
                        better_animate_node = create_node_group(material, "Procedural Emission & Animation", (PBSDF.location.x - 200, PBSDF.location.y - 265))

                    if PProperties.randomize:
                        add_modifier(selected_object, "Random Face Value")
                    
                    better_animate_node.inputs["Procedural Emission"].default_value = PProperties.procedural_emission_and_animation
                    better_animate_node.inputs["Camera Strength"].default_value = PProperties.camera_strength
                    better_animate_node.inputs["Non-Camera Strength"].default_value = PProperties.non_camera_strength
                    
                    if PProperties.procedural_animation:
                        better_animate_node.inputs["Procedural Animation"].default_value = PProperties.procedural_animation
                        better_animate_node.inputs["Randomize"].default_value = PProperties.randomize

                    if GetConnectedSocketTo("Emission Color", PBSDF) is None:
                        material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), PBSDF.inputs["Emission Color"])

                    emit_socket = GetConnectedSocketTo("Emission Strength", PBSDF)
                    if emit_socket and emit_socket.node != better_animate_node:
                        material.node_tree.links.new(emit_socket, better_animate_node.inputs["Multiply"])
                        
                    material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), better_animate_node.inputs["Emission Color"])
                    material.node_tree.links.new(better_animate_node.outputs["Emission Strength"], PBSDF.inputs["Emission Strength"])

            elif PProperties.procedural_emission_and_animation_revert and not PProperties.procedural_emission_and_animation and better_animate_node:
                mult_socket = GetConnectedSocketTo("Multiply", better_animate_node)
                if mult_socket:
                    material.node_tree.links.new(mult_socket, PBSDF.inputs["Emission Strength"])
                material.node_tree.nodes.remove(better_animate_node)

            if Preferences.experimental_features and base_color_connection:
                if PProperties.proughness:
                    if proughness_node is None:
                        proughness_node = material.node_tree.nodes.new(type='ShaderNodeMapRange')
                        proughness_node.label = "Procedural Roughness Node"
                        proughness_node.location = (PBSDF.location.x - 180, PBSDF.location.y - 90)
                        proughness_node.hide = True

                    proughness_node.interpolation_type = PProperties.pr_interpolation
                    proughness_node.inputs["From Max"].default_value = 0.0
                    proughness_node.inputs["From Min"].default_value = 1.0
                    proughness_node.inputs["To Max"].default_value = PBSDF.inputs["Roughness"].default_value
                    proughness_node.inputs["To Min"].default_value = PBSDF.inputs["Roughness"].default_value * PProperties.pr_dif
                    
                    material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), proughness_node.inputs["Value"])
                    material.node_tree.links.new(proughness_node.outputs[0], PBSDF.inputs["Roughness"])

                elif PProperties.pr_revert and proughness_node is not None:
                    material.node_tree.nodes.remove(proughness_node)
                
                if PProperties.pspecular:
                    if pspecular_node is None:
                        pspecular_node = material.node_tree.nodes.new(type='ShaderNodeMapRange')
                        pspecular_node.label = "Procedural Specular Node"
                        pspecular_node.location = (PBSDF.location.x - 180, PBSDF.location.y - 200)
                        pspecular_node.hide = True

                    pspecular_node.interpolation_type = PProperties.ps_interpolation
                    pspecular_node.inputs["From Max"].default_value = 1.0
                    pspecular_node.inputs["From Min"].default_value = 0.0
                    pspecular_node.inputs["To Max"].default_value = PBSDF.inputs["Specular IOR Level"].default_value
                    pspecular_node.inputs["To Min"].default_value = PBSDF.inputs["Specular IOR Level"].default_value * PProperties.ps_dif
                    
                    material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), pspecular_node.inputs["Value"])
                    material.node_tree.links.new(pspecular_node.outputs[0], PBSDF.inputs["Specular IOR Level"])
                    
                elif PProperties.ps_revert and pspecular_node is not None:
                    material.node_tree.nodes.remove(pspecular_node)
