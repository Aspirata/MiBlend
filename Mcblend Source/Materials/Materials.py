from ..Data import *
import re
from ..MCB_API import *

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

def EmissionMode(PBSDF, material):
        
        # LoL it works
        Preferences = bpy.context.preferences.addons[__package__.replace(".Materials", "")].preferences
                
        if Preferences.emissiondetection == 'Automatic & Manual' and (PBSDF.inputs["Emission Strength"].default_value != 0 or MaterialIn(Emissive_Materials, material)):
            return 1

        if Preferences.emissiondetection == 'Automatic' and PBSDF.inputs["Emission Strength"].default_value != 0:
            return 2
        
        if Preferences.emissiondetection == 'Manual' and MaterialIn(Emissive_Materials, material):
            return 3

def upgrade_materials():
    for selected_object in bpy.context.selected_objects:
        slot = 0
        if selected_object.material_slots:
            slot += 1
            for i, material in enumerate(selected_object.data.materials):
                if material is not None and material.use_nodes:
                    for original_material, upgraded_material in Upgrade_Materials_Array.items():
                        for material_part in material.name.lower().replace("-", ".").split("."):
                            if original_material == material_part:
                                if upgraded_material not in bpy.data.materials:
                                    try:
                                        with bpy.data.libraries.load(os.path.join(materials_folder, "Upgraded Materials.blend"), link=False) as (data_from, data_to):
                                            data_to.materials = [upgraded_material]
                                    except:
                                        Absolute_Solver('004', "Upgraded Materials", traceback.format_exc())

                                    appended_material = bpy.data.materials.get(upgraded_material)
                                    selected_object.data.materials[i] = appended_material
                                else:
                                    selected_object.data.materials[i] = bpy.data.materials[upgraded_material]
                else:
                    Absolute_Solver("m002", slot)
        else:
            Absolute_Solver("m003", selected_object)

# Fix World

def get_linked_nodes(node, input_name):
    linked_nodes = []
    if input_name in node.inputs and node.inputs[input_name].is_linked:
        for link in node.inputs[input_name].links:
            linked_nodes.append(link.from_node)
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

def fix_world():
    
    for selected_object in bpy.context.selected_objects:
        slot = 0
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                slot += 1
                if material is not None and material.use_nodes:
                    PBSDF = None
                    image_texture_node = None
                    lbcf_node = None
                    scene = bpy.context.scene
                    WProperties = scene.world_properties

                    if MaterialIn(Alpha_Blend_Materials, material) and WProperties.use_alpha_blend:
                        material.blend_method = 'BLEND'
                    else:
                        material.blend_method = 'HASHED'
                    
                    material.shadow_method = 'HASHED'

                    if WProperties.delete_useless_textures:
                        DeleteUselessTextures(material)

                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            node.interpolation = "Closest"

                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node
                            connected_nodes = traverse_nodes(node, "Base Color")
                            for n in connected_nodes:
                                if n.type == "TEX_IMAGE":
                                    image_texture_node = n
                        
                        if node.type == "GROUP":
                            if "Lazy Biome Color Fix" == node.node_tree.name:
                                lbcf_node = node
                                
                    if image_texture_node and PBSDF:
                        if GetConnectedSocketTo("Alpha", "BSDF_PRINCIPLED", material) == None:
                            material.node_tree.links.new(image_texture_node.outputs["Alpha"], PBSDF.inputs["Alpha"])
                        
                        # Emission
                        if EmissionMode(PBSDF, material):
                            if GetConnectedSocketTo(PBSDF_compability("Emission Color"), "BSDF_PRINCIPLED", material) == None:
                                material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), PBSDF.inputs[PBSDF_compability("Emission Color")])

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
                                            with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                                                data_to.node_groups = ["Backface Culling"]
                                        except:
                                            Absolute_Solver("004", "Materials", traceback.format_exc())
                                    
                                    bfc_node = material.node_tree.nodes.new(type='ShaderNodeGroup')
                                    bfc_node.node_tree = bpy.data.node_groups["Backface Culling"]
                                    bfc_node.location = (PBSDF.location.x - 170, PBSDF.location.y - 110)

                                if GetConnectedSocketTo("Alpha", PBSDF).node != bfc_node:
                                    material.node_tree.links.new(GetConnectedSocketTo("Alpha", PBSDF), bfc_node.inputs[0])
                                        
                                material.node_tree.links.new(bfc_node.outputs[0], PBSDF.inputs["Alpha"])
                        else:
                            if MaterialIn(Backface_Culling_Materials, material):
                                bfc_node = None

                                for node in material.node_tree.nodes:
                                    if node.type == "GROUP":
                                        if "Backface Culling" in node.node_tree.name:                                                                                              
                                            material.node_tree.links.new(GetConnectedSocketTo(0, node), PBSDF.inputs["Alpha"])
                                            material.node_tree.nodes.remove(node)

                                material.use_backface_culling = False
                        
                        if WProperties.lazy_biome_fix:
                            material_parts = image_texture_node.image.name.lower().replace("-", "_").split("_")
                        
                            if ("grass" in material_parts or "water" in material_parts or "leaves" in material_parts) and "side" not in material_parts:
                                if lbcf_node == None:
                                    if "Lazy Biome Color Fix" not in bpy.data.node_groups:
                                        try:
                                            with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                                                data_to.node_groups = ["Lazy Biome Color Fix"]
                                        except:
                                            Absolute_Solver("004", "Materials", traceback.format_exc())
                                    
                                    lbcf_node = material.node_tree.nodes.new(type='ShaderNodeGroup')
                                    lbcf_node.node_tree = bpy.data.node_groups["Lazy Biome Color Fix"]
                                    lbcf_node.location = (PBSDF.location.x - 170, PBSDF.location.y)

                                if GetConnectedSocketTo("Base Color", PBSDF).node != lbcf_node:
                                    material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), lbcf_node.inputs["Texture"])
                                        
                                material.node_tree.links.new(lbcf_node.outputs[0], PBSDF.inputs["Base Color"])

                                if "water" in material_parts:
                                    lbcf_node.inputs["Water"].default_value = True
                else:
                    Absolute_Solver("m002", slot)
        else:
            Absolute_Solver("m003", selected_object)

