import bpy, os, zipfile, traceback
from ..MIB_API import *
from ..Data import *
from ..Utils.Absolute_Solver import Call_AS

@ Perf_Time
def replace_materials():
    original_materials_list = {}
    replaced_materials_path = os.path.join(materials_folder, "Replaced Materials.blend")
    with bpy.data.libraries.load(replaced_materials_path, link=False) as (data_from, data_to):
        for material_name in data_from.materials:
            split_name = material_name.split(" | ")
        
            if len(split_name) > 1 and "Dev" not in split_name:
                original_materials_list[split_name[0]] = split_name[1]

    if len(original_materials_list) == 0:
        return
    
    for selected_object in bpy.context.selected_objects:
        if not is_mesh(selected_object) and not is_code_ignored("w01") and bpy.context.preferences.addons[str(__package__).split(".")[0]].preferences.show_warnings:
            Call_AS("w01", selected_object)
            continue
        
        elif not is_mesh(selected_object):
            continue

        for slot, material in enumerate(selected_object.data.materials):
            if material is None or not material.use_nodes:
                continue

            for material_part in format_material_name(material.name):
                if upgraded_material := original_materials_list.get(material_part, None):
                    if upgraded_material not in bpy.data.materials:
                        try:
                            with bpy.data.libraries.load(replaced_materials_path, link=False) as (data_from, data_to):
                                data_to.materials = [f"{material_part} | {upgraded_material}"]
                        except Exception as error:
                            Call_AS("e03", error, replaced_materials_path)
                            
                    appended_material = bpy.data.materials.get(f"{material_part} | {upgraded_material}")
                    appended_material.name = upgraded_material
                    selected_object.data.materials[slot] = appended_material
                    break

