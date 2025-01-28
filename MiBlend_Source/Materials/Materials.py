from ..MIB_API import *
from ..Data import *
from ..Resource_Packs import *
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
        if not is_mesh(selected_object):
            Call_AS("w01", selected_object)
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

# Fix World

# Scan the material for image texture node duplicates > if nothing is connected to the vector input then delete and restore connections else don't touch
def DeleteUselessTextures(material):
    texture_nodes = [node for node in material.node_tree.nodes if node.type == "TEX_IMAGE"]
    image_to_nodes = {}

    for node in texture_nodes:
        image = node.image
        if image is not None:
            if image in image_to_nodes:
                image_to_nodes[image].append(node)
            else:
                image_to_nodes[image] = [node]
        else:
            material.node_tree.nodes.remove(node)

    def get_node_suffix_number(node_name):
        parts = node_name.split(".")
        if len(parts) > 1 and parts[-1].isdigit():
            return int(parts[-1])
        return 0

    for image, nodes in image_to_nodes.items():
        if len(nodes) > 1:
            nodes.sort(key=lambda node: ('.' in node.name, get_node_suffix_number(node.name)))
            
            node_to_keep = nodes[0]
            nodes_to_remove = nodes[1:]

            for node in nodes_to_remove:
                if any(input.links for input in node.inputs):
                    continue
                
                output_number = -1
                for output in node.outputs:
                    output_number += 1
                    for link in output.links:
                        material.node_tree.links.new(node_to_keep.outputs[output_number], link.to_socket)
                
                material.node_tree.nodes.remove(node)

def get_linked_nodes(node, input_name):
    linked_nodes = []
    if input_name in node.inputs and node.inputs[input_name].is_linked:
        for link in node.inputs[input_name].links:
            linked_nodes.append(link.from_node)
            linked_nodes.extend(get_all_linked_nodes(link.from_node))
    return linked_nodes

def get_all_linked_nodes(node):
    linked_nodes = []
    for input_name, input_socket in node.inputs.items():
        if input_socket.is_linked:
            for link in input_socket.links:
                linked_nodes.append(link.from_node)
                linked_nodes.extend(get_all_linked_nodes(link.from_node))
    return linked_nodes

def traverse_nodes(node, input_name, visited=None):
    if visited is None:
        visited = set()
    
    if node in visited:
        return visited
    
    visited.add(node)
    
    linked_nodes = get_linked_nodes(node, input_name)
    for linked_node in linked_nodes:
        traverse_nodes(linked_node, input_name, visited)
    
    return visited

