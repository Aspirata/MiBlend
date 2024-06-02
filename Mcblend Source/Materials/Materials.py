from ..Data import *

# This function checks if a given material's name contains any of the keywords in the provided array. 
# It returns True if a match is found, and False otherwise.

def MaterialIn(Array, material):
    for material_part in material.name.lower().replace("-", ".").split("."):
        try:
            for keyword, other in Array.items():
                if keyword == material_part:
                    return True
        except:
            for keyword in Array:
                if keyword in material_part:
                    return True
    return False

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

def EmissionMode(PBSDF, material):
                
        if bpy.context.scene.world_properties.emissiondetection == 'Automatic & Manual' and (PBSDF.inputs["Emission Strength"].default_value != 0 or MaterialIn(Emissive_Materials, material)):
            return 1

        if bpy.context.scene.world_properties.emissiondetection == 'Automatic' and PBSDF.inputs["Emission Strength"].default_value != 0:
            return 2
        
        if bpy.context.scene.world_properties.emissiondetection == 'Manual' and MaterialIn(Emissive_Materials, material):
            return 3

def upgrade_materials():
    for selected_object in bpy.context.selected_objects:
        slot = 0
        if selected_object.material_slots:
            slot += 1
            for i, material in enumerate(selected_object.data.materials):
                if material is not None:
                    for original_material, upgraded_material in Materials_Array.items():
                        for material_part in material.name.lower().replace("-", ".").split("."):
                            if original_material == material_part:
                                if upgraded_material not in bpy.data.materials:
                                    try:
                                        with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                                            data_to.materials = [upgraded_material]
                                    except:
                                        Absolute_Solver('004', "Materials", traceback.format_exc())

                                    appended_material = bpy.data.materials.get(upgraded_material)
                                    selected_object.data.materials[i] = appended_material
                                else:
                                    selected_object.data.materials[i] = bpy.data.materials[upgraded_material]

                                selected_object.data.update()
                else:
                    Absolute_Solver("m002", slot)
        else:
            Absolute_Solver("m003", selected_object)

# Fix World
                        
def fix_world():
    for selected_object in bpy.context.selected_objects:
        slot = 0
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                slot += 1
                if material is not None:
                    PBSDF = None
                    image_texture_node = None
                    scene = bpy.context.scene
                    WProperties = scene.world_properties

                    if MaterialIn(Alpha_Blend_Materials, material):
                        material.blend_method = 'BLEND'
                    else:
                        material.blend_method = 'HASHED'
                    
                    material.shadow_method = 'HASHED'

                    if WProperties.delete_useless_textures:
                        DeleteUselessTextures(material)

                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            image_texture_node = node
                            image_texture_node.interpolation = "Closest"

                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node
                                
                    if (image_texture_node and PBSDF) != None:
                        if GetConnectedSocketTo("Alpha", "BSDF_PRINCIPLED", material) == None:
                            material.node_tree.links.new(image_texture_node.outputs["Alpha"], PBSDF.inputs["Alpha"])
                        
                        # Emission
                        if EmissionMode(PBSDF, material):
                            if blender_version("4.x.x"):
                                if GetConnectedSocketTo("Emission Color", "BSDF_PRINCIPLED", material) == None:
                                    material.node_tree.links.new(image_texture_node.outputs["Color"], PBSDF.inputs["Emission Color"])
                            else:
                                if GetConnectedSocketTo("Emission", "BSDF_PRINCIPLED", material) == None:
                                    material.node_tree.links.new(image_texture_node.outputs["Color"], PBSDF.inputs["Emission"])

                            if (EmissionMode(PBSDF, material) == 1 or EmissionMode(PBSDF, material) == 3) and PBSDF.inputs["Emission Strength"].default_value == 0:
                                PBSDF.inputs["Emission Strength"].default_value = 1

                        # Backface Culling
                        if WProperties.backface_culling:
                            if MaterialIn(Backface_Culling_Materials, material):
                                bfc_node = None

                                material.use_backface_culling = True
                                
                                for node in material.node_tree.nodes:
                                    if node.type == "GROUP":
                                        if "Backface Culling" in node.node_tree.name:
                                            bfc_node = node
                                            break
                                
                                if bfc_node == None:
                                    if "Backface Culling" not in bpy.data.node_groups:
                                        try:
                                            with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                                                data_to.node_groups = ["Backface Culling"]
                                        except:
                                            Absolute_Solver("004", "Materials", traceback.format_exc())
                                    
                                    bfc_node = material.node_tree.nodes.new(type='ShaderNodeGroup')
                                    bfc_node.node_tree = bpy.data.node_groups["Backface Culling"]
                                    bfc_node.location = (PBSDF.location.x - 170, PBSDF.location.y - 110)

                                material.node_tree.links.new(image_texture_node.outputs[1], bfc_node.inputs[0])

                                for node in material.node_tree.nodes:
                                    if node.type == "BSDF_PRINCIPLED":
                                        for link in node.inputs["Alpha"].links:                                            
                                            if link.from_node.name != bfc_node.name:                                                
                                                for output in link.from_node.outputs:
                                                    for link_out in output.links:
                                                        if link_out.to_socket.node.name == node.name:                                                                                                                    
                                                            material.node_tree.links.new(link_out.from_socket, bfc_node.inputs[0]) 
                                                            break
                            
                                material.node_tree.links.new(bfc_node.outputs[0], PBSDF.inputs["Alpha"])
                        else:
                            if MaterialIn(Backface_Culling_Materials, material):
                                bfc_node = None

                                for node in material.node_tree.nodes:
                                    if node.type == "GROUP":
                                        if "Backface Culling" in node.node_tree.name:
                                            for link in node.inputs[0].links:     
                                                for output in link.from_node.outputs:
                                                    for link_out in output.links:
                                                        if link_out.to_socket.node.name == node.name:                                                                                                                    
                                                            material.node_tree.links.new(link_out.from_socket, PBSDF.inputs["Alpha"])
                                            material.node_tree.nodes.remove(node)

                                material.use_backface_culling = False

                        selected_object.data.update()
                else:
                    Absolute_Solver("m002", slot)
        else:
            Absolute_Solver("m003", selected_object)