class FixWorld():
    def __init__(self):
        self.is_experimental_features_enabled = bpy.context.preferences.addons[str(__package__).split(".")[0]].preferences.experimental_features
        self.is_show_warnings_enabled = bpy.context.preferences.addons[str(__package__).split(".")[0]].preferences.show_warnings
        self.world_properties = bpy.context.scene.miblend_properties.world_properties

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

    @staticmethod
    def get_node_suffix_number(node_name):
        parts = node_name.rsplit(".", 1)
        if len(parts) > 1 and parts[-1].isdigit():
            return int(parts[-1])
        return 0

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
    
    @staticmethod
    def find_node_by_type(node_type, material):
        return next((node for node in material.node_tree.nodes if node.type == node_type), None)
    
    @staticmethod
    def find_nodes_group_by_name(group_name, material):
        return next((node for node in material.node_tree.nodes if node.type == "GROUP" and group_name in node.node_tree.name), None)

    @ Perf_Time
    def fix_world(self):
        for current_object in bpy.context.selected_objects:
            if not current_object.type == 'MESH':
                if not is_code_ignored("w01") and self.is_show_warnings_enabled:
                    Call_AS("w01", data=current_object)
                continue

            current_world_exporter = detect_world_exporter(current_object)

            if current_world_exporter == "unknown" and not is_code_ignored("w03") and self.is_show_warnings_enabled:
                Call_AS("w03")
                continue

            current_object["MiBlend ID"] = "World"

            self.apply_force_shading_flat()
            self.apply_remove_doubles()

            for current_material in current_object.data.materials:
                if not current_material:
                    continue

                # Remove after Blender 5.x support ends
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

                pbsdf_node = self.find_node_by_type("BSDF_PRINCIPLED", current_material)
                image_texture_node = detect_texture_node(pbsdf_node)
                image = detect_image_texture(pbsdf_node)

                if not image_texture_node or not pbsdf_node:
                    continue

                if not GetConnectedSocketTo("Alpha", pbsdf_node):
                    current_material.node_tree.links.new(image_texture_node.outputs["Alpha"], pbsdf_node.inputs["Alpha"])
                
                # Emission
                if EmissionMode(pbsdf_node, image.name):
                    if not GetConnectedSocketTo(PBSDF_compability("Emission Color"), pbsdf_node):
                        current_material.node_tree.links.new(GetConnectedSocketTo("Base Color", pbsdf_node), pbsdf_node.inputs[PBSDF_compability("Emission Color")])

                    if (EmissionMode(pbsdf_node, image.name) == 1 or EmissionMode(pbsdf_node, image.name) == 3) and pbsdf_node.inputs["Emission Strength"].default_value == 0:
                        pbsdf_node.inputs["Emission Strength"].default_value = 1
                
                self.apply_backface_culling(current_material, pbsdf_node)
                self.apply_lazy_biome_color_fix(current_material, pbsdf_node, image_texture_node, image)
                self.apply_animated_texture_fix(current_material, pbsdf_node, image_texture_node, image)
    
    def apply_force_shading_flat(self):
        if not self.world_properties.force_shade_flat or not self.is_experimental_features_enabled:
            return

        current_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.shade_flat()
        bpy.ops.object.mode_set(mode=current_mode)
    
    def apply_remove_doubles(self):
        if not self.world_properties.remove_doubles or not self.is_experimental_features_enabled:
            return

        current_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.edge_split(type='VERT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode=current_mode)
    
    def apply_backface_culling(self, current_material, pbsdf_node):
        if not self.world_properties.backface_culling or not name_in(Backface_Culling_Materials, current_material.name)[0]:
            current_material.use_backface_culling = False
            backface_culling_node = self.find_nodes_group_by_name("Backface Culling", current_material)
            dissolve_node(current_material, backface_culling_node)
            return

        current_material.use_backface_culling = True
        backface_culling_node = create_node_group(current_material, "Backface Culling", (pbsdf_node.location.x - 170, pbsdf_node.location.y - 110), exists_check = True)
        inject_node(current_material, backface_culling_node, pbsdf_node, "Alpha")
    
    def apply_lazy_biome_color_fix(self, current_material, pbsdf_node, image_texture_node, image):
        texture_parts = format_texture_name(image.name)

        # Remove in v0.8
        use_legacy_mode = any(i for i in ["grass", "block", "side"] if i not in texture_parts)
        lazy_biome_color_fix_node_name = "Lazy Biome Color Fix" if use_legacy_mode else "Lazy Biome Color Fix v2"

        if not self.world_properties.lazy_biome_fix or not is_gray(image.name):
            lazy_biome_fix_node = self.find_nodes_group_by_name(lazy_biome_color_fix_node_name, current_material)
            dissolve_node(current_material, lazy_biome_fix_node)
            return

        lazy_biome_fix_node = create_node_group(current_material, lazy_biome_color_fix_node_name, (pbsdf_node.location.x - 170, pbsdf_node.location.y - 20), exists_check = True)
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

        # Remove in v0.8
        if not use_legacy_mode:
            lazy_biome_fix_node.inputs["Mode"].default_value = 2
            lazy_biome_fix_node.inputs["Biome Color"].default_value = tuple(Grass_Color.get(biome, lazy_biome_fix_node.inputs["Biome Color"].default_value)[:3]) + (1.0,)
            # make the node active for proper workbench render
            return
            
        if "grass" in texture_parts:
            lazy_biome_fix_node.inputs["Mode"].default_value = 2

        elif "water" in texture_parts:
            lazy_biome_fix_node.inputs["Mode"].default_value = 3

        elif "redstone" in texture_parts:
            lazy_biome_fix_node.inputs["Mode"].default_value = 4

        lazy_biome_fix_node.inputs["Grass Color"].default_value = tuple(Grass_Color.get(biome, lazy_biome_fix_node.inputs["Grass Color"].default_value)[:3]) + (1.0,)
        lazy_biome_fix_node.inputs["Foliage Color"].default_value = tuple(Foliage_Color.get(biome, lazy_biome_fix_node.inputs["Foliage Color"].default_value)[:3]) + (1.0,)

        # make the node active for proper workbench render

    def apply_animated_texture_fix(self, current_material, pbsdf_node, image_texture_node, image):
        if image_texture_node.type == "GROUP" or image.size[0] == 0:
            return

        if name_in(["lava flow"], image.name, True)[0]:
            frames = int(image.size[1] / image.size[0])*2
            x_divider = 2.0
        else:
            frames = int(image.size[1] / image.size[0])
            x_divider = 1.0
        
        if not self.world_properties.animated_uv_fix or frames == 1:
            animated_uv_fix_node = self.find_nodes_group_by_name("Animated UV Fix", current_material)
            dissolve_node(current_material, animated_uv_fix_node)
            return

        texture_animator_node = self.find_nodes_group_by_name("Texture Animator", current_material)
        dissolve_node(current_material, texture_animator_node)

        animated_uv_fix_node = create_node_group(current_material, "Animated UV Fix", (image_texture_node.location.x - 200, image_texture_node.location.y - 220), exists_check = True)
        inject_node(current_material, animated_uv_fix_node, image_texture_node, "Vector")

        animated_uv_fix_node.inputs["Frames"].default_value = frames
        animated_uv_fix_node.inputs["X Divider"].default_value = x_divider

@Perf_Time
def recreate_env(self):

    scene = bpy.context.scene
    world = scene.world

    # Sky
    if self.reset_settings:
        world_material = bpy.context.scene.world.node_tree
        group = bpy.data.node_groups["MiBlend Sky"]

        for node in world_material.nodes:
            if node.type == 'GROUP' and "MiBlend Sky" in node.node_tree.name:
                if blender_version(">= 4.0.0"):
                    for socket in node.inputs:
                        try:
                            for i, vector_value in enumerate(socket.default_value, 1):
                                vector_value = group.interface.items_tree[socket.name].default_value[i]
                        except:
                            socket.default_value = group.interface.items_tree[socket.name].default_value
                else:
                    try:
                        for i, vector_value in enumerate(socket.default_value, 1):
                            vector_value = group.inputs[socket.name].default_value[i]
                    except:
                            socket.default_value = group.inputs[socket.name].default_value

    if self.create_sky == 'Recreate Sky':
        if world == bpy.data.worlds.get(world_material_name) and bpy.data.worlds.get(world_material_name) is not None:
            bpy.data.worlds.remove(bpy.data.worlds.get(world_material_name), do_unlink=True)
        
        for group in bpy.data.node_groups:
            if "MiBlend" in group.name:
                bpy.data.node_groups.remove(group)

        create_env("Sky")

    elif self.create_sky == 'Create Sky' and world_material_name in bpy.data.worlds:
        bpy.context.scene.world = bpy.data.worlds.get(world_material_name)

    # Fog
    if self.create_fog == 'Recreate Fog':
        for obj in scene.objects:
            if obj.get("MiBlend ID") == "Fog":
                bpy.data.objects.remove(obj, do_unlink=True)

        if fog_node_tree_name in bpy.data.node_groups:
            bpy.data.node_groups.remove(bpy.data.node_groups.get(fog_node_tree_name))

        if "Fog" in bpy.data.materials:
            bpy.data.materials.remove(bpy.data.materials.get("Fog"))

        create_env("Fog")

    elif self.create_fog == 'Create Fog':
        
        if "Fog" in bpy.data.materials:
            bpy.data.materials["Fog"]

        if fog_node_tree_name in bpy.data.node_groups:
            if not any(obj.get("MiBlend ID") == "Fog" for obj in scene.objects):
                bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
                bpy.context.object.name = "Clouds"
                bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
                geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
                geonodes_modifier.node_group = bpy.data.node_groups.get(clouds_node_tree_name)

            bpy.context.object["MiBlend ID"] = "Clouds"

    # Clouds
    if self.create_clouds == 'Recreate Clouds':
        for obj in scene.objects:
            if obj.get("MiBlend ID") == "Clouds":
                bpy.data.objects.remove(obj, do_unlink=True)

        if clouds_node_tree_name in bpy.data.node_groups:
            bpy.data.node_groups.remove(bpy.data.node_groups.get(clouds_node_tree_name))

        if "Clouds" in bpy.data.materials:
            bpy.data.materials.remove(bpy.data.materials.get("Clouds"))
        
        create_env("Clouds")
    
    elif self.create_clouds == 'Create Clouds':
        
        if "Clouds" in bpy.data.materials:
            bpy.data.materials["Clouds"]

        if clouds_node_tree_name in bpy.data.node_groups:
            if not any(obj.get("MiBlend ID") == "Clouds" for obj in scene.objects):
                bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
                bpy.context.object.name = "Clouds"
                bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
                geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
                geonodes_modifier.node_group = bpy.data.node_groups.get(clouds_node_tree_name)

            bpy.context.object["MiBlend ID"] = "Clouds"

@ Perf_Time
def create_env(mode=None):

    def clouds_file_comp():
        return "4.0" if blender_version(">= 4.0.0") else "3.6"
    
    scene = bpy.context.scene
    MIB_env_collection = bpy.data.collections.get("MiBlend Environment", None)
    clouds_path = os.path.join(main_directory, "Materials", f"Clouds Generator {clouds_file_comp()}.blend")
    world = scene.world
    sky_exists = False
    fog_exists = False
    clouds_exists = False

    if any(obj.get("MiBlend ID") == "Clouds" for obj in scene.objects):
        clouds_exists = True
    
    if any(obj.get("MiBlend ID") == "Fog" for obj in scene.objects):
        fog_exists = True

    if world is not None and "MiBlend Sky" in bpy.data.node_groups:
        if world_material_name in bpy.data.worlds:
            sky_exists = True
    
    if (clouds_exists or sky_exists or fog_exists) and mode == None:
        bpy.ops.special.recreate_env('INVOKE_DEFAULT')

    else:
        # Create Sky
        if (scene.miblend_properties.env_properties.create_sky and mode == None) or mode == "Sky":
            if not os.path.exists(nodes_file):
                Call_AS("e03", traceback.format_exc(), "Nodes.blend")

            if world_material_name not in bpy.data.worlds:
                with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                    data_to.worlds = [world_material_name]
                appended_world_material = bpy.data.worlds.get(world_material_name)
            else:
                appended_world_material = bpy.data.worlds[world_material_name]
            bpy.context.scene.world = appended_world_material

        # Create Fog
        if (scene.miblend_properties.env_properties.create_fog and mode == None) or mode == "Fog":
    
            if not MIB_env_collection:
                MIB_env_collection = bpy.data.collections.new("MiBlend Environment")
                bpy.context.scene.collection.children.link(MIB_env_collection)

            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_cube_add(size=1.0, enter_editmode=False, align='WORLD', location=(0, 0, 50))
            fog_cube = bpy.context.active_object

            for collection in fog_cube.users_collection:
                collection.objects.unlink(fog_cube)
            MIB_env_collection.objects.link(fog_cube)

            fog_cube.name = "Fog"
            #fog_cube.display_type = "BOUNDS"
            fog_cube.scale = (500, 500, 75)

            fog_material = bpy.data.materials.new(name="Fog")
            fog_material.use_nodes = True
            fog_cube.data.materials.append(fog_material)

            output_node = [node for node in fog_material.node_tree.nodes if node.type == "OUTPUT_MATERIAL"][0]
            fog_material.node_tree.nodes.remove(GetConnectedSocketTo(0, output_node).node)
            fog_node = create_node_group(fog_material, fog_node_tree_name, (output_node.location.x - 200, output_node.location.y))
            fog_material.node_tree.links.new(fog_node.outputs[0], output_node.inputs["Volume"])

            bpy.context.scene.eevee.volumetric_end = fog_node.inputs["Max Distance"].default_value + 400.0
    
            bpy.context.object["MiBlend ID"] = "Fog"

            bpy.ops.object.select_all(action='DESELECT')

        # Create Clouds
        if (scene.miblend_properties.env_properties.create_clouds and mode == None) or mode == "Clouds":
            if not os.path.exists(clouds_path):
                Call_AS("e03", traceback.format_exc(), f"Clouds Generator {clouds_file_comp()}")

            if clouds_node_tree_name not in bpy.data.node_groups:
                with bpy.data.libraries.load(clouds_path, link=False) as (data_from, data_to):
                    data_to.node_groups = [clouds_node_tree_name]
            else:
                bpy.data.node_groups[clouds_node_tree_name]
    
            if "Clouds" not in bpy.data.materials:
                with bpy.data.libraries.load(clouds_path, link=False) as (data_from, data_to):
                    data_to.materials = ["Clouds"]
            else:
                bpy.data.materials["Clouds"]

            if not MIB_env_collection:
                MIB_env_collection = bpy.data.collections.new("MiBlend Environment")
                bpy.context.scene.collection.children.link(MIB_env_collection)

            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_plane_add(size=1.0, enter_editmode=False, align='WORLD', location=(0, 0, 500))
            clouds_obj = bpy.context.active_object

            for collection in clouds_obj.users_collection:
                collection.objects.unlink(clouds_obj)
            MIB_env_collection.objects.link(clouds_obj)

            clouds_obj.name = "Clouds"
            clouds_obj.scale = (400, 400, 1)
            clouds_obj.data.materials.append(bpy.data.materials.get("Clouds"))
            geonodes_modifier = clouds_obj.modifiers.new('Clouds Generator', type='NODES')
            geonodes_modifier.node_group = bpy.data.node_groups.get(clouds_node_tree_name)

            clouds_obj["MiBlend ID"] = "Clouds"

            bpy.ops.object.select_all(action='DESELECT')

@ Perf_Time
def fix_materials():
    for selected_object in bpy.context.selected_objects:
        if not is_mesh(selected_object) and not is_code_ignored("w01") and bpy.context.preferences.addons[str(__package__).split(".")[0]].preferences.show_warnings:
            Call_AS("w01", data=selected_object)
            continue
        
        elif not is_mesh(selected_object):
            continue

        for slot, material in enumerate(selected_object.data.materials):
            if material is None or not material.use_nodes:
                continue

            image_texture_node = None
            PBSDF = None

            material.blend_method = 'HASHED'

            for node in material.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    image_texture_node = node
                    node.interpolation = "Closest"

                if node.type == "BSDF_PRINCIPLED":
                    PBSDF = node

            if image_texture_node and PBSDF:
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], PBSDF.inputs["Alpha"])