@ Perf_Time
def fix_world():
    Preferences = bpy.context.preferences.addons[str(__package__).split(".")[0]].preferences
    WProperties = bpy.context.scene.miblend_properties.world_properties

    for selected_object in bpy.context.selected_objects:

        if not is_mesh(selected_object):
            Call_AS("w01", data=selected_object)
            continue

        if Preferences.dev_tools and Preferences.experimental_features and WProperties.remove_doubles:
            bpy.ops.object.editmode_toggle()
            
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.edge_split(type='VERT')
            bpy.ops.mesh.remove_doubles()

            bpy.ops.object.editmode_toggle()

        for slot, material in enumerate(selected_object.data.materials):
            if material is None or not material.use_nodes:
                continue

            dprint(f"Material: {material.name}", is_deep=True, zone="fw")

            PBSDF = None
            image_texture_node = None
            lbcf_node = None
            bfc_node = None
            Texture_Animator = None
            auvf_node = None
            scene = bpy.context.scene
            WProperties = scene.world_properties

            material.blend_method = 'HASHED'
            
            if blender_version("< 4.3.0"):
                material.shadow_method = 'HASHED'

            # Delete Useless Textres
            if WProperties.delete_useless_textures:
                DeleteUselessTextures(material)

            for node in material.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    if node.image.name.replace(".png", "").endswith("_y"):
                        node.image.name = node.image.name.replace(".png", "")[-2:].replace("_y", "")
                    elif node.image.name.replace(".png", "").endswith("_a"):
                        node.node_tree.nodes.remove(node)
                    node.interpolation = "Closest"

                if node.type == "BSDF_PRINCIPLED":
                    PBSDF = node
                    image_texture_node = detect_texture_node(PBSDF)
                    image = detect_image_texture(PBSDF)
                
                if node.type == "GROUP":
                    if "Backface Culling" in node.node_tree.name:
                        bfc_node = node
                    
                    elif "Lazy Biome Color Fix" == node.node_tree.name:
                        lbcf_node = node
                    
                    elif "Animated UV Fix" in node.node_tree.name:
                        auvf_node = node
                    
                    elif "Texture Animator" in node.node_tree.name or "Animated;" in node.node_tree.name:
                        Texture_Animator = node
                        
            if not image_texture_node or not PBSDF:
                continue

            if GetConnectedSocketTo("Alpha", PBSDF) is None:
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], PBSDF.inputs["Alpha"])
            
            # Emission
            if EmissionMode(PBSDF, image.name):
                if GetConnectedSocketTo(PBSDF_compability("Emission Color"), PBSDF) is None:
                    material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), PBSDF.inputs[PBSDF_compability("Emission Color")])

                if (EmissionMode(PBSDF, image.name) == 1 or EmissionMode(PBSDF, image.name) == 3) and PBSDF.inputs["Emission Strength"].default_value == 0:
                    PBSDF.inputs["Emission Strength"].default_value = 1

            # Backface Culling
            alpha_connection = GetConnectedSocketTo("Alpha", PBSDF)
            if WProperties.backface_culling and name_in(Backface_Culling_Materials, material.name)[0]:
                material.use_backface_culling = True

                if bfc_node is None:
                    bfc_node = create_node_group(material.node_tree.nodes, "Backface Culling", (PBSDF.location.x - 170, PBSDF.location.y - 110))

                if alpha_connection and alpha_connection.node != bfc_node:
                    material.node_tree.links.new(alpha_connection, bfc_node.inputs[0])
                        
                material.node_tree.links.new(bfc_node.outputs[0], PBSDF.inputs["Alpha"])
                    
            elif bfc_node:
                material.use_backface_culling = False
                material.node_tree.links.new(GetConnectedSocketTo(0, bfc_node), PBSDF.inputs["Alpha"])
                material.node_tree.nodes.remove(bfc_node)
            
            # Lazy Biome Color Fix
            base_color_connection = GetConnectedSocketTo("Base Color", PBSDF)
            if WProperties.lazy_biome_fix and is_gray(image.name):
                texture_parts = format_texture_name(image.name)

                if lbcf_node is None:
                    lbcf_node = create_node_group(material.node_tree.nodes, "Lazy Biome Color Fix", (PBSDF.location.x - 170, PBSDF.location.y - 20))

                if base_color_connection and base_color_connection.node != lbcf_node:
                    material.node_tree.links.new(base_color_connection, lbcf_node.inputs["Texture"])

                material.node_tree.links.new(lbcf_node.outputs[0], PBSDF.inputs["Base Color"])

                # Simple Biomes Support
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

                if "grass" in texture_parts:
                    lbcf_node.inputs["Mode"].default_value = 2

                elif "water" in texture_parts:
                    lbcf_node.inputs["Mode"].default_value = 3

                elif "redstone" in texture_parts:
                    lbcf_node.inputs["Mode"].default_value = 4
                
                lbcf_node.inputs["Grass Color"].default_value = tuple(Grass_Color.get(biome, lbcf_node.inputs["Grass Color"].default_value)[:3]) + (1.0,)
                lbcf_node.inputs["Foliage Color"].default_value = tuple(Foliage_Color.get(biome, lbcf_node.inputs["Foliage Color"].default_value)[:3]) + (1.0,)

            elif lbcf_node:
                material.node_tree.links.new(GetConnectedSocketTo(0, lbcf_node), PBSDF.inputs["Base Color"])
                material.node_tree.nodes.remove(lbcf_node)

            # Animated UV Fix
            if image_texture_node.type == "GROUP":
                continue
            else:
                vector_connection = GetConnectedSocketTo("Vector", image_texture_node)
            
            if image.size[0] == 0:
                continue
            
            if WProperties.animated_uv_fix and int(image.size[1] / image.size[0]) > 1:
                if Texture_Animator is not None:
                    material.node_tree.nodes.remove(Texture_Animator)

                if auvf_node is None:
                    auvf_node = create_node_group(material.node_tree.nodes, "Animated UV Fix", (image_texture_node.location.x - 200, image_texture_node.location.y - 220))

                if vector_connection and vector_connection.node != auvf_node:
                    material.node_tree.links.new(vector_connection, auvf_node.inputs["Vector"])

                auvf_node.inputs["Frames"].default_value = int(image.size[1] / image.size[0])
                material.node_tree.links.new(auvf_node.outputs["Fixed UV"], image_texture_node.inputs["Vector"])

            elif auvf_node:
                material.node_tree.nodes.remove(auvf_node)
            
            selected_object["MiBlend ID"] = "World"

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
                if blender_version("4.x.x"):
                    for socket in node.inputs:
                            try:
                                vec_counter = 0
                                for vec in socket.default_value:
                                    vec_counter += 1
                                    vec = group.interface.items_tree[socket.name].default_value[vec_counter]
                            except:
                                socket.default_value = group.interface.items_tree[socket.name].default_value
                    else:
                        try:
                            vec_counter = 0
                            for vec in socket.default_value:
                                vec_counter += 1
                                vec = group.inputs[socket.name].default_value[vec_counter]
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
        if blender_version("4.x.x"):
            return "4.0"
        else:
            return "3.6"
    
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
        if (scene.env_properties.create_sky and mode == None) or mode == "Sky":
            if os.path.exists(nodes_file):
                if world_material_name not in bpy.data.worlds:
                    with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                        data_to.worlds = [world_material_name]
                    appended_world_material = bpy.data.worlds.get(world_material_name)
                else:
                    appended_world_material = bpy.data.worlds[world_material_name]
                bpy.context.scene.world = appended_world_material
            else:
                Call_AS("e03", traceback.format_exc(), "Nodes.blend")

        # Create Fog
        if (scene.env_properties.create_fog and mode == None) or mode == "Fog":
    
            if not MIB_env_collection:
                MIB_env_collection = bpy.data.collections.new("MiBlend Environment")
                bpy.context.scene.collection.children.link(MIB_env_collection)

            bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 50))
            fog_cube = bpy.context.active_object

            MIB_env_collection.objects.link(fog_cube)
            bpy.context.scene.collection.objects.unlink(fog_cube)

            fog_cube.name = "Fog"
            #fog_cube.display_type = "BOUNDS"
            fog_cube.scale = (500, 500, 75)

            fog_material = bpy.data.materials.new(name="Fog")
            fog_material.use_nodes = True
            fog_cube.data.materials.append(fog_material)

            output_node = [node for node in fog_material.node_tree.nodes if node.type == "OUTPUT_MATERIAL"][0]
            fog_material.node_tree.nodes.remove(GetConnectedSocketTo(0, output_node).node)
            fog_node = create_node_group(fog_material.node_tree.nodes, fog_node_tree_name, (output_node.location.x - 200, output_node.location.y))
            fog_material.node_tree.links.new(fog_node.outputs[0], output_node.inputs["Volume"])

            bpy.context.scene.eevee.volumetric_end = fog_node.inputs["Max Distance"].default_value
    
            bpy.context.object["MiBlend ID"] = "Fog"

        # Create Clouds
        if (scene.env_properties.create_clouds and mode == None) or mode == "Clouds":
            if os.path.exists(clouds_path):
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
            else:
                Call_AS("e03", traceback.format_exc(), f"Clouds Generator {clouds_file_comp()}")


            if not MIB_env_collection:
                MIB_env_collection = bpy.data.collections.new("MiBlend Environment")
                bpy.context.scene.collection.children.link(MIB_env_collection)

            bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
            bpy.context.object.name = "Clouds"

            MIB_env_collection.objects.link(bpy.context.object)
            bpy.context.scene.collection.objects.unlink(bpy.context.object)

            bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
            geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
            geonodes_modifier.node_group = bpy.data.node_groups.get(clouds_node_tree_name)

            bpy.context.object["MiBlend ID"] = "Clouds"