def create_env(self=None):
    scene = bpy.context.scene
    world = scene.world
    clouds_exists = False
    sky_exists = False

    if (any(node.name == clouds_node_tree_name for node in bpy.data.node_groups)):
        clouds_exists = True

    if world != None and (any(node.name == "Mcblend Sky" for node in bpy.data.node_groups)):
        if world_material_name in bpy.data.worlds:
            sky_exists = True
    
    if clouds_exists == True or sky_exists == True:

        # Recreate Sky
        if self != None:

            if self.reset_settings == True:
                world_material = bpy.context.scene.world.node_tree
                group = bpy.data.node_groups["Mcblend Sky"]

                for node in world_material.nodes:
                    if node.type == 'GROUP':
                        if "Mcblend Sky" in node.node_tree.name:
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
                if world == bpy.data.worlds.get(world_material_name) and bpy.data.worlds.get(world_material_name) != None:
                    
                    bpy.data.worlds.remove(bpy.data.worlds.get(world_material_name), do_unlink=True)
                
                for group in bpy.data.node_groups:
                    if "Mcblend" in group.name:
                        bpy.data.node_groups.remove(group)

                try:
                    with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                        data_to.worlds = [world_material_name]
                    appended_world_material = bpy.data.worlds.get(world_material_name)
                    bpy.context.scene.world = appended_world_material
                except:
                    Absolute_Solver('004', "Materials", traceback.format_exc())

            if self.create_sky == 'Create Sky':

                if world_material_name in bpy.data.worlds:
                    bpy.context.scene.world = bpy.data.worlds.get(world_material_name)
                else:
                    print("World not found (Create Sky)")

            if self.create_clouds == 'Recreate Clouds':
                for obj in scene.objects:
                    if obj.get("Mcblend ID") == "Clouds":
                        bpy.data.objects.remove(obj, do_unlink=True)

                if clouds_node_tree_name in bpy.data.node_groups:
                    bpy.data.node_groups.remove(bpy.data.node_groups.get(clouds_node_tree_name))

                if "Clouds" in bpy.data.materials:
                    bpy.data.materials.remove(bpy.data.materials.get("Clouds"))
                
                if blender_version("4.x.x"):
                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator 4.0.blend"), link=False) as (data_from, data_to):
                        data_to.node_groups = [clouds_node_tree_name]

                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator 4.0.blend"), link=False) as (data_from, data_to):
                        data_to.materials = ["Clouds"]
                else:
                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator 3.6.blend"), link=False) as (data_from, data_to):
                        data_to.node_groups = [clouds_node_tree_name]

                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator 3.6.blend"), link=False) as (data_from, data_to):
                        data_to.materials = ["Clouds"]

                bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
                bpy.context.object.name = "Clouds"
                bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
                geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
                geonodes_modifier.node_group = bpy.data.node_groups.get(clouds_node_tree_name)

                bpy.context.object["Mcblend ID"] = "Clouds"
            
            clouds_exists = False
            
            if self.create_clouds == 'Create Clouds':

                if clouds_node_tree_name in bpy.data.node_groups:
                    bpy.data.node_groups[clouds_node_tree_name]
                else:
                    print("Clouds geometry nodes not found (Create Clouds)")
                
                if "Clouds" in bpy.data.materials:
                    bpy.data.materials["Clouds"]
                else:
                    print("Clouds material not found (Create Clouds)")

                for obj in scene.objects:
                    if obj.get("Mcblend ID") == "Clouds":
                        clouds_exists =True

                if clouds_exists == False:
                    bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
                    bpy.context.object.name = "Clouds"
                    bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
                    geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
                    geonodes_modifier.node_group = bpy.data.node_groups.get(clouds_node_tree_name)

                    bpy.context.object["Mcblend ID"] = "Clouds"
        else:
            bpy.ops.wm.recreate_env('INVOKE_DEFAULT')

    else:
        
        # Create Sky
        if scene.env_properties.create_sky:
            try:
                if world_material_name not in bpy.data.worlds:
                    with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                        data_to.worlds = [world_material_name]
                    appended_world_material = bpy.data.worlds.get(world_material_name)
                else:
                    appended_world_material = bpy.data.worlds[world_material_name]
                bpy.context.scene.world = appended_world_material
            except:
                Absolute_Solver("004", "Materials", traceback.format_exc())

        for obj in scene.objects:
            if obj.get("Mcblend ID") == "Clouds":
                clouds_exists = True

        if scene.env_properties.create_clouds and clouds_exists == False:               
            if blender_version("4.x.x"):     
                if clouds_node_tree_name not in bpy.data.node_groups:
                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator 4.0.blend"), link=False) as (data_from, data_to):
                        data_to.node_groups = [clouds_node_tree_name]
                else:
                    bpy.data.node_groups[clouds_node_tree_name]
                
                if "Clouds" not in bpy.data.materials:
                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator 4.0.blend"), link=False) as (data_from, data_to):
                        data_to.materials = ["Clouds"]
                else:
                    bpy.data.materials["Clouds"]
            else:
                if clouds_node_tree_name not in bpy.data.node_groups:
                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator 3.6.blend"), link=False) as (data_from, data_to):
                        data_to.node_groups = [clouds_node_tree_name]
                else:
                    bpy.data.node_groups[clouds_node_tree_name]
                
                if "Clouds" not in bpy.data.materials:
                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator 3.6.blend"), link=False) as (data_from, data_to):
                        data_to.materials = ["Clouds"]
                else:
                    bpy.data.materials["Clouds"]

            bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
            bpy.context.object.name = "Clouds"
            bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
            geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
            geonodes_modifier.node_group = bpy.data.node_groups.get(clouds_node_tree_name)

            bpy.context.object["Mcblend ID"] = "Clouds"
            

    bpy.context.view_layer.update()

    