@ Perf_Time
def swap_textures(folder_path):
    def find_image(image_name, root_folder):
        for dirpath, _, files in os.walk(root_folder):
            for file in files:
                if file == image_name:
                    return os.path.join(dirpath, file)

                if file.endswith(('.zip', '.jar')):
                    archive_path = os.path.join(dirpath, file)
                    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                        file_list = zip_ref.namelist()
                        if image_name in file_list:
                            extract_path = os.path.join(main_directory, 'Resource Packs', os.path.splitext(file)[0])
                            extracted_file_path = zip_ref.extract(image_name, extract_path)
                            return extracted_file_path
                
                format_fixed = os.path.join(dirpath, "short_" + image_name)
                if os.path.isfile(format_fixed):
                    return format_fixed

                format_fixed = os.path.join(dirpath, image_name.replace("short_", ""))
                if os.path.isfile(format_fixed):
                    return format_fixed
            
        return None
    
    for selected_object in bpy.context.selected_objects:
        if not is_mesh(selected_object) and not is_code_ignored("w01") and bpy.context.preferences.addons[str(__package__).split(".")[0]].preferences.show_warnings:
            Call_AS("w01", selected_object)
            continue
        elif not is_mesh(selected_object):
            continue

        for slot, material in enumerate(selected_object.data.materials):
            if material is None or not material.use_nodes:
                continue

            for node in material.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image is not None:
                    new_image_path = find_image(node.image.name, folder_path)
                    if new_image_path is not None:
                        if node.image.name in bpy.data.images:
                            bpy.data.images.remove(bpy.data.images[node.image.name], do_unlink=True)

                        node.image = bpy.data.images.load(new_image_path)