def create_env(self=None):

    def clouds_file_comp():
        if blender_version("4.x.x"):
            return "4.0"
        else:
            return "3.6"
        
    scene = bpy.context.scene
    world = scene.world
    clouds_exists = False
    sky_exists = False

    if any(obj.get("Mcblend ID") == "Clouds" for obj in scene.objects):
        clouds_exists = True

    if world != None and "Mcblend Sky" in bpy.data.node_groups:
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
                    with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                        data_to.worlds = [world_material_name]
                    appended_world_material = bpy.data.worlds.get(world_material_name)
                    bpy.context.scene.world = appended_world_material
                except:
                    Absolute_Solver('004', "Nodes", traceback.format_exc())

            elif self.create_sky == 'Create Sky' and world_material_name in bpy.data.worlds:
                bpy.context.scene.world = bpy.data.worlds.get(world_material_name)

            # Recreate Clouds
            if self.create_clouds == 'Recreate Clouds':
                for obj in scene.objects:
                    if obj.get("Mcblend ID") == "Clouds":
                        bpy.data.objects.remove(obj, do_unlink=True)

                if clouds_node_tree_name in bpy.data.node_groups:
                    bpy.data.node_groups.remove(bpy.data.node_groups.get(clouds_node_tree_name))

                if "Clouds" in bpy.data.materials:
                    bpy.data.materials.remove(bpy.data.materials.get("Clouds"))
                
                    try:
                        with bpy.data.libraries.load(os.path.join(main_directory, "Materials", f"Clouds Generator {clouds_file_comp()}.blend"), link=False) as (data_from, data_to):
                            data_to.node_groups = [clouds_node_tree_name]
                            data_to.materials = ["Clouds"]
                    except:
                        Absolute_Solver('004', f"Clouds Generator {clouds_file_comp()}", traceback.format_exc())

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
                
                if "Clouds" in bpy.data.materials:
                    bpy.data.materials["Clouds"]
                else:
                    Absolute_Solver("007", "Clouds Material")

                if any(obj.get("Mcblend ID") == "Clouds" for obj in scene.objects):
                    clouds_exists =True

                if clouds_node_tree_name in bpy.data.node_groups:
                    if clouds_exists == False:
                        bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
                        bpy.context.object.name = "Clouds"
                        bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
                        geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
                        geonodes_modifier.node_group = bpy.data.node_groups.get(clouds_node_tree_name)
                else:
                    Absolute_Solver("007", clouds_node_tree_name)

                    bpy.context.object["Mcblend ID"] = "Clouds"
        else:
            bpy.ops.special.recreate_env('INVOKE_DEFAULT')

    else:
        
        # Create Sky
        if scene.env_properties.create_sky:
            try:
                if world_material_name not in bpy.data.worlds:
                    with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                        data_to.worlds = [world_material_name]
                    appended_world_material = bpy.data.worlds.get(world_material_name)
                else:
                    appended_world_material = bpy.data.worlds[world_material_name]
                bpy.context.scene.world = appended_world_material
            except:
                Absolute_Solver("004", "Nodes", traceback.format_exc())

        for obj in scene.objects:
            if obj.get("Mcblend ID") == "Clouds":
                clouds_exists = True

        # Create Clouds
        if scene.env_properties.create_clouds and clouds_exists == False:
            try:
                if clouds_node_tree_name not in bpy.data.node_groups:
                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", f"Clouds Generator {clouds_file_comp()}.blend"), link=False) as (data_from, data_to):
                        data_to.node_groups = [clouds_node_tree_name]
                else:
                    bpy.data.node_groups[clouds_node_tree_name]
                
                if "Clouds" not in bpy.data.materials:
                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", f"Clouds Generator {clouds_file_comp()}.blend"), link=False) as (data_from, data_to):
                        data_to.materials = ["Clouds"]
                else:
                    bpy.data.materials["Clouds"]
            except:
                Absolute_Solver('004', f"Clouds Generator {clouds_file_comp()}", traceback.format_exc())

            bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
            bpy.context.object.name = "Clouds"
            bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
            geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
            geonodes_modifier.node_group = bpy.data.node_groups.get(clouds_node_tree_name)

            bpy.context.object["Mcblend ID"] = "Clouds"

    