def fix_materials():
    for selected_object in bpy.context.selected_objects:
        slot = 0
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                slot += 1
                if material is not None:
                    image_texture_node = None
                    PBSDF = None

                    material.blend_method = 'HASHED'
                    material.shadow_method = 'HASHED'

                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            image_texture_node = node
                            node.interpolation = "Closest"
                        
                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node

                    if (image_texture_node and PBSDF) != None:
                        material.node_tree.links.new(image_texture_node.outputs["Alpha"], PBSDF.inputs["Alpha"])
                else:
                    Absolute_Solver("m002", slot)
        else:
            Absolute_Solver("m003", selected_object)

def apply_resources():
    resource_packs = get_resource_packs(bpy.context.scene)
    r_props = bpy.context.scene.resource_properties

    for selected_object in bpy.context.selected_objects:
        slot = 0
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                slot += 1
                if material is not None:
                    PBSDF = None
                    image_texture_node = None
                    normal_texture_node = None
                    normal_map_node = None
                    specular_texture_node = None
                    emission_texture_node = None
                    separate_color_node = None
                    roughness_invert_color_node = None
                    emission_invert_color_node = None

                    new_image_path = None
                    new_normal_image_path = None
                    new_specular_image_path = None

                    for node in material.node_tree.nodes:

                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node

                        if node.type == "TEX_IMAGE" and node.image:

                            for part in node.image.name.replace(".png", "").split("_"):

                                if part == "n":
                                    normal_texture_node = node
                                    break
                                
                                if part == "s":
                                    specular_texture_node = node
                                    break

                                if part == "e":
                                    emission_texture_node = node
                                
                                if part != "s" and part != "n" and part != "e":
                                    image_texture_node = node
                        
                        if node.type == "NORMAL_MAP":
                            normal_map_node = node
                        
                        if node.type == "SEPARATE_COLOR":
                            separate_color_node = node
                        
                        if node.type == "INVERT":
                            if "Roughness Invert" in node.name:
                                roughness_invert_color_node = node
                            if "Emission Invert" in node.name:
                                emission_invert_color_node = node


                    # Texture Update
                    if image_texture_node != None:

                        if abs(image_texture_node.location.x - PBSDF.location.x) < 600:
                            image_texture_node.location.x = PBSDF.location.x - 600

                        for pack, pack_info in resource_packs.items():
                            path, enabled = pack_info["path"], pack_info["enabled"]
                            if not enabled:
                                continue

                            new_image_path = find_image(image_texture_node.image.name, path)
                            if new_image_path != None:
                                break
                        
                        if new_image_path != None:
                            if image_texture_node.image.name in bpy.data.images:
                                bpy.data.images.remove(bpy.data.images[image_texture_node.image.name], do_unlink=True)
                            image_texture_node.image = bpy.data.images.load(new_image_path)

                        # Normal Texture Update
                        if r_props.use_n:

                            if normal_texture_node == None:
                                normal_image_name = f"{image_texture_node.image.name.split('.png')[0]}_n.png"
                            else:
                                normal_image_name = normal_texture_node.image.name
                            
                            for pack, pack_info in resource_packs.items():
                                path, enabled = pack_info["path"], pack_info["enabled"]
                                if not enabled:
                                    continue
                                
                                new_normal_image_path = find_image(normal_image_name, path)
                                if new_normal_image_path != None:
                                    break

                            if new_normal_image_path != None:
                                if normal_texture_node == None:
                                    normal_texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
                                    normal_texture_node.location = (image_texture_node.location.x, image_texture_node.location.y - 562)
                                    normal_texture_node.interpolation = "Closest"
                                
                                if normal_image_name in bpy.data.images:
                                    bpy.data.images.remove(bpy.data.images[normal_image_name], do_unlink=True)
                                
                                normal_texture_node.image = bpy.data.images.load(new_normal_image_path)
                                
                                normal_texture_node.image.colorspace_settings.name = "Non-Color"

                                if normal_map_node == None:
                                    normal_map_node = material.node_tree.nodes.new("ShaderNodeNormalMap")
                                    normal_map_node.location = (normal_texture_node.location.x + 280, normal_texture_node.location.y)
                                    material.node_tree.links.new(normal_texture_node.outputs["Color"], normal_map_node.inputs["Color"])
                                    material.node_tree.links.new(normal_map_node.outputs["Normal"], PBSDF.inputs["Normal"])
                        
                        # Specular Texture Update
                        if r_props.use_s:

                            if specular_texture_node == None:
                                specular_image_name = f"{image_texture_node.image.name.split('.png')[0]}_s.png"
                            else:
                                specular_image_name = specular_texture_node.image.name
                            
                            for pack, pack_info in resource_packs.items():
                                path, enabled = pack_info["path"], pack_info["enabled"]
                                if not enabled:
                                    continue

                                new_specular_image_path = find_image(specular_image_name, path)
                                if new_specular_image_path != None:
                                    break

                            if new_specular_image_path != None:
                                if specular_texture_node == None:
                                    specular_texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
                                    specular_texture_node.location = (image_texture_node.location.x, image_texture_node.location.y - 280)
                                    specular_texture_node.interpolation = "Closest"

                                if separate_color_node == None:
                                    separate_color_node = material.node_tree.nodes.new("ShaderNodeSeparateColor")
                                    separate_color_node.location = (specular_texture_node.location.x + 260, specular_texture_node.location.y)
                                
                                if roughness_invert_color_node == None:
                                    roughness_invert_color_node = material.node_tree.nodes.new("ShaderNodeInvert")
                                    roughness_invert_color_node.location = (separate_color_node.location.x + 160, image_texture_node.location.y - 280)
                                    roughness_invert_color_node.name ="Roughness Invert"
                                
                                if emission_invert_color_node == None:
                                    emission_invert_color_node = material.node_tree.nodes.new("ShaderNodeInvert")
                                    emission_invert_color_node.location = (separate_color_node.location.x, separate_color_node.location.y - 140)
                                    emission_invert_color_node.name = "Emission Invert"
                                    
                                if specular_image_name in bpy.data.images:
                                    bpy.data.images.remove(bpy.data.images[specular_image_name], do_unlink=True)

                                specular_texture_node.image = bpy.data.images.load(new_specular_image_path)
                                
                                specular_texture_node.image.colorspace_settings.name = "Non-Color"

                                material.node_tree.links.new(specular_texture_node.outputs["Color"], separate_color_node.inputs[0])

                                material.node_tree.links.new(separate_color_node.outputs["Red"], roughness_invert_color_node.inputs["Color"])
                                material.node_tree.links.new(separate_color_node.outputs["Green"], PBSDF.inputs["Metallic"])
                                #material.node_tree.links.new(separate_color_node.outputs["Blue"], PBSDF.inputs["Emission Strength"])

                                material.node_tree.links.new(specular_texture_node.outputs["Alpha"], emission_invert_color_node.inputs["Color"])
                                if blender_version("4.x.x"):
                                    material.node_tree.links.new(image_texture_node.outputs["Color"], PBSDF.inputs["Emission Color"])
                                else:
                                    material.node_tree.links.new(image_texture_node.outputs["Color"], PBSDF.inputs["Emission"])
                                material.node_tree.links.new(emission_invert_color_node.outputs[0], PBSDF.inputs["Emission Strength"])

                                material.node_tree.links.new(roughness_invert_color_node.outputs[0], PBSDF.inputs["Roughness"])
                        
                        # Emission Texture Update
                        if r_props.use_e:

                            if emission_texture_node == None:
                                emission_image_name = f"{image_texture_node.image.name.split('.png')[0]}_e.png"
                            else:
                                emission_image_name = emission_texture_node.image.name
                            
                            for pack, pack_info in resource_packs.items():
                                path, enabled = pack_info["path"], pack_info["enabled"]
                                if not enabled:
                                    continue

                                new_emission_image_path = find_image(emission_image_name, path)
                                if new_emission_image_path != None:
                                    break

                            if new_emission_image_path != None:
                                if emission_texture_node == None:
                                    emission_texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
                                    emission_texture_node.location = (image_texture_node.location.x, image_texture_node.location.y - 760)
                                    emission_texture_node.interpolation = "Closest"
                                
                                if emission_image_name in bpy.data.images:
                                    bpy.data.images.remove(bpy.data.images[emission_image_name], do_unlink=True)

                                emission_texture_node.image = bpy.data.images.load(new_emission_image_path)


                                if blender_version("4.x.x"):
                                    material.node_tree.links.new(emission_texture_node.outputs["Color"], PBSDF.inputs["Emission Color"])
                                else:
                                    material.node_tree.links.new(emission_texture_node.outputs["Color"], PBSDF.inputs["Emission"])
                                material.node_tree.links.new(emission_texture_node.outputs["Color"], PBSDF.inputs["Emission Strength"])

                else:
                    Absolute_Solver("m002", slot)
        else:
            Absolute_Solver("m003", selected_object)
        
