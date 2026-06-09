import bpy
from ...mib_utils import (dprint, get_preferences, is_code_ignored, name_in, perf_time, 
                        detect_world_exporter, detect_texture_node, detect_image_texture, 
                        is_emissive, format_texture_name, is_gray, GetConnectedSocketTo, 
                        create_node_group, inject_node, dissolve_node)
from ..absolute_solver.absolute_solver_logic import trigger_absolute_solver


class FixWorld:
    def __init__(self):
        self.is_experimental_features_enabled = get_preferences().experimental_features
        self.is_show_warnings_enabled = get_preferences().show_warnings
        self.world_properties = bpy.context.scene.miblend_properties.world_properties
        self.GRASS_COLORS = {
            "Forest": (0.226964, 0.617207, 0.088656),
            "Birch": (0.242279, 0.396756, 0.16203),
            "Taiga": (0.25415, 0.467784, 0.250158),
            "Dark Forest": (0.021219, 0.03434, 0.003035),
            "Bad Land": (0.278893, 0.219526, 0.074214),
        }

        self.FOLIAGE_COLORS = {
            "Forest": (0.227161, 0.614651, 0.089036),
            "Taiga": (0.152925, 0.366253, 0.147027),
            "Jungle": (0.2455, 0.664272, 0.096224),
            "Mangrove": (0.314244, 0.522575, 0.023661),
            "Savanna": (0.618196, 0.49695, 0.081344),
        }

        self.BACKFACE_CULLING_MATERIALS = ["glass", "door", "nether portal", "redstone torch"]
    
    @staticmethod
    def find_nodes_group_by_name(group_name, material):
        return next((node for node in material.node_tree.nodes if node.type == "GROUP" and group_name in node.node_tree.name), None)

    @perf_time
    def fix_world(self):
        for current_object in bpy.context.selected_objects:
            if not current_object.type == 'MESH':
                if not is_code_ignored("w01") and self.is_show_warnings_enabled:
                    trigger_absolute_solver("w01", data=current_object)
                continue

            current_world_exporter = detect_world_exporter(current_object)

            if current_world_exporter == "unknown" and not is_code_ignored("w03") and self.is_show_warnings_enabled:
                trigger_absolute_solver("w03")
                continue

            current_object["MiBlend ID"] = "World"

            self.apply_force_shading_flat()

            for current_material in current_object.data.materials:
                if not current_material:
                    continue

                # Remove after Blender 4.x support ends
                if bpy.app.version < (5, 0, 0) and not current_material.use_nodes:
                    continue

                dprint(f"Material: {current_material.name}", is_deep=True, zone="fw")

                current_material.blend_method = 'HASHED'
                
                if bpy.app.version < (4, 3, 0):
                    current_material.shadow_method = 'HASHED'

                self.apply_combine_texture_nodes_duplicates(current_material)

                image_texture_nodes_list = [node for node in current_material.node_tree.nodes if node.type == "TEX_IMAGE"]
                for node in image_texture_nodes_list:
                    if current_world_exporter == "mineways" and node.image:
                        if node.image.name.replace(".png", "").endswith("_y"):
                            node.image.name = node.image.name.replace("_y", "", 1)
                        elif node.image.name.replace(".png", "").endswith("_a"):
                            current_material.node_tree.nodes.remove(node)
                            continue
                    node.interpolation = "Closest"

                pbsdf_node = next((node for node in current_material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
                image_texture_node = detect_texture_node(pbsdf_node)
                image = detect_image_texture(pbsdf_node)

                if not image_texture_node or not pbsdf_node:
                    continue

                if not GetConnectedSocketTo("Alpha", pbsdf_node):
                    current_material.node_tree.links.new(image_texture_node.outputs["Alpha"], pbsdf_node.inputs["Alpha"])
                
                # Emission
                if is_emissive(pbsdf_node, image.name):
                    if not GetConnectedSocketTo("Emission Color", pbsdf_node):
                        current_material.node_tree.links.new(GetConnectedSocketTo("Base Color", pbsdf_node), pbsdf_node.inputs["Emission Color"])

                    if pbsdf_node.inputs["Emission Strength"].default_value == 0:
                        pbsdf_node.inputs["Emission Strength"].default_value = 1
                
                self.apply_backface_culling(current_material, pbsdf_node)
                self.apply_lazy_biome_color_fix(current_material, pbsdf_node, image_texture_node, image)
                self.apply_animated_texture_fix(current_material, pbsdf_node, image_texture_node, image)
    
    @staticmethod
    def get_node_suffix_number(node_name):
        parts = node_name.rsplit(".", 1)
        if len(parts) > 1 and parts[-1].isdigit():
            return int(parts[-1])
        return 0

    def get_all_linked_nodes(self, node, visited=None):
        if not visited:
            visited = set()
        
        if node in visited:
            return visited
        
        visited.add(node)
        
        for input_socket in node.inputs:
            if not input_socket.is_linked:
                continue
                
            for link in input_socket.links:
                self.get_all_linked_nodes(link.from_node, visited)
        
        return visited

    def get_linked_nodes(self, node, input_name):
        if input_name not in node.inputs or not node.inputs[input_name].is_linked:
            return []
        
        linked_nodes = []
        for link in node.inputs[input_name].links:
            linked_nodes.append(link.from_node)
            linked_nodes.extend(self.get_all_linked_nodes(link.from_node))
        
        return linked_nodes

    def apply_combine_texture_nodes_duplicates(self, current_material):
        texture_nodes = [node for node in current_material.node_tree.nodes if node.type == "TEX_IMAGE"]
        
        if not texture_nodes:
            return
        
        image_to_nodes = {}
        for node in texture_nodes:
            if node.image:
                if node.image not in image_to_nodes:
                    image_to_nodes[node.image] = []
                image_to_nodes[node.image].append(node)
            else:
                current_material.node_tree.nodes.remove(node)
        
        for image, nodes in image_to_nodes.items():
            if len(nodes) < 2:
                continue

            nodes.sort(key=lambda node: ('.' in node.name, self.get_node_suffix_number(node.name)))
            
            node_to_keep = nodes[0]
            nodes_to_remove = nodes[1:]
            
            for node in nodes_to_remove:
                if any(input.is_linked for input in node.inputs):
                    continue
                
                for output_idx, output in enumerate(node.outputs):
                    if not output.links:
                        continue
                        
                    for link in output.links:
                        current_material.node_tree.links.new(node_to_keep.outputs[output_idx], link.to_socket)
                
                current_material.node_tree.nodes.remove(node)

    def apply_force_shading_flat(self):
        current_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        try:
            bpy.ops.object.shade_flat()
        except Exception:
            dprint("Failed to set shading to flat for object: " + bpy.context.object.name, zone="fw")
        bpy.ops.object.mode_set(mode=current_mode)

    def apply_backface_culling(self, current_material, pbsdf_node):
        if not self.world_properties.use_backface_culling or not name_in(self.BACKFACE_CULLING_MATERIALS, current_material.name)[0]:
            current_material.use_backface_culling = False
            backface_culling_node = self.find_nodes_group_by_name("Backface Culling", current_material)
            dissolve_node(current_material, backface_culling_node)
            return

        current_material.use_backface_culling = True
        backface_culling_node = create_node_group(current_material, "Backface Culling", (pbsdf_node.location.x - 170, pbsdf_node.location.y - 110), exists_check = True)
        inject_node(current_material, backface_culling_node, pbsdf_node, "Alpha")
    
    def apply_lazy_biome_color_fix(self, current_material, pbsdf_node, image_texture_node, image):
        if not self.world_properties.use_lazy_biome_fix or not is_gray(image.name):
            lazy_biome_fix_node = self.find_nodes_group_by_name("Lazy Biome Color Fix v2", current_material)
            dissolve_node(current_material, lazy_biome_fix_node)
            return

        texture_parts = format_texture_name(image.name)

        lazy_biome_fix_node = create_node_group(current_material, "Lazy Biome Color Fix v2", (pbsdf_node.location.x - 170, pbsdf_node.location.y - 20), exists_check = True)
        inject_node(current_material, lazy_biome_fix_node, pbsdf_node, "Base Color")
        
        if "fern" in texture_parts or "spruce" in texture_parts:
            biome = "Taiga"
        elif "dark" in texture_parts:
            biome = "Dark Forest"
        elif "mangrove" in texture_parts:
            biome = "Mangrove"
        elif "jungle" in texture_parts:
            biome = "Jungle"
        elif "acacia" in texture_parts:
            biome = "Savanna"
        elif "birch" in texture_parts:
            biome = "Birch"
        else:
            biome = "Forest"

        if all(i in texture_parts for i in ["grass", "block", "side"]):
            lazy_biome_fix_node.inputs["Biome Color"].default_value = tuple(self.GRASS_COLORS.get(biome, lazy_biome_fix_node.inputs["Biome Color"].default_value)[:3]) + (1.0,)
            lazy_biome_fix_node.inputs["Mode"].default_value = 2

        elif "grass" in texture_parts:
            lazy_biome_fix_node.inputs["Biome Color"].default_value = tuple(self.GRASS_COLORS.get(biome, lazy_biome_fix_node.inputs["Biome Color"].default_value)[:3]) + (1.0,)
            lazy_biome_fix_node.inputs["Mode"].default_value = 1

        elif "water" in texture_parts:
            lazy_biome_fix_node.inputs["Biome Color"].default_value = (0.066625, 0.135633, 1.0, 1.0)
            lazy_biome_fix_node.inputs["Mode"].default_value = 3

        elif "redstone" in texture_parts:
            lazy_biome_fix_node.inputs["Biome Color"].default_value = (0.066625, 0.135633, 1.0, 1.0)
            lazy_biome_fix_node.inputs["Mode"].default_value = 4
        
        else:
            lazy_biome_fix_node.inputs["Biome Color"].default_value = tuple(self.FOLIAGE_COLORS.get(biome, lazy_biome_fix_node.inputs["Biome Color"].default_value)[:3]) + (1.0,)
            lazy_biome_fix_node.inputs["Mode"].default_value = 1

        current_material.node_tree.nodes.active = image_texture_node

    def apply_animated_texture_fix(self, current_material, pbsdf_node, image_texture_node, image):
        if image_texture_node.type == "GROUP" or image.size[0] == 0:
            return
        
        frames = max(1, int(image.size[1] / image.size[0]))
        x_divider = 1.0

        if name_in(["lava flow"], image.name, True)[0]:
            frames *= 2
            x_divider = 2.0
        
        if not self.world_properties.use_animated_uv_fix or frames == 1:
            animated_uv_fix_node = self.find_nodes_group_by_name("Animated UV Fix", current_material)
            dissolve_node(current_material, animated_uv_fix_node)
            return

        texture_animator_node = self.find_nodes_group_by_name("Texture Animator", current_material)
        dissolve_node(current_material, texture_animator_node)

        animated_uv_fix_node = create_node_group(current_material, "Animated UV Fix", (image_texture_node.location.x - 200, image_texture_node.location.y - 220), exists_check = True)
        inject_node(current_material, animated_uv_fix_node, image_texture_node, "Vector")

        animated_uv_fix_node.inputs["Frames"].default_value = frames
        animated_uv_fix_node.inputs["X Divider"].default_value = x_divider