def fix_materials():
    for selected_object in bpy.context.selected_objects:
        slot = 0
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                slot += 1
                if material is not None and material.use_nodes:
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
    resource_packs = get_resource_packs()
    r_props = bpy.context.scene.resource_properties

    def fast_find_image(textures_paths, texture_name):
        for texture_path in filter(None, textures_paths):
            dir_path = os.path.dirname(texture_path)
            predicted_texture = os.path.join(dir_path, texture_name)
            if os.path.isfile(predicted_texture):
                return predicted_texture
        return None
    
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
                        
                        elif "grass" in image_name:
                            if "short_" + image_name in file_list:
                                extract_path = os.path.join(main_directory, 'Resource Packs', os.path.splitext(file)[0])
                                extracted_file_path = zip_ref.extract("short_" + image_name, extract_path)
                                return extracted_file_path
                            
                            if  image_name.replace("short_", "") in file_list:
                                extract_path = os.path.join(main_directory, 'Resource Packs', os.path.splitext(file)[0])
                                extracted_file_path = zip_ref.extract(image_name.replace("short_", ""), extract_path)
                                return extracted_file_path
                
                if "grass" in image_name:
                    if os.path.isfile(format_fixed := os.path.join(dirpath, "short_" + image_name)):
                        return format_fixed

                    if os.path.isfile(format_fixed := os.path.join(dirpath, image_name.replace("short_", ""))):
                        return format_fixed
            
        return None

    def find_texture_users(texture):
        Texture_users = []
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for material in selected_object.data.materials:
                    if material and material.use_nodes:
                        for node in material.node_tree.nodes:
                            if node.type == 'TEX_IMAGE' and node.image == texture:
                                Texture_users.append(node)
        
        for group in bpy.data.node_groups:
            for node in group.nodes:
                if node.type == 'TEX_IMAGE' and node.image == texture:
                    Texture_users.append(node)
        
        return Texture_users

    def update_texture(new_image_path, image_texture, texture_node=None, colorspace=None):
        Users = None

        if image_texture in bpy.data.images:
            Users = find_texture_users(bpy.data.images[image_texture])
            if not r_props.ignore_dublicates:
                for texture in bpy.data.images:
                    if image_texture in texture.name:
                        parts = texture.name.split(".")
                        if len(parts) > 1 and parts[-1].isdigit() and texture.name.replace("." + str(parts[-1]), "") == image_texture:
                            Users.extend(find_texture_users(blender_texture := bpy.data.images.get(texture)))
                            bpy.data.images.remove(blender_texture)

            bpy.data.images.remove(bpy.data.images[image_texture], do_unlink=True)
        
        new_image_texture = os.path.basename(new_image_path)
        if texture_node != None:
            if not texture_node.image:
                if image_texture in bpy.data.images:
                    texture_node.image = bpy.data.images[new_image_texture]
                else:
                    texture_node.image = bpy.data.images.load(new_image_path)

        if Users != None:

            if new_image_texture in bpy.data.images:
                user_texture = bpy.data.images[new_image_texture]
            else:
                bpy.data.images.load(new_image_path)
                user_texture = bpy.data.images[new_image_texture]

            if colorspace != None:
                for user in Users:
                    user.image = user_texture
                    try:
                        user.image.colorspace_settings.name = colorspace
                    except:
                        Absolute_Solver("u006", colorspace)
            else:
                for user in Users:
                    user.image = user_texture

    def animate_texture(texture_node, new_image_texture_path, ITexture_Animator, Current_node_tree, image_path=None):
        Texture_Animator = None
        image_texture = bpy.data.images.get(os.path.basename(new_image_texture_path))

        for node in material.node_tree.nodes:
            if node.type == "GROUP":
                if "Texture Animator" in node.node_tree.name:
                    Texture_Animator = node

        if r_props.animate_textures:
            if int(image_texture.size[1] / image_texture.size[0]) != 1:
                animation_file = new_image_texture_path + ".mcmeta"
                if not os.path.isfile(animation_file) and image_path != None:
                    animation_file = image_path + re.sub(r'(_n|_s|_e)$', '', image_texture.name.replace('.png', '')) + ".png" + ".mcmeta"
                if os.path.isfile(animation_file):
                    with open(animation_file, 'r') as file:
                        data = json.load(file).get('animation', {})
                        if frametime := data.get('frametime') == None:
                            frametime = 20

                        if interpolate := data.get('interpolate') == None:
                            interpolate = False
                    
                    if interpolate == True and r_props.interpolate:
                        if Texture_Animator != None:
                            material.node_tree.nodes.remove(Texture_Animator)

                        if ITexture_Animator is None:

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

                            if texture_node != None:
                                for socket in GetConnectedSocketFrom("Color", texture_node):
                                    material.node_tree.links.new(ITexture_Animator.outputs["Color"], socket)
                            
                                for socket in GetConnectedSocketFrom("Alpha", texture_node):
                                    material.node_tree.links.new(ITexture_Animator.outputs["Alpha"], socket)

                                material.node_tree.nodes.remove(texture_node)
                        
                        ITexture_Animator.inputs["Frames"].default_value = int(image_texture.size[1] / image_texture.size[0])
                        ITexture_Animator.inputs["Only Fix UV"].default_value = False
                        ITexture_Animator.inputs["Frametime"].default_value = frametime
                        ITexture_Animator.inputs["Interpolate"].default_value = interpolate
                        ITexture_Animator.inputs["Only Fix UV"].default_value = r_props.only_fix_uv

                    else:
                        if ITexture_Animator is not None:
                           texture_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')
                           texture_node.location = ITexture_Animator.location
                           texture_node.image = image_texture
                           texture_node.interpolation = "Closest"

                           for socket in GetConnectedSocketFrom("Color", ITexture_Animator):
                                material.node_tree.links.new(texture_node.outputs["Color"], socket)
                            
                           for socket in GetConnectedSocketFrom("Alpha", ITexture_Animator):
                                material.node_tree.links.new(texture_node.outputs["Alpha"], socket)

                           material.node_tree.nodes.remove(ITexture_Animator)

                        if Texture_Animator is None:
                            if "Texture Animator" not in bpy.data.node_groups:
                                try:
                                    with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                                        data_to.node_groups = ["Texture Animator"]
                                except:
                                    Absolute_Solver("004", "Materials", traceback.format_exc())
                        
                            Texture_Animator = material.node_tree.nodes.new(type='ShaderNodeGroup')
                            Texture_Animator.node_tree = bpy.data.node_groups["Texture Animator"]
                            Texture_Animator.location = (texture_node.location.x - 200, texture_node.location.y - 60)

                        material.node_tree.links.new(Texture_Animator.outputs["Current Frame"], texture_node.inputs["Vector"])
                    
                        Texture_Animator.inputs["Frames"].default_value = int(image_texture.size[1] / image_texture.size[0])
                        Texture_Animator.inputs["Only Fix UV"].default_value = False
                        Texture_Animator.inputs["Frametime"].default_value = frametime
                        Texture_Animator.inputs["Interpolate"].default_value = interpolate
                        Texture_Animator.inputs["Only Fix UV"].default_value = r_props.only_fix_uv
        else:
            if ITexture_Animator is not None:
                texture_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')
                texture_node.location = ITexture_Animator.location
                texture_node.image = image_texture
                texture_node.interpolation = "Closest"

                for socket in GetConnectedSocketFrom("Color", ITexture_Animator):
                    material.node_tree.links.new(texture_node.outputs["Color"], socket)

                for socket in GetConnectedSocketFrom("Alpha", ITexture_Animator):
                    material.node_tree.links.new(texture_node.outputs["Alpha"], socket)

                material.node_tree.nodes.remove(ITexture_Animator)

            if Texture_Animator != None:
                material.node_tree.nodes.remove(Texture_Animator)

    def normal_texture_change(path, normal_texture_node, normal_map_node, PBSDF, image_texture_node, image_texture, new_image_path, image_path):
        NTexture_Animator = None
        Current_node_tree = None

        if normal_texture_node == None:
            normal_image_name = image_texture.replace(".png", "_n.png")
        else:
            normal_image_name = normal_texture_node.image.name

        if predicted_texture_path := fast_find_image([new_image_path], normal_image_name) == None:
            new_normal_image_path = find_image(normal_image_name, path)
        else:
            if r_props.use_i == False:
                new_normal_image_path = find_image(normal_image_name, path)
            else:
                new_normal_image_path = predicted_texture_path
            

        if new_normal_image_path != None:
            if normal_texture_node == None:
                normal_texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
                for node in material.node_tree.nodes:
                    if node.type == "GROUP":
                        if "Animated;" in node.node_tree.name:
                            if re.search(r'_n$', node.node_tree.name.replace(".png", "")):
                                NTexture_Animator = node
                            elif re.search(r'_s$', node.node_tree.name.replace(".png", "")):
                                STexture_Animator = node
                            elif re.search(r'_e$', node.node_tree.name.replace(".png", "")):
                                ETexture_Animator = node
                            else:
                                ITexture_Animator = node
                                image_texture = node.node_tree.name.replace("Animated; ", "") + ".png"
                            Current_node_tree = node.node_tree
                try:
                    normal_texture_node.location = (image_texture_node.location.x, image_texture_node.location.y - 562)
                except:
                    normal_texture_node.location = (ITexture_Animator.location.x, ITexture_Animator.location.y - 562)

                normal_texture_node.interpolation = "Closest"
            
            update_texture(new_normal_image_path, normal_image_name, normal_texture_node)
            
            try:
                normal_texture_node.image.colorspace_settings.name = "Non-Color"
            except:
                Absolute_Solver("u006", "Non-Color")

            if normal_map_node == None:
                normal_map_node = material.node_tree.nodes.new("ShaderNodeNormalMap")
                normal_map_node.location = (normal_texture_node.location.x + 280, normal_texture_node.location.y)
                material.node_tree.links.new(normal_texture_node.outputs["Color"], normal_map_node.inputs["Color"])
                material.node_tree.links.new(normal_map_node.outputs["Normal"], PBSDF.inputs["Normal"])
            
            animate_texture(normal_texture_node, new_normal_image_path, NTexture_Animator, Current_node_tree, image_path)
            return new_normal_image_path
        return False
    
    def specular_texture_change(path, specular_texture_node, LabPBR_s, new_normal_image_path, PBSDF, image_texture_node, image_texture, new_image_path, image_path):
        STexture_Animator = None
        Current_node_tree = None

        if specular_texture_node == None:
            specular_image_name = image_texture.replace(".png", "_s.png")
        else:
            specular_image_name = specular_texture_node.image.name

        if predicted_texture_path := fast_find_image([new_normal_image_path, new_image_path], specular_image_name) == None and len([pack for pack in get_resource_packs().values() if "PBR" in pack.get("type", "")]) > 1:
            new_specular_image_path = find_image(specular_image_name, path)
        else:
            if r_props.use_i == False or r_props.use_n == False:
                new_specular_image_path = find_image(specular_image_name, path)
            else:
                new_specular_image_path = predicted_texture_path

        if new_specular_image_path != None:
            if STexture_Animator == None:
                for node in material.node_tree.nodes:
                    if node.type == "GROUP":
                        if "Animated;" in node.node_tree.name:
                            if re.search(r'_n$', node.node_tree.name.replace(".png", "")):
                                NTexture_Animator = node
                            elif re.search(r'_s$', node.node_tree.name.replace(".png", "")):
                                STexture_Animator = node
                            elif re.search(r'_e$', node.node_tree.name.replace(".png", "")):
                                ETexture_Animator = node
                            else:
                                ITexture_Animator = node
                                image_texture = node.node_tree.name.replace("Animated; ", "") + ".png"
                            Current_node_tree = node.node_tree

            if specular_texture_node == None and STexture_Animator == None:
                specular_texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
                try:
                    specular_texture_node.location = (image_texture_node.location.x, image_texture_node.location.y - 280)
                except:
                    specular_texture_node.location = (ITexture_Animator.location.x, ITexture_Animator.location.y - 280)

                specular_texture_node.interpolation = "Closest"

            update_texture(new_specular_image_path, specular_image_name, specular_texture_node, "Non-Color")

            if LabPBR_s == None:
                if "LabPBR Specular" not in bpy.data.node_groups:
                    with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                        data_to.node_groups = ["LabPBR Specular"]

                LabPBR_s = material.node_tree.nodes.new("ShaderNodeGroup")
                LabPBR_s.node_tree = bpy.data.node_groups["LabPBR Specular"]
                LabPBR_s.location = (specular_texture_node.location.x + 280, specular_texture_node.location.y)

            if STexture_Animator == None:
                material.node_tree.links.new(specular_texture_node.outputs["Color"], LabPBR_s.inputs["Color"])
                material.node_tree.links.new(specular_texture_node.outputs["Alpha"], LabPBR_s.inputs["Alpha"])
            else:
                material.node_tree.links.new(STexture_Animator.outputs["Color"], LabPBR_s.inputs["Color"])
                material.node_tree.links.new(STexture_Animator.outputs["Alpha"], LabPBR_s.inputs["Alpha"])

            if r_props.roughness:
                material.node_tree.links.new(LabPBR_s.outputs["Roughness"], PBSDF.inputs["Roughness"])
            else:
                RemoveLinksFrom(LabPBR_s.outputs["Roughness"])

            if r_props.metallic:
                material.node_tree.links.new(LabPBR_s.outputs["Reflectance (Metallic)"], PBSDF.inputs["Metallic"])
            else:
                RemoveLinksFrom(LabPBR_s.outputs["Reflectance (Metallic)"])
            
            if r_props.specular:
                material.node_tree.links.new(LabPBR_s.outputs["Porosity (Specular)"], PBSDF.inputs["Specular IOR Level"])
            else:
                RemoveLinksFrom(LabPBR_s.outputs["Porosity (Specular)"])

            if r_props.sss:
                material.node_tree.links.new(LabPBR_s.outputs["SSS"], PBSDF.inputs[PBSDF_compability("Subsurface Weight")])

                PBSDF.inputs["Subsurface Radius"].default_value = (1,1,1)

                PBSDF.subsurface_method = 'BURLEY'
            else:
                RemoveLinksFrom(LabPBR_s.outputs["SSS"])

            if r_props.emission:
                try:
                    try:
                        material.node_tree.links.new(image_texture_node.outputs["Color"], PBSDF.inputs[PBSDF_compability("Emission Color")])
                    except:
                        material.node_tree.links.new(ITexture_Animator.outputs["Color"], PBSDF.inputs[PBSDF_compability("Emission Color")])
                except:
                    pass
            
                material.node_tree.links.new(LabPBR_s.outputs["Emission Strength"], PBSDF.inputs["Emission Strength"])
            else:
                RemoveLinksFrom(LabPBR_s.outputs["Emission Strength"])
                RemoveLinksFrom(PBSDF.inputs[PBSDF_compability("Emission Color")])

            animate_texture(specular_texture_node, new_specular_image_path, STexture_Animator, Current_node_tree, image_path)
            return new_specular_image_path
        return False
        
    def emission_texture_change(path, emission_texture_node, new_normal_image_path, new_specular_image_path, PBSDF, image_texture_node, image_texture, new_image_path, image_path):

        if emission_texture_node == None:
            emission_image_name = image_texture.replace(".png", "_e.png")
        else:
            emission_image_name = emission_texture_node.image.name

        if predicted_texture_path := fast_find_image([new_image_path, new_normal_image_path, new_specular_image_path], emission_image_name) == None and len([pack for pack in get_resource_packs().values() if "PBR" in pack.get("type", "")]) > 1:
            new_emission_image_path = find_image(emission_image_name, path)
        else:
            if r_props.use_i == False or r_props.use_n == False or r_props.use_s == False:
                new_emission_image_path = find_image(emission_image_name, path)
            else:
                new_emission_image_path = predicted_texture_path

        if new_emission_image_path != None:
            if emission_texture_node == None:
                emission_texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")

                if ETexture_Animator == None or ITexture_Animator == None:
                    for node in material.node_tree.nodes:
                        if node.type == "GROUP":
                            if "Animated;" in node.node_tree.name:
                                if re.search(r'_n$', node.node_tree.name.replace(".png", "")):
                                    NTexture_Animator = node
                                elif re.search(r'_s$', node.node_tree.name.replace(".png", "")):
                                    STexture_Animator = node
                                elif re.search(r'_e$', node.node_tree.name.replace(".png", "")):
                                    ETexture_Animator = node
                                else:
                                    ITexture_Animator = node
                                    image_texture = node.node_tree.name.replace("Animated; ", "") + ".png"
                                Current_node_tree = node.node_tree

                try:
                    emission_texture_node.location = (image_texture_node.location.x, image_texture_node.location.y - 850)
                except:
                    emission_texture_node.location = (ITexture_Animator.location.x, ITexture_Animator.location.y - 850)

                emission_texture_node.interpolation = "Closest"

            update_texture(new_emission_image_path, emission_image_name, emission_texture_node)

            material.node_tree.links.new(emission_texture_node.outputs["Color"], PBSDF.inputs[PBSDF_compability("Emission Color")])
            material.node_tree.links.new(emission_texture_node.outputs["Alpha"], PBSDF.inputs["Emission Strength"])

            animate_texture(emission_texture_node, new_emission_image_path, ETexture_Animator, Current_node_tree, image_path)
            return True
        return False

    for selected_object in bpy.context.selected_objects:
        slot = 0
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                slot += 1
                if material is not None and material.use_nodes:
                    PBSDF = None
                    image_texture_node = None
                    image_path = None
                    normal_texture_node = None
                    normal_map_node = None
                    specular_texture_node = None
                    emission_texture_node = None
                    LabPBR_s = None
                    image_texture = None
                    ITexture_Animator = None
                    NTexture_Animator = None
                    STexture_Animator = None
                    ETexture_Animator = None
                    Current_node_tree = None

                    new_image_path = None
                    new_normal_image_path = None
                    new_specular_image_path = None

                    for node in material.node_tree.nodes:

                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node
                        
                        if node.type == "GROUP":
                            if "Animated;" in node.node_tree.name:
                                if re.search(r'_n$', node.node_tree.name.replace(".png", "")):
                                    NTexture_Animator = node
                                elif re.search(r'_s$', node.node_tree.name.replace(".png", "")):
                                    STexture_Animator = node
                                elif re.search(r'_e$', node.node_tree.name.replace(".png", "")):
                                    ETexture_Animator = node
                                else:
                                    ITexture_Animator = node
                                    image_texture = node.node_tree.name.replace("Animated; ", "") + ".png"
                                Current_node_tree = node.node_tree
                            
                            if node.node_tree.name == "LabPBR Specular":
                                LabPBR_s = node

                        if node.type == "TEX_IMAGE" and node.image:

                            if node.type == "TEX_IMAGE" and node.image:
                                image_name = node.image.name.replace(".png", "")
                                if re.search(r'_n$', image_name):
                                    normal_texture_node = node
                                elif re.search(r'_s$', image_name):
                                    specular_texture_node = node
                                elif re.search(r'_e$', image_name):
                                    emission_texture_node = node
                                else:
                                    image_texture_node = node
                                    original_name = image_texture_node.image.name
                                    new_name = original_name.replace("_y", "")
                                    image_texture_node.image.name = new_name
                                    image_texture = image_texture_node.image.name

                        if node.type == "NORMAL_MAP":
                            normal_map_node = node

                    if image_texture != None:
                        
                        try:
                            relevant_node = image_texture_node or ITexture_Animator
                            if abs(relevant_node.location.x - PBSDF.location.x) < 500:
                                relevant_node.location.x = PBSDF.location.x - 500
                        except:
                            pass
                        
                        # Image Texture Update
                        if r_props.use_i and "MWO" not in image_texture:
                            for pack, pack_info in resource_packs.items():
                                path, Type, enabled = pack_info["path"], pack_info["type"], pack_info["enabled"]
                                if not enabled or "Texture" not in Type:
                                    continue
                                
                                
                                new_image_path = find_image(image_texture, path)

                                if new_image_path != None and os.path.isfile(new_image_path):
                                        
                                    update_texture(new_image_path, image_texture)
                                        
                                    animate_texture(image_texture_node, new_image_path, ITexture_Animator, Current_node_tree)
                                    image_path = path
                                    break

                        # Normal Texture Update
                        if r_props.use_n and r_props.use_additional_textures and "MWO" not in image_texture:
                            for pack, pack_info in resource_packs.items():
                                path, Type, enabled = pack_info["path"], pack_info["type"], pack_info["enabled"]
                                if not enabled or "PBR" not in Type:
                                    continue

                                if new_normal_image_path := normal_texture_change(path, normal_texture_node, normal_map_node, PBSDF, image_texture_node, image_texture, new_image_path, image_path):
                                    break
                        else:
                            if normal_texture_node is not None:
                                material.node_tree.nodes.remove(normal_texture_node)
                                normal_texture_node = None
                            
                            if normal_map_node is not None:
                                material.node_tree.nodes.remove(normal_map_node)
                                normal_map_node = None

                        # Specular Texture Update
                        if r_props.use_s and r_props.use_additional_textures and "MWO" not in image_texture:
                            for pack, pack_info in resource_packs.items():
                                path, Type, enabled = pack_info["path"], pack_info["type"], pack_info["enabled"]
                                if not enabled or "PBR" not in Type:
                                    continue

                                if new_specular_image_path := specular_texture_change(path, specular_texture_node, LabPBR_s, new_normal_image_path, PBSDF, image_texture_node, image_texture, new_image_path, image_path):
                                    break
                        
                        else:
                            if specular_texture_node is not None:
                                material.node_tree.nodes.remove(specular_texture_node)
                                specular_texture_node = None
                            
                            if LabPBR_s is not None:
                                material.node_tree.nodes.remove(LabPBR_s)
                                LabPBR_s = None
                        
                        # Emission Texture Update
                        if r_props.use_e and r_props.use_additional_textures and "MWO" not in image_texture:
                            for pack, pack_info in resource_packs.items():
                                path, Type, enabled = pack_info["path"], pack_info["type"], pack_info["enabled"]
                                if not enabled or "PBR" not in Type:
                                    continue

                                if emission_texture_found := emission_texture_change(path, emission_texture_node, new_normal_image_path, new_specular_image_path, PBSDF, image_texture_node, image_texture, new_image_path, image_path):
                                    break
                        elif emission_texture_node is not None:
                            material.node_tree.nodes.remove(emission_texture_node)
                            emission_texture_node = None

                else:
                    Absolute_Solver("m002", slot)
        else:
            Absolute_Solver("m003", selected_object)
        
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
        slot = 0
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                slot += 1
                if material is not None and material.use_nodes:
                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE" and node.image is not None:
                            new_image_path = find_image(node.image.name, folder_path)
                            if new_image_path != None:
                                if node.image.name in bpy.data.images:
                                    bpy.data.images.remove(bpy.data.images[node.image.name], do_unlink=True)

                                node.image = bpy.data.images.load(new_image_path)
                else:
                    Absolute_Solver("m002", slot)
        else:
            Absolute_Solver("m003", selected_object)