@ Perf_Time
def fix_materials():
    for selected_object in bpy.context.selected_objects:
        if not is_mesh(selected_object):
            Call_AS("w01", data=selected_object)
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
        if not is_mesh(selected_object):
            Call_AS("w01", selected_object)
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
        if not is_mesh(selected_object):
            Call_AS("w01", data=selected_object)
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
            scene = bpy.context.scene
            PProperties = scene.ppbr_properties

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

                    elif "Better Animate Textures" in node.node_tree.name:
                        better_animate_node = node
                        break
                
                elif node.type == "MAP_RANGE":
                    if "Procedural Roughness Node" in node.name:
                        proughness_node = node
                    
                    elif "Procedural Specular Node" in node.name:
                        pspecular_node = node

            if not PBSDF:
                continue

            # Use Normals
            if image:
                if image_texture_node.type == "GROUP":
                    vector_connection = image_texture_node.outputs["Current Frame"]
                else:
                    vector_connection = GetConnectedSocketTo("Vector", image_texture_node)

                if PProperties.use_normals:

                    if PProperties.normals_selector == 'Bump':
                        if PNormals:
                            material.node_tree.nodes.remove(PNormals)

                        if bump_node is None:
                            bump_node = material.node_tree.nodes.new(type='ShaderNodeBump')
                            bump_node.location = (PBSDF.location.x - 180, PBSDF.location.y - 132)
                            material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), bump_node.inputs['Height'])
                            material.node_tree.links.new(bump_node.outputs['Normal'], PBSDF.inputs['Normal'])

                        bump_node.inputs[0].default_value = PProperties.bump_strength

                    else:
                        if bump_node:
                            material.node_tree.nodes.remove(bump_node)
                        
                        if PNormals is None:
                            PNormals = material.node_tree.nodes.new(type='ShaderNodeGroup')
                            group_name = f"PNormals; {material.name}"

                            if group_name in bpy.data.node_groups:
                                Current_node_tree = bpy.data.node_groups[group_name]
                            else:
                                with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                                    data_to.node_groups = ["PNormals"]
                                bpy.data.node_groups["PNormals"].name = group_name
                                Current_node_tree = bpy.data.node_groups[group_name]

                            PNormals.node_tree = Current_node_tree
                            PNormals.location = (PBSDF.location.x - 180, PBSDF.location.y - 132)

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
                    
                    if bump_node is not None:
                        material.node_tree.nodes.remove(bump_node)
                    
                    if PNormals is not None:
                        material.node_tree.nodes.remove(PNormals)

            # Change PBSDF Settings                                
            if PProperties.change_bsdf:
                PBSDF.inputs["Roughness"].default_value = PProperties.roughness
                PBSDF.inputs[PBSDF_compability("Specular IOR Level")].default_value = PProperties.specular

            # Use SSS                            
            if PProperties.use_sss:
                if name_in(SSS_Materials, material.name)[0] or PProperties.sss_skip:
                    PBSDF.subsurface_method = PProperties.sss_type

                    if PProperties.connect_texture:
                        material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), PBSDF.inputs[PBSDF_compability('Subsurface Radius')])
                    else:
                        RemoveLinksFrom(PBSDF.inputs[PBSDF_compability('Subsurface Radius')])

                    if blender_version("4.x.x"):
                        PBSDF.inputs["Subsurface Weight"].default_value = PProperties.sss_weight
                        PBSDF.inputs["Subsurface Scale"].default_value = PProperties.sss_scale
                    else:
                        PBSDF.inputs["Subsurface"].default_value = PProperties.sss_weight

                    PBSDF.inputs["Subsurface Radius"].default_value = (1,1,1)
            elif PProperties.revert_sss:
                PBSDF.inputs[PBSDF_compability("Subsurface Weight")].default_value = 0

            # Use Translucency
            if PProperties.use_translucency:
                    if name_in(Translucent_Materials, material.name)[0]:
                        PBSDF.inputs[PBSDF_compability("Transmission Weight")].default_value = PProperties.translucency
            elif PProperties.revert_translucency:
                PBSDF.inputs[PBSDF_compability("Transmission Weight")].default_value = 0

            # Make Metals                            
            if PProperties.make_metal and name_in(Metal, material.name)[0]:
                PBSDF.inputs["Metallic"].default_value = PProperties.metal_metallic
                PBSDF.inputs["Roughness"].default_value = PProperties.metal_roughness
                
            # Make Reflections                            
            if PProperties.make_reflections and name_in(Reflective, material.name)[0]:
                PBSDF.inputs["Roughness"].default_value = PProperties.reflections_roughness

            # Make Better Emission and Animate Textures
            if (PProperties.better_emission or PProperties.procedural_animation) and image and EmissionMode(PBSDF, image.name):
                is_valid, item = name_in(Emissive_Materials.keys(), material.name)

                if is_valid:
                    material_properties = Emissive_Materials[item]
                    if len(material_properties) >= 1:
                        if better_animate_node is None:
                            better_animate_node = create_node_group(material.node_tree.nodes, "Better Animate Texture", (PBSDF.location.x - 200, PBSDF.location.y - 265))

                        if PProperties.randomize and not any(mod for mod in selected_object.modifiers if mod.type == "NODES" and "Random Face Value" in mod.node_group.name):
                            with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                                data_to.node_groups = ["Random Face Value"]

                            selected_object.modifiers.new("Random Face Value", "NODES")
                            selected_object.modifiers["Random Face Value"].node_group = bpy.data.node_groups["Random Face Value"]

                        current_section = None
                        for input_socket in better_animate_node.inputs:
                            if input_socket.name in material_properties:
                                current_section = input_socket.name
                            elif current_section and current_section in material_properties:
                                if value := material_properties.get(current_section, {}).get(input_socket.name):
                                    input_socket.default_value = value

                        Better_Emission_Dict = material_properties.get("Better Emission", {})
                        if PProperties.better_emission and Better_Emission_Dict:
                            better_animate_node.inputs["Better Emission"].default_value = bool(PProperties.better_emission and material_properties.get("Better Emission", False))
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

            elif not PProperties.better_emission and not PProperties.procedural_animation and better_animate_node:
                mult_socket = GetConnectedSocketTo("Multiply", better_animate_node)
                if mult_socket:
                    material.node_tree.links.new(mult_socket, PBSDF.inputs["Emission Strength"])
                material.node_tree.nodes.remove(better_animate_node)

            if Preferences.dev_tools and Preferences.experimental_features:
                if PProperties.proughness:
                    if proughness_node is None:
                        proughness_node = material.node_tree.nodes.new(type='ShaderNodeMapRange')
                        proughness_node.name = "Procedural Roughness Node"
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
                        pspecular_node.name = "Procedural Specular Node"
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