# Set Procedural PBR
@ Perf_Time
def setproceduralpbr():
    Preferences = bpy.context.preferences.addons[str(__package__).split(".")[0]].preferences
        
    for selected_object in bpy.context.selected_objects:
        if not is_mesh(selected_object) and not is_code_ignored("w01") and Preferences.show_warnings:
            Call_AS("w01", data=selected_object)
            continue
        elif not is_mesh(selected_object):
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
            PProperties = bpy.context.scene.miblend_properties.ppbr_properties
            

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
                    if blender_version(">= 4.4.1"):
                        bump_node.inputs["Filter Width"].default_value = 1.0
                    
                    if blender_version(">= 4.5.0"):
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
                PBSDF.inputs[PBSDF_compability("Specular IOR Level")].default_value = PProperties.specular

            # Use SSS                            
            if PProperties.use_sss and (name_in(SSS_Materials, material.name)[0] or PProperties.sss_skip):
                PBSDF.subsurface_method = PProperties.sss_type

                if PProperties.connect_texture:
                    material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), PBSDF.inputs[PBSDF_compability('Subsurface Radius')])
                else:
                    RemoveLinksFrom(PBSDF.inputs[PBSDF_compability('Subsurface Radius')])

                if blender_version(">= 4.0.0"):
                    PBSDF.inputs["Subsurface Weight"].default_value = PProperties.sss_weight
                    PBSDF.inputs["Subsurface Scale"].default_value = PProperties.sss_scale
                else:
                    PBSDF.inputs["Subsurface"].default_value = PProperties.sss_weight

                PBSDF.inputs["Subsurface Radius"].default_value = (1,1,1)
            elif not PProperties.use_sss and PProperties.revert_sss:
                PBSDF.inputs[PBSDF_compability("Subsurface Weight")].default_value = 0

            # Use Translucency
            if PProperties.use_translucency and name_in(Translucent_Materials, material.name)[0]:
                PBSDF.inputs[PBSDF_compability("Transmission Weight")].default_value = PProperties.translucency
            elif not PProperties.use_translucency and PProperties.revert_translucency:
                PBSDF.inputs[PBSDF_compability("Transmission Weight")].default_value = 0

            # Make Metals                            
            if PProperties.make_metal and name_in(Metal, material.name)[0]:
                PBSDF.inputs["Metallic"].default_value = PProperties.metal_metallic
                PBSDF.inputs["Roughness"].default_value = PProperties.metal_roughness
                
            # Make Reflections                            
            if PProperties.make_reflections and name_in(Reflective, material.name)[0]:
                PBSDF.inputs["Roughness"].default_value = PProperties.reflections_roughness

            # Make Better Emission and Animate Textures
            if PProperties.procedural_emission_and_animation and base_color_connection and image and EmissionMode(PBSDF, image.name):
                is_valid, item = name_in(Emissive_Materials.keys(), material.name)

                if is_valid and PProperties.custom_peaa_config:
                    material_properties = Emissive_Materials[item]
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

                        if GetConnectedSocketTo(PBSDF_compability("Emission Color"), PBSDF) is None:
                            material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), PBSDF.inputs[PBSDF_compability("Emission Color")])
                        
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

                    if GetConnectedSocketTo(PBSDF_compability("Emission Color"), PBSDF) is None:
                        material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), PBSDF.inputs[PBSDF_compability("Emission Color")])
                    
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
                    pspecular_node.inputs["To Max"].default_value = PBSDF.inputs[PBSDF_compability("Specular IOR Level")].default_value
                    pspecular_node.inputs["To Min"].default_value = PBSDF.inputs[PBSDF_compability("Specular IOR Level")].default_value * PProperties.ps_dif
                    
                    material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), pspecular_node.inputs["Value"])
                    material.node_tree.links.new(pspecular_node.outputs[0], PBSDF.inputs[PBSDF_compability("Specular IOR Level")])
                    
                elif PProperties.ps_revert and pspecular_node is not None:
                    material.node_tree.nodes.remove(pspecular_node)