def swap_textures(folder_path):
    for selected_object in bpy.context.selected_objects:
        slot = 0
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                slot += 1
                if material is not None:
                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE" and node.image is not None:
                            new_image_path = find_image(node.image.name, folder_path)
                            if new_image_path != None:
                                if node.image.name in bpy.data.images:
                                    bpy.data.images.remove(bpy.data.images[node.image.name], do_unlink=True)
                                if os.path.isfile(new_image_path):
                                    node.image = bpy.data.images.load(new_image_path)
                            print(new_image_path)
                else:
                    Absolute_Solver("m002", slot)
        else:
            Absolute_Solver("m003", selected_object)

# Set Procedural PBR
        
def setproceduralpbr():
    for selected_object in bpy.context.selected_objects:
        counter = -1
        slot = 0
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                slot += 1
                if material is not None:
                    image_texture_node = None
                    PBSDF = None
                    bump_node = None
                    PNormals = None
                    image_difference_X = 1
                    image_difference_Y = 1
                    PNormals_exists = False
                    Current_node_tree = None
                    scene = bpy.context.scene
                    PProperties = scene.ppbr_properties

                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            if ".00" not in node.name:
                                image_texture_node = node

                        if node.type == "BUMP":
                            bump_node = node

                        if node.type == "GROUP":
                            if "PNormals" in node.node_tree.name:
                                PNormals = node
                                Current_node_tree = node.node_tree

                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node

                    if PBSDF is not None:
                        if image_texture_node is not None:
                            # Use Normals
                            if PProperties.use_normals:

                                if PProperties.normals_selector == 'Bump':
                                    if PNormals is not None:
                                        material.node_tree.nodes.remove(PNormals)

                                    if image_texture_node and bump_node is None:
                                        bump_node = material.node_tree.nodes.new(type='ShaderNodeBump')
                                        bump_node.location = (PBSDF.location.x - 200, PBSDF.location.y - 100)
                                        material.node_tree.links.new(image_texture_node.outputs["Color"], bump_node.inputs['Height'])
                                        material.node_tree.links.new(bump_node.outputs['Normal'], PBSDF.inputs['Normal'])
                                        bump_node.inputs[0].default_value = PProperties.bump_strength

                                    if bump_node is not None:
                                        bump_node.inputs[0].default_value = PProperties.bump_strength
                                else:
                                    if bump_node is not None:
                                        material.node_tree.nodes.remove(bump_node)
                                    
                                    if PNormals is None:
                                        if f"PNormals; {material.name}" in bpy.data.node_groups:
                                            PNormals_exists = True
                                            Current_node_tree = bpy.data.node_groups[f"PNormals; {material.name}"]
                                        
                                        if PNormals_exists == False:
                                            with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                                                data_to.node_groups = ["PNormals"]

                                            counter += 1

                                            PNormals = material.node_tree.nodes.new(type='ShaderNodeGroup')

                                            try:
                                                bpy.data.node_groups[f"PNormals.{counter}"].name = f"PNormals; {material.name}"
                                                PNormals.node_tree = bpy.data.node_groups[f"PNormals; {material.name}"]
                                                for node in PNormals.node_tree.nodes:
                                                    if node.type == "TEX_IMAGE":
                                                        node.image = image_texture_node.image
                                            except:
                                                bpy.data.node_groups[f"PNormals"].name = f"PNormals; {material.name}"
                                                PNormals.node_tree = bpy.data.node_groups[f"PNormals; {material.name}"]
                                                for node in PNormals.node_tree.nodes:
                                                    if node.type == "TEX_IMAGE":
                                                        node.image = image_texture_node.image

                                            PNormals.location = (PBSDF.location.x - 200, PBSDF.location.y - 132)

                                        else:
                                            PNormals = material.node_tree.nodes.new(type='ShaderNodeGroup')
                                            PNormals.node_tree = Current_node_tree
                                            PNormals.location = (PBSDF.location.x - 200, PBSDF.location.y - 132)
                                            for node in bpy.data.node_groups[Current_node_tree.name].nodes:
                                                if node.type == "TEX_IMAGE":
                                                    node.image = image_texture_node.image

                                    else:
                                        for node in bpy.data.node_groups[Current_node_tree.name].nodes:
                                            if node.type == "TEX_IMAGE":
                                                node.image = image_texture_node.image
                                    

                                    if image_texture_node.image.size[0] > image_texture_node.image.size[1]:
                                        image_difference_X = image_texture_node.image.size[1] / image_texture_node.image.size[0]

                                    if image_texture_node.image.size[0] < image_texture_node.image.size[1]:
                                        image_difference_Y = image_texture_node.image.size[0] / image_texture_node.image.size[1]

                                    PNormals.inputs["Size"].default_value = PProperties.pnormals_size
                                    PNormals.inputs["Blur"].default_value = PProperties.pnormals_blur
                                    PNormals.inputs["Strength"].default_value = PProperties.pnormals_strength
                                    PNormals.inputs["Exclude"].default_value = PProperties.pnormals_exclude
                                    PNormals.inputs["Min"].default_value = PProperties.pnormals_min
                                    PNormals.inputs["Max"].default_value = PProperties.pnormals_max
                                    PNormals.inputs["Size X Multiplier"].default_value = PProperties.pnormals_size_x_multiplier * image_difference_X
                                    PNormals.inputs["Size Y Multiplier"].default_value = PProperties.pnormals_size_y_multiplier * image_difference_Y

                                    material.node_tree.links.new(PNormals.outputs['Normal'], PBSDF.inputs['Normal'])
                            else:
                                
                                if bump_node is not None:
                                    material.node_tree.nodes.remove(bump_node)
                                
                                if PNormals is not None:
                                    material.node_tree.nodes.remove(PNormals)

                                
                        # Change PBSDF Settings                                
                        if PProperties.change_bsdf:
                            PBSDF.inputs["Roughness"].default_value = PProperties.roughness
                            if blender_version("4.x.x"):
                                PBSDF.inputs["Specular IOR Level"].default_value = PProperties.specular
                            else:
                                PBSDF.inputs["Specular"].default_value = PProperties.specular


                        # Use SSS                            
                        if PProperties.use_sss  == True:
                            if MaterialIn(SSS_Materials, material) or PProperties.sss_skip:
                                PBSDF.subsurface_method = PProperties.sss_type

                                if PProperties.connect_texture:
                                    for node in material.node_tree.nodes:
                                        if node.type == "BSDF_PRINCIPLED":
                                            for link in node.inputs[0].links:
                                                if blender_version("4.x.x"):
                                                    material.node_tree.links.new(link.from_socket, PBSDF.inputs['Subsurface Radius'])
                                                else:
                                                    material.node_tree.links.new(link.from_socket, PBSDF.inputs['Subsurface Color'])
                                else:
                                    for link in material.node_tree.links:
                                        if blender_version("4.x.x"):
                                            if link.to_socket == PBSDF.inputs["Subsurface Radius"]:
                                                material.node_tree.links.remove(link)
                                        else:
                                            if link.to_socket == PBSDF.inputs["Subsurface Color"]:
                                                material.node_tree.links.remove(link)

                                
                                if blender_version("4.x.x"):
                                    PBSDF.inputs["Subsurface Weight"].default_value = PProperties.sss_weight
                                    PBSDF.inputs["Subsurface Scale"].default_value = PProperties.sss_scale
                                else:
                                    PBSDF.inputs["Subsurface"].default_value = PProperties.sss_weight

                                PBSDF.inputs["Subsurface Radius"].default_value[0] = 1.0
                                PBSDF.inputs["Subsurface Radius"].default_value[1] = 1.0
                                PBSDF.inputs["Subsurface Radius"].default_value[2] = 1.0
                        else:
                            if blender_version("4.x.x"):
                                PBSDF.inputs["Subsurface Weight"].default_value = 0
                            else:
                                PBSDF.inputs["Subsurface"].default_value = 0


                        # Make Metals                            
                        if PProperties.make_metal == True and MaterialIn(Metal, material):
                            PBSDF.inputs["Metallic"].default_value = PProperties.metal_metallic
                            PBSDF.inputs["Roughness"].default_value = PProperties.metal_roughness

                            
                        # Make Reflections                            
                        if PProperties.make_reflections == True and MaterialIn(Reflective, material):
                            PBSDF.inputs["Roughness"].default_value = PProperties.reflections_roughness


                        # Make Better Emission and Animate Textures
                        if (PProperties.make_better_emission == True or PProperties.animate_textures == True) and EmissionMode(PBSDF, material):
                            image_texture_node = None
                            node_group = None
                            
                            # Texture Check
                            for node in material.node_tree.nodes:
                                if node.type == "TEX_IMAGE":
                                    if ".00" not in node.name:
                                        image_texture_node = node

                            # The Main Thing
                            if image_texture_node != None:

                                for node in material.node_tree.nodes:
                                    if node.type == "GROUP":
                                        if BATGroup in node.node_tree.name:
                                            node_group = node
                                            break

                                # BATGroup Import if BATGroup isn't in File
                                if node_group == None:
                                    if BATGroup not in bpy.data.node_groups:
                                        with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                                            data_to.node_groups = [BATGroup]

                                    node_group = material.node_tree.nodes.new(type='ShaderNodeGroup')
                                    node_group.node_tree = bpy.data.node_groups[BATGroup]

                                # Settings Set
                                if MaterialIn(Emissive_Materials, material) == True:
                                    for material_part in material.name.lower().replace("-", ".").split("."):
                                        for material_name, material_properties in Emissive_Materials.items():
                                            if material_name == material_part:
                                                for property_name, property_value in material_properties.items():
                                                    if property_name == "Divider":
                                                        node_group.inputs[property_name].default_value = property_value * bpy.context.scene.render.fps/30
                                                    else:
                                                        node_group.inputs[property_name].default_value = property_value

                                                node_group.inputs["Better Emission"].default_value = PProperties.make_better_emission

                                                if "Middle Value" in material_properties and 11 in material_properties and 12 in material_properties and "Adder" in material_properties and "Divider" in material_properties:
                                                    node_group.inputs["Animate Textures"].default_value = PProperties.animate_textures
                                else:
                                    for material_name, material_properties in Emissive_Materials.items():
                                        if material_name == "Default":
                                            for property_name, property_value in material_properties.items():
                                                if property_name == "Divider":
                                                    node_group.inputs[property_name].default_value = property_value * bpy.context.scene.render.fps/30
                                                else:
                                                    node_group.inputs[property_name].default_value = property_value

                                            node_group.inputs["Better Emission"].default_value = PProperties.make_better_emission
                                            node_group.inputs["Animate Textures"].default_value = PProperties.animate_textures
                                
                                # Color Connection if Nothing Connected
                                if blender_version("4.x.x"):
                                    if GetConnectedSocketTo("Emission Color", "BSDF_PRINCIPLED", material) == None:
                                        material.node_tree.links.new(image_texture_node.outputs[0], PBSDF.inputs["Emission Color"])
                                else:
                                    if GetConnectedSocketTo("Emission", "BSDF_PRINCIPLED", material) == None:
                                        material.node_tree.links.new(image_texture_node.outputs[0], PBSDF.inputs["Emission"])
                                
                                try:
                                    if GetConnectedSocketTo("Emission Strength", "BSDF_PRINCIPLED", material).node != node_group:
                                        material.node_tree.links.new(GetConnectedSocketTo("Emission Strength", "BSDF_PRINCIPLED", material), node_group.inputs["Multiply"])
                                except:
                                    pass

                                node_group.location = (PBSDF.location.x - 200, PBSDF.location.y - 250)
                                if blender_version("4.x.x"):
                                    material.node_tree.links.new(image_texture_node.outputs[0], node_group.inputs["Emission Color"])
                                else:
                                    material.node_tree.links.new(image_texture_node.outputs[0], node_group.inputs["Emission Color"])
                                material.node_tree.links.new(node_group.outputs["Emission Strength"], PBSDF.inputs["Emission Strength"])

                        if PProperties.make_better_emission == False and PProperties.animate_textures == False:
                            for node in material.node_tree.nodes:
                                if node.type == 'GROUP':
                                    if BATGroup in node.node_tree.name:
                                        material.node_tree.nodes.remove(node)
                else:
                    Absolute_Solver("m002", slot)
                
        else:
            Absolute_Solver("m003", selected_object)
            
        selected_object.data.update()
#
        
# TODO:
    # Upgrade World - Сделать так чтобы выбирались определённые фейсы у мира > они отделялись от него в отдельный объект > Как-то группировались > Производилась замена этих объектов на риги (Сундук)
    # Texture logic - Сделать использование текстур из папки, например из папки tex или из папки майнкрафта
    # Upgrade World - Сщединённое стекло: Импортировать текстуры соединённого > Выбираются фейсы с материалом стекла > Математически вычислить находятся ли стёкла рядом (if Glass.location.x + 1: поставить сообтветствующую текстуру стекла)