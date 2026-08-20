import os
import bpy
from ..absolute_solver.absolute_solver_logic import trigger_absolute_solver
from ...mib_utils import (get_preferences, is_code_ignored, name_in, perf_time, 
                        detect_texture_node, detect_image_texture, 
                        is_emissive, get_connected_socket_to, create_node_group,
                        add_modifier, remove_links_from, dissolve_node, inject_node,
                        wrap_texture_node_in_closures,
                        place_node_opposite_input)
from ...resources.data import nodes_file, resources_directory, EMISSIVE_MATERIALS


class ProceduralPBR:
    def __init__(self):
        self.is_experimental_features_enabled = get_preferences().experimental_features
        self.is_show_warnings_enabled = get_preferences().show_warnings
        self.procedural_pbr_properties = bpy.context.scene.miblend_properties.procedural_pbr_properties
        self.SSS_Materials = ["leaves", "grass", "tulip", "oxeye daisy", "dandelion", "poppy", "blue orchid", "torchflower",
                            "lily of the valley", "lily pad", "cornflower", "allium", "azure bluet", "azalea", "cactus", "wheat", "hay", "wildflowers",
                            "moss block", "moss carpet", "hanging moss", "eyeblossom", "chorus flower", "bush", "resin"]
        self.TRANSLUCENT_MATERIALS = ["leaves", "glass"]
        self.METALLIC_MATERIALS = ["iron", "gold", "emerald", "copper ; torch", "diamond", "netherite", "minecart", "lantern ; jack", "chain", "anvil", "clock", "cauldron", "spyglass", "rail", "spawner", "bell"]
        self.REFLECTIVE_MATERIALS = ["glass", "ender", "amethyst", "water", "emerald", "quartz", "concrete", "ice"]

    @staticmethod
    def find_nodes_group_by_name(group_name, material):
        return next((node for node in material.node_tree.nodes if node.type == "GROUP" and group_name in node.node_tree.name), None)

    @perf_time
    def apply_procedural_pbr(self):
        for current_object in bpy.context.selected_objects:
            if current_object.type != 'MESH':
                if not is_code_ignored("w01") and self.is_show_warnings_enabled:
                    trigger_absolute_solver("w01", data=current_object)
                continue

            for slot, current_material in enumerate(current_object.data.materials):
                if not current_material:
                    continue

                # Remove after Blender 4.x support ends
                if bpy.app.version < (5, 0, 0) and not current_material.use_nodes:
                    continue
                
                pbsdf_node = next((node for node in current_material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
                
                if not pbsdf_node:
                    continue

                image_texture_node = detect_texture_node(pbsdf_node)
                image = detect_image_texture(pbsdf_node)

                self.apply_pbsdf_tweaks(current_material, pbsdf_node)

                base_color_connection = get_connected_socket_to("Base Color", pbsdf_node)
                if base_color_connection:
                    self.apply_procedural_emission(current_object, current_material, pbsdf_node, image)
                    self.apply_procedural_specular_and_roughness(current_material, pbsdf_node)
                
                self.apply_normals(current_material, pbsdf_node, image_texture_node, image)
                current_material.node_tree.nodes.active = image_texture_node

    def apply_normals(self, current_material, pbsdf_node, image_texture_node, image):
        bump_node = next((node for node in current_material.node_tree.nodes if node.type == "BUMP"), None)
        procedural_normals_node = self.find_nodes_group_by_name("PNormals", current_material)
        procedural_normals_v2_node = self.find_nodes_group_by_name("Procedural Normals V2", current_material)

        if not self.procedural_pbr_properties.use_normals:
            if self.procedural_pbr_properties.revert_normals:
                dissolve_node(current_material, bump_node, None)
                dissolve_node(current_material, procedural_normals_node, None)
                dissolve_node(current_material, procedural_normals_v2_node, None)
            return

        normals_mode = self.procedural_pbr_properties.normals_selector if not self.is_experimental_features_enabled or \
                        bpy.app.version < (5, 1, 0) else self.procedural_pbr_properties.normals_selector_experimental
        normals_size_x_multiplier = 1
        normals_size_y_multiplier = 1
        base_color_connection = get_connected_socket_to("Base Color", pbsdf_node)

        if normals_mode == 'BUMP' and base_color_connection:
            dissolve_node(current_material, procedural_normals_node, None)

            if not bump_node:
                bump_node = current_material.node_tree.nodes.new(type='ShaderNodeBump')
                bump_node.location = (pbsdf_node.location.x - 180, pbsdf_node.location.y - 132)
                current_material.node_tree.links.new(base_color_connection, bump_node.inputs['Height'])
                inject_node(current_material, bump_node, pbsdf_node, "Normal", "Normal")

            bump_node.inputs[0].default_value = self.procedural_pbr_properties.bump_strength
            if bpy.app.version >= (4, 4, 1):
                bump_node.inputs["Filter Width"].default_value = 1.0
            
            if bpy.app.version >= (4, 5, 0) and bump_node.inputs["Distance"].default_value < 1.0:
                bump_node.inputs["Distance"].default_value = 1.0

        elif normals_mode == 'PROCEDURAL_NORMALS' and image_texture_node and image:
            dissolve_node(current_material, bump_node, None)
            vector_connection = None

            if image_texture_node.type == "GROUP":
                vector_connection = image_texture_node.outputs["Current Frame"]
            else:
                vector_connection = get_connected_socket_to("Vector", image_texture_node)
            
            group_name = f"PNormals; {image.name[:63]}"
            
            if not procedural_normals_node:
                procedural_normals_node = current_material.node_tree.nodes.new(type='ShaderNodeGroup')
                group_name = f"PNormals; {image.name[:63]}"

                if group_name in bpy.data.node_groups:
                    current_node_tree = bpy.data.node_groups[group_name]
                else:
                    with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                        data_to.node_groups = ["PNormals"]
                    bpy.data.node_groups["PNormals"].name = group_name
                    current_node_tree = bpy.data.node_groups[group_name]

                procedural_normals_node.node_tree = current_node_tree
                procedural_normals_node.location = (pbsdf_node.location.x - 180, pbsdf_node.location.y - 132)

            else:
                current_node_tree = procedural_normals_node.node_tree

            for node in current_node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    node.image = image
            
            procedural_normals_node.node_tree.name = group_name
            
            if image.size[0] > image.size[1]:
                normals_size_x_multiplier = image.size[1] / image.size[0]

            if image.size[0] < image.size[1]:
                normals_size_y_multiplier = image.size[0] / image.size[1]

            procedural_normals_node.inputs["Size"].default_value = self.procedural_pbr_properties.pnormals_size
            procedural_normals_node.inputs["Blur"].default_value = self.procedural_pbr_properties.pnormals_blur
            procedural_normals_node.inputs["Strength"].default_value = self.procedural_pbr_properties.pnormals_strength
            procedural_normals_node.inputs["Exclude"].default_value = self.procedural_pbr_properties.pnormals_exclude
            procedural_normals_node.inputs["Min"].default_value = self.procedural_pbr_properties.pnormals_min
            procedural_normals_node.inputs["Max"].default_value = self.procedural_pbr_properties.pnormals_max
            procedural_normals_node.inputs["Size X Multiplier"].default_value = normals_size_x_multiplier
            procedural_normals_node.inputs["Size Y Multiplier"].default_value = normals_size_y_multiplier

            current_material.node_tree.links.new(procedural_normals_node.outputs['Normal Map'], pbsdf_node.inputs['Normal'])

            if vector_connection:
                current_material.node_tree.links.new(vector_connection, procedural_normals_node.inputs['Vector'])
        
        elif normals_mode == 'PROCEDURAL_NORMALS_V2' and self.is_experimental_features_enabled and image_texture_node and image:
            existing_node_names = {
                node.name for node in current_material.node_tree.nodes
            }
            image_texture_closure_output = wrap_texture_node_in_closures(image_texture_node, current_material)
            
            procedural_normals_v2_node = create_node_group(current_material, "Procedural Normals V2", (pbsdf_node.location.x - 185, pbsdf_node.location.y - 155), os.path.join(resources_directory, "Procedural Normals V2.blend"), True)

            if image.size[0] > image.size[1]:
                normals_size_x_multiplier = image.size[1] / image.size[0]

            if image.size[0] < image.size[1]:
                normals_size_y_multiplier = image.size[0] / image.size[1]

            procedural_normals_v2_node.inputs["Strength"].default_value = self.procedural_pbr_properties.procedural_normals_v2_size
            procedural_normals_v2_node.inputs["Strength X Multiplier"].default_value = normals_size_x_multiplier
            procedural_normals_v2_node.inputs["Strength Y Multiplier"].default_value = normals_size_y_multiplier

            current_material.node_tree.links.new(image_texture_closure_output.outputs['Closure'], procedural_normals_v2_node.inputs['Closure'])
            current_material.node_tree.links.new(procedural_normals_v2_node.outputs['Normal'], pbsdf_node.inputs['Normal'])
            closure_socket = image_texture_closure_output.outputs['Closure']
            evaluate_node = next(link.to_node for link in closure_socket.links if link.to_node.bl_idname == "NodeEvaluateClosure")
            layout_items = (
                (procedural_normals_v2_node, procedural_normals_v2_node.outputs['Normal'], pbsdf_node.inputs['Normal'], (0, -22)),
                (evaluate_node, evaluate_node.outputs['Color'], pbsdf_node.inputs['Base Color'], (0, 0)),
                (image_texture_closure_output, closure_socket, evaluate_node.inputs['Closure'], (0, 0)),
            )
            if procedural_normals_v2_node.name not in existing_node_names:
                layout_names = {node.name for node, *_ in layout_items}
                original_locations = {
                    node.name: tuple(node.location) for node, *_ in layout_items
                }
                parking_x = pbsdf_node.location.x - 10000
                image_texture_closure_output.location = (parking_x, pbsdf_node.location.y + 10000)
                evaluate_node.location = (parking_x, pbsdf_node.location.y + 10500)
                occupied_nodes = [
                    node for node in current_material.node_tree.nodes
                    if node.name not in layout_names
                ]

                for node, source_socket, target_socket, offset in layout_items:
                    if place_node_opposite_input(
                            source_socket, target_socket,
                            nodes_to_avoid=occupied_nodes, offset=offset):
                        occupied_nodes.append(node)
                    else:
                        node.location = original_locations[node.name]

    def apply_procedural_emission(self, current_object, current_material, pbsdf_node, image):
        procedural_emission_node = self.find_nodes_group_by_name("Procedural Emission", current_material)
        _is_valid, item = name_in(EMISSIVE_MATERIALS.keys(), current_material.name)
        emission_settings_dict: dict[str, float] = EMISSIVE_MATERIALS.get(item, {})

        if not image or not is_emissive(pbsdf_node, image.name) or not self.procedural_pbr_properties.use_procedural_emission:
            if self.procedural_pbr_properties.revert_procedural_emission:
                dissolve_node(current_material, procedural_emission_node, "Strength Multiply")
            return

        if not procedural_emission_node:
            procedural_emission_node = create_node_group(current_material, "Procedural Emission", (pbsdf_node.location.x - 200, pbsdf_node.location.y - 265))

        if self.procedural_pbr_properties.randomize_emission_strength:
            add_modifier(current_object, "Random Face Value")

        if emission_settings_dict and self.procedural_pbr_properties.use_procedural_emission_custom_config:
            for setting, value in emission_settings_dict.items():
                procedural_emission_node.inputs[setting].default_value = value

        procedural_emission_node.inputs["Camera Strength"].default_value = self.procedural_pbr_properties.camera_emission_strength
        procedural_emission_node.inputs["Non-Camera Strength"].default_value = self.procedural_pbr_properties.non_camera_emission_strength
        procedural_emission_node.inputs["Randomize Strength"].default_value = self.procedural_pbr_properties.randomize_emission_strength and emission_settings_dict.get("Randomize Strength", False)

        if get_connected_socket_to("Emission Color", pbsdf_node):
            current_material.node_tree.links.new(get_connected_socket_to("Emission Color", pbsdf_node), procedural_emission_node.inputs["Emission Color"])
        else:
            current_material.node_tree.links.new(get_connected_socket_to("Base Color", pbsdf_node), pbsdf_node.inputs["Emission Color"])
        
        inject_node(current_material, procedural_emission_node, pbsdf_node, "Emission Strength", "Strength Multiply")
    
    def apply_procedural_specular_and_roughness(self, current_material, pbsdf_node):
        if not self.is_experimental_features_enabled:
            return

        procedural_roughness_node = next((node for node in current_material.node_tree.nodes if node.type == "MAP_RANGE"
                                            and "Procedural Roughness Node" in node.label), None)
        procedural_specular_node = next((node for node in current_material.node_tree.nodes if node.type == "MAP_RANGE" 
                                            and "Procedural Specular Node" in node.label), None)

        if not self.procedural_pbr_properties.use_procedural_specular_and_roughness:
            if self.procedural_pbr_properties.revert_procedural_specular_and_roughness:
                dissolve_node(current_material, procedural_specular_node, None)
                dissolve_node(current_material, procedural_roughness_node, None)
            return

        if not procedural_specular_node:
            procedural_specular_node = current_material.node_tree.nodes.new(type='ShaderNodeMapRange')
            procedural_specular_node.label = "Procedural Specular Node"
            procedural_specular_node.location = (pbsdf_node.location.x - 180, pbsdf_node.location.y - 200)
            procedural_specular_node.hide = True

        if not procedural_roughness_node:
            procedural_roughness_node = current_material.node_tree.nodes.new(type='ShaderNodeMapRange')
            procedural_roughness_node.label = "Procedural Roughness Node"
            procedural_roughness_node.location = (pbsdf_node.location.x - 180, pbsdf_node.location.y - 90)
            procedural_roughness_node.hide = True

        procedural_specular_node.interpolation_type = self.procedural_pbr_properties.procedural_specular_interpolation
        procedural_specular_node.inputs["From Max"].default_value = 1.0
        procedural_specular_node.inputs["From Min"].default_value = 0.0
        procedural_specular_node.inputs["To Max"].default_value = pbsdf_node.inputs["Specular IOR Level"].default_value
        procedural_specular_node.inputs["To Min"].default_value = pbsdf_node.inputs["Specular IOR Level"].default_value * self.procedural_pbr_properties.procedural_specular_difference

        procedural_roughness_node.interpolation_type = self.procedural_pbr_properties.procedural_roughness_interpolation
        procedural_roughness_node.inputs["From Max"].default_value = 0.0
        procedural_roughness_node.inputs["From Min"].default_value = 1.0
        procedural_roughness_node.inputs["To Max"].default_value = pbsdf_node.inputs["Roughness"].default_value
        procedural_roughness_node.inputs["To Min"].default_value = pbsdf_node.inputs["Roughness"].default_value * self.procedural_pbr_properties.procedural_roughness_difference
        
        current_material.node_tree.links.new(get_connected_socket_to("Base Color", pbsdf_node), procedural_specular_node.inputs["Value"])
        current_material.node_tree.links.new(procedural_specular_node.outputs[0], pbsdf_node.inputs["Specular IOR Level"])

        current_material.node_tree.links.new(get_connected_socket_to("Base Color", pbsdf_node), procedural_roughness_node.inputs["Value"])
        current_material.node_tree.links.new(procedural_roughness_node.outputs[0], pbsdf_node.inputs["Roughness"])

    def apply_pbsdf_tweaks(self, current_material, pbsdf_node):
        if not self.procedural_pbr_properties.use_pbsdf_tweaks:
            if name_in(self.SSS_Materials, current_material.name)[0] and self.procedural_pbr_properties.revert_sss:
                pbsdf_node.inputs["Subsurface Weight"].default_value = 0

            if name_in(self.TRANSLUCENT_MATERIALS, current_material.name)[0] and self.procedural_pbr_properties.revert_translucency:
                pbsdf_node.inputs["Transmission Weight"].default_value = 0
            return

        # Global PBSDF Tweaks
        pbsdf_node.inputs["Roughness"].default_value = self.procedural_pbr_properties.roughness
        pbsdf_node.inputs["Specular IOR Level"].default_value = self.procedural_pbr_properties.specular

        # Smart PBSDF Tweaks
        if self.procedural_pbr_properties.use_sss and name_in(self.SSS_Materials, current_material.name)[0]:
            pbsdf_node.subsurface_method = self.procedural_pbr_properties.sss_type

            if self.procedural_pbr_properties.use_sss_connect_texture_to_radius:
                current_material.node_tree.links.new(get_connected_socket_to("Base Color", pbsdf_node), pbsdf_node.inputs["Subsurface Radius"])
            else:
                remove_links_from(pbsdf_node.inputs["Subsurface Radius"])

            pbsdf_node.inputs["Subsurface Weight"].default_value = self.procedural_pbr_properties.sss_weight
            pbsdf_node.inputs["Subsurface Scale"].default_value = self.procedural_pbr_properties.sss_scale

            if pbsdf_node.inputs["Subsurface Radius"].default_value == (0.0, 0.0, 0.0):
                pbsdf_node.inputs["Subsurface Radius"].default_value = (1,1,1)
        
        elif not self.procedural_pbr_properties.use_sss and name_in(self.SSS_Materials, current_material.name)[0] and self.procedural_pbr_properties.revert_sss:
            pbsdf_node.inputs["Subsurface Weight"].default_value = 0

        if self.procedural_pbr_properties.use_translucency and name_in(self.TRANSLUCENT_MATERIALS, current_material.name)[0]:
            pbsdf_node.inputs["Transmission Weight"].default_value = self.procedural_pbr_properties.translucency

        elif not self.procedural_pbr_properties.use_translucency and name_in(self.TRANSLUCENT_MATERIALS, current_material.name)[0] and self.procedural_pbr_properties.revert_translucency:
                pbsdf_node.inputs["Transmission Weight"].default_value = 0

        if self.procedural_pbr_properties.use_reflectiveness and name_in(self.REFLECTIVE_MATERIALS, current_material.name)[0]:
            pbsdf_node.inputs["Roughness"].default_value = self.procedural_pbr_properties.reflections_roughness

        if self.procedural_pbr_properties.use_metallic and name_in(self.METALLIC_MATERIALS, current_material.name)[0]:
            pbsdf_node.inputs["Metallic"].default_value = self.procedural_pbr_properties.metallic
            pbsdf_node.inputs["Roughness"].default_value = self.procedural_pbr_properties.metallic_roughness