# Set Procedural PBR
        
def setproceduralpbr():

    for selected_object in bpy.context.selected_objects:
        slot = 0
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                slot += 1
                if material is not None and material.use_nodes:
                    PBSDF = None
                    bump_node = None
                    proughness_node = None
                    pspecular_node = None
                    PNormals = None
                    ITexture_Animator = None
                    Texture_Animator = None
                    image_difference_X = 1
                    image_difference_Y = 1
                    Current_node_tree = None
                    scene = bpy.context.scene
                    PProperties = scene.ppbr_properties

                    for node in material.node_tree.nodes:
                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node
                            connected_nodes = traverse_nodes(node, "Base Color")
                            for n in connected_nodes:
                                if n.type == "TEX_IMAGE":
                                    image = n.image

                        if node.type == "BUMP":
                            bump_node = node

                        if node.type == "GROUP":
                            if "PNormals" in node.node_tree.name:
                                PNormals = node
                                Current_node_tree = node.node_tree

                            if "Texture Animator" in node.node_tree.name:
                                Texture_Animator = node
                        
                        if node.type == "MAP_RANGE":
                            if "Procedural Roughness Node" in node.name:
                                proughness_node = node
                            
                            if "Procedural Specular Node" in node.name:
                                pspecular_node = node

                    if PBSDF is not None:
                        # Use Normals
                        if PProperties.use_normals:

                            if PProperties.normals_selector == 'Bump':
                                if PNormals is not None:
                                    material.node_tree.nodes.remove(PNormals)

                                if bump_node is None:
                                    bump_node = material.node_tree.nodes.new(type='ShaderNodeBump')
                                    bump_node.location = (PBSDF.location.x - 200, PBSDF.location.y - 100)
                                    material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), bump_node.inputs['Height'])
                                    material.node_tree.links.new(bump_node.outputs['Normal'], PBSDF.inputs['Normal'])
                                bump_node.inputs[0].default_value = PProperties.bump_strength
                            else:
                                if bump_node is not None:
                                    material.node_tree.nodes.remove(bump_node)
                                
                                if PNormals is None:
                                    if f"PNormals; {material.name}" in bpy.data.node_groups:
                                        Current_node_tree = bpy.data.node_groups[f"PNormals; {material.name}"]

                                        PNormals = material.node_tree.nodes.new(type='ShaderNodeGroup')
                                        PNormals.node_tree = Current_node_tree
                                        PNormals.location = (PBSDF.location.x - 200, PBSDF.location.y - 132)
                                    
                                    else:
                                        with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                                            data_to.node_groups = ["PNormals"]

                                        PNormals = material.node_tree.nodes.new(type='ShaderNodeGroup')

                                        bpy.data.node_groups[f"PNormals"].name = f"PNormals; {material.name}"
                                        PNormals.node_tree = bpy.data.node_groups[f"PNormals; {material.name}"]
                                        Current_node_tree = PNormals.node_tree
                                        PNormals.location = (PBSDF.location.x - 200, PBSDF.location.y - 132)

                                for node in material.node_tree.nodes:
                                    if node.type == "GROUP":
                                        if "Animated;" in node.node_tree.name:
                                            if node.node_tree.name.replace("Animated; ", "") == Current_node_tree.name.replace("PNormals; ", ""):
                                                ITexture_Animator = node
                                                image = bpy.data.images[node.node_tree.name.replace("Animated; ", "") + ".png"]

                                for node in Current_node_tree.nodes:
                                    if node.type == "TEX_IMAGE":
                                        node.image = image

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

                                if ITexture_Animator != None: 
                                    material.node_tree.links.new(ITexture_Animator.outputs['Current Frame'], PNormals.inputs['Vector'])
                                
                                if Texture_Animator != None: 
                                    material.node_tree.links.new(Texture_Animator.outputs['Current Frame'], PNormals.inputs['Vector'])

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
                        if PProperties.use_sss  == True:
                            if MaterialIn(SSS_Materials, material) or PProperties.sss_skip:
                                PBSDF.subsurface_method = PProperties.sss_type

                                if PProperties.connect_texture:
                                    if blender_version("4.x.x"):
                                        material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), PBSDF.inputs['Subsurface Radius'])
                                    else:
                                        material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), PBSDF.inputs['Subsurface Color'])
                                else:
                                    if blender_version("4.x.x"):
                                        RemoveLinksFrom(PBSDF.inputs["Subsurface Radius"])
                                    else:
                                        RemoveLinksFrom(PBSDF.inputs["Subsurface Color"])

                                
                                if blender_version("4.x.x"):
                                    PBSDF.inputs["Subsurface Weight"].default_value = PProperties.sss_weight
                                    PBSDF.inputs["Subsurface Scale"].default_value = PProperties.sss_scale
                                else:
                                    PBSDF.inputs["Subsurface"].default_value = PProperties.sss_weight

                                PBSDF.inputs["Subsurface Radius"].default_value = (1,1,1)
                        elif PProperties.revert_sss:
                            PBSDF.inputs[PBSDF_compability("Subsurface Weight")].default_value = 0

                        # Use Translucency
                        if MaterialIn(Translucent_Materials, material):
                            if PProperties.use_translucency == True:
                                    PBSDF.inputs[PBSDF_compability("Transmission Weight")].default_value = PProperties.translucency
                            elif PProperties.revert_translucency:
                                PBSDF.inputs[PBSDF_compability("Transmission Weight")].default_value = 0

                        # Make Metals                            
                        if PProperties.make_metal == True and MaterialIn(Metal, material):
                            PBSDF.inputs["Metallic"].default_value = PProperties.metal_metallic
                            PBSDF.inputs["Roughness"].default_value = PProperties.metal_roughness

                            
                        # Make Reflections                            
                        if PProperties.make_reflections == True and MaterialIn(Reflective, material):
                            PBSDF.inputs["Roughness"].default_value = PProperties.reflections_roughness


                        # Make Better Emission and Animate Textures
                        if (PProperties.make_better_emission == True or PProperties.animate_textures == True) and EmissionMode(PBSDF, material):
                            node_group = None

                            # The Main Thing

                            for node in material.node_tree.nodes:
                                if node.type == "GROUP":
                                    if BATGroup in node.node_tree.name:
                                        node_group = node
                                        break

                            # BATGroup Import if BATGroup isn't in File
                            if node_group == None:
                                if BATGroup not in bpy.data.node_groups:
                                    with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                                        data_to.node_groups = [BATGroup]

                                node_group = material.node_tree.nodes.new(type='ShaderNodeGroup')
                                node_group.node_tree = bpy.data.node_groups[BATGroup]

                            # Settings Set
                            if MaterialIn(Emissive_Materials, material):
                                for material_part in material.name.lower().replace("-", ".").split("."):
                                    for material_name, material_properties in Emissive_Materials.items():
                                        if material_name == material_part:
                                            for property_name, property_value in material_properties.items():
                                                node_group.inputs[property_name].default_value = property_value

                                            if "Middle Value" in material_properties and 11 in material_properties and 12 in material_properties and "Adder" in material_properties and "Divider" in material_properties:
                                                node_group.inputs["Animate Textures"].default_value = PProperties.animate_textures
                                            
                                            if "From Min" in material_properties and "From Max" in material_properties and "To Min" in material_properties and "To Max" in material_properties:
                                                node_group.inputs["Better Emission"].default_value = PProperties.make_better_emission
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
                            if GetConnectedSocketTo(PBSDF_compability("Emission Color"), "BSDF_PRINCIPLED", material) == None:
                                material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), PBSDF.inputs[PBSDF_compability("Emission Color")])
                            
                            try:
                                if emit_socket := GetConnectedSocketTo("Emission Strength", "BSDF_PRINCIPLED", material).node != node_group:
                                    material.node_tree.links.new(emit_socket, node_group.inputs["Multiply"])
                            except:
                                pass

                            node_group.location = (PBSDF.location.x - 200, PBSDF.location.y - 250)
                            material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), node_group.inputs["Emission Color"])
                            material.node_tree.links.new(node_group.outputs["Emission Strength"], PBSDF.inputs["Emission Strength"])

                        if PProperties.make_better_emission == False and PProperties.animate_textures == False:
                            node_group = None
                            for node in material.node_tree.nodes:
                                if node.type == "GROUP":
                                    if BATGroup in node.node_tree.name:
                                        node_group = node
                                        break
                            
                            if node_group != None:
                                if mult_socket := GetConnectedSocketTo("Multiply", node_group) != None:
                                    material.node_tree.links.new(mult_socket, PBSDF.inputs["Emission Strength"])
                                material.node_tree.nodes.remove(node_group)

                        if PProperties.proughness:
                            if proughness_node == None:
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

                        elif PProperties.pr_revert and proughness_node != None:
                            material.node_tree.nodes.remove(proughness_node)
                        
                        if PProperties.pspecular:
                            if pspecular_node == None:
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
                            
                        elif PProperties.ps_revert and pspecular_node != None:
                            material.node_tree.nodes.remove(pspecular_node)

                else:
                    Absolute_Solver("m002", slot)
                
        else:
            Absolute_Solver("m003", selected_object)
#
        
# TODO:
    # Upgrade World - Сделать так чтобы выбирались определённые фейсы у мира > они отделялись от него в отдельный объект > Как-то группировались > Производилась замена этих объектов на риги (Сундук)
    # Upgrade World - Сщединённое стекло: Импортировать текстуры соединённого > Выбираются фейсы с материалом стекла > Математически вычислить находятся ли стёкла рядом (if Glass.location.x + 1: поставить сообтветствующую текстуру стекла)