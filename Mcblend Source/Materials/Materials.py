from ..Data import *

#Replace Materials

# This function checks if a given material's name contains any of the keywords in the provided array. 
# It returns True if a match is found, and False otherwise.

def MaterialIn(Array, material):
    for keyword in Array:
        if keyword in material.name.lower():
            return True

# This function checks if there is a connection between two nodes in a material's node tree based on the specified criteria. 
# It returns True if a connection is found, and False otherwise.
        
def IsConnectedTo(NodeFromName, NodeFromType, NodeToName, NodeToType, index, nodeTo=None):
    if nodeTo is None:
        for selected_object in bpy.context.selected_objects:
            if selected_object.material_slots:
                for material in selected_object.data.materials:
                    if material is not None:                       # Materials Check
                        for Node in material.node_tree.nodes:      # Every Node in Material Check
                            if NodeToName is not None:
                                if NodeToName in Node.name:
                            
                                    if NodeFromName is not None and NodeFromType is None:
                                        for link in Node.inputs[index].links:
                                            if NodeFromName in link.from_node.name:
                                                return True
                                    
                                    if NodeFromType is not None and NodeFromName is None:
                                        if NodeFromType == link.from_node.type:

                                                return True
                                        
                                    if NodeFromName is not None and NodeFromType is not None:
                                        if NodeFromName in link.from_node.name and NodeFromType == link.from_node.type:
                                                return True
                                            
                            if NodeToType is not None:
                                if NodeToType == Node.type:
                                    if NodeFromName is not None and NodeFromType is None:
                                        for link in Node.inputs[index].links:
                                            if NodeFromName in link.from_node.name:
                                                    return True
                                    
                                    if NodeFromType is not None and NodeFromName is None:
                                        if NodeFromType == link.from_node.type:
                                                return True
                                        
                                    if NodeFromName is not None and NodeFromType is not None:
                                        if NodeFromName in link.from_node.name and NodeFromType == link.from_node.type:
                                                return True

                            if NodeToName is not None and NodeToType is not None:
                                if NodeToName == Node.name and NodeToType == Node.type:
                                    if NodeFromName is not None and NodeFromType is None:
                                        for link in Node.inputs[index].links:
                                            if NodeFromName in link.from_node.name:
                                                    return True
                                    
                                    if NodeFromType is not None and NodeFromName is None:
                                        if NodeFromType == link.from_node.type:
                                                return True
                                        
                                    if NodeFromName is not None and NodeFromType is not None:
                                        if NodeFromName in link.from_node.name and NodeFromType == link.from_node.type:
                                                return True

    else:
        for selected_object in bpy.context.selected_objects:
            if selected_object.material_slots:
                for material in selected_object.data.materials:
                    if material is not None:

                        for link in nodeTo.inputs[index].links:
                            if NodeFromName is None and NodeFromType is None:
                                    return True

                            else:
                                if NodeFromName is not None and NodeFromType is None:
                                    if NodeFromName in link.from_node.name:
                                        return True

                                if NodeFromType is not None and NodeFromName is None:
                                    if NodeFromType == link.from_node.type:
                                        return True

                                if NodeFromName is not None and NodeFromType is not None:
                                    if NodeFromName in link.from_node.name and NodeFromType == link.from_node.type:
                                        return True

# This function appends a material from an external .blend file to the current Blender scene 
# and assigns it to a specific face of a 3D object.
                                    
def append_materials(upgraded_material_name, selected_object, i):
    if upgraded_material_name not in bpy.data.materials:
        try:
            with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                data_to.materials = [upgraded_material_name]
        except:
            CEH('004')
        appended_material = bpy.data.materials.get(upgraded_material_name)
        selected_object.data.materials[i] = appended_material
    else:
        selected_object.data.materials[i] = bpy.data.materials[upgraded_material_name]

def EmissionMode(PBSDF, material):
    for material_name, properties in Emissive_Materials.items():
        for property_name, property_value in properties.items():
            if property_name == "Exclude":
                if property_value != "None":
                    for Excluder in property_value.split(", "):
                        if material_name in material.name.lower():
                            if Excluder not in material.name.lower():
                                Excluded = False
                            else:
                                Excluded = True
                                break
                else:
                    Excluded = False

                if bpy.context.scene.world_properties.emissiondetection == 'Automatic & Manual' and ((material_name in material.name.lower() and Excluded == False) or PBSDF.inputs[27].default_value != 0):
                    return 1

                if bpy.context.scene.world_properties.emissiondetection == 'Automatic' and PBSDF.inputs[27].default_value != 0:
                    return 2

                if bpy.context.scene.world_properties.emissiondetection == 'Manual' and (material_name in material.name.lower() and Excluded == False):
                    return 3

def upgrade_materials():
    for selected_object in bpy.context.selected_objects:
        if selected_object.material_slots:
            for i, material in enumerate(selected_object.data.materials):
                if i != None:
                    replace = False
                    for material_name, material_info in Materials_Array.items():
                        for property_name, property_value in material_info.items():
                            if property_name == "Upgraded Material":
                                upgraded_material = property_value

                            if property_name == "Original Material":
                                original_material = property_value

                            if original_material in material.name.lower():
                                if property_name == "Exclude" and property_value != "None":
                                    for excluder in property_value.split(", "):
                                        if original_material in material.name.lower() and excluder not in material.name.lower():
                                            replace = True
                                            r_upgraded_material = upgraded_material
                                                
                                        if original_material in material.name.lower() and excluder in material.name.lower():
                                            replace = False
                                            break
                                    
                    if replace == True:
                        append_materials(r_upgraded_material, selected_object, i)
                        selected_object.data.update()
            else:
                CEH('m002')
        else:
            CEH('m003', Data=selected_object)

# Fix World
                        
def fix_world():
    for selected_object in bpy.context.selected_objects:
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                if material != None:
                    PBSDF = None
                    image_texture_node = None
                    scene = bpy.context.scene
                    WProperties = scene.world_properties

                    if MaterialIn(Alpha_Blend_Materials, material):
                        material.blend_method = 'BLEND'
                    else:
                        material.blend_method = 'HASHED'

                    for node in material.node_tree.nodes:
                        if WProperties.delete_useless_textures:
                            if node.type == "TEX_IMAGE" and ".00" in node.name:
                                material.node_tree.nodes.remove(node)

                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            if ".00" not in node.name:
                                image_texture_node = node
                            image_texture_node.interpolation = "Closest"

                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node
                                
                    if (image_texture_node and PBSDF) != None:
                        material.node_tree.links.new(image_texture_node.outputs["Alpha"], PBSDF.inputs[4])
                        
                        # Emission
                        if EmissionMode(PBSDF, material) == 1 or EmissionMode(PBSDF, material) == 3:
                            material.node_tree.links.new(image_texture_node.outputs["Color"], PBSDF.inputs[26])
                            PBSDF.inputs[27].default_value = 1

                        if EmissionMode(PBSDF, material) == 2:
                            material.node_tree.links.new(image_texture_node.outputs["Color"], PBSDF.inputs[26])

                        # Backface Culling
                        if WProperties.backface_culling:
                            if MaterialIn(Backface_Culling_Materials, material):
                                bfc_node = None

                                material.use_backface_culling = True
                                
                                for node in material.node_tree.nodes:
                                    if node.type == "GROUP":
                                        if "Backface Culling" in node.node_tree.name:
                                            bfc_node = node
                                
                                if bfc_node == None:
                                    if "Backface Culling" not in bpy.data.node_groups:
                                        try:
                                            with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                                                data_to.node_groups = ["Backface Culling"]
                                        except:
                                            CEH("004")
                                    
                                    bfc_node = material.node_tree.nodes.new(type='ShaderNodeGroup')
                                    bfc_node.node_tree = bpy.data.node_groups["Backface Culling"]
                                    bfc_node.location = (PBSDF.location.x - 170, PBSDF.location.y - 110)
                                material.node_tree.links.new(bfc_node.outputs[0], PBSDF.inputs[4])
                                material.node_tree.links.new(image_texture_node.outputs[1], bfc_node.inputs[0])
                                
                        else:
                            if MaterialIn(Backface_Culling_Materials, material):
                                bfc_node = None

                                for node in material.node_tree.nodes:
                                    if node.type == "GROUP":
                                        if "Backface Culling" in node.node_tree.name:
                                            material.node_tree.nodes.remove(node)

                                material.use_backface_culling = False

                        selected_object.data.update()
                else:
                    CEH('m002')
        else:
            CEH('m003', Data=selected_object)

def create_sky(self=None):
    scene = bpy.context.scene
    world = scene.world
    clouds_exists = False
    
    if world != None and world == bpy.data.worlds.get(world_material_name):
        if self != None:

            if self.reappend_material == True:

                if world == bpy.data.worlds.get(world_material_name):
                    bpy.data.worlds.remove(bpy.data.worlds.get(world_material_name))

                try:
                    with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                        data_to.worlds = [world_material_name]
                    appended_world_material = bpy.data.worlds.get(world_material_name)
                except:
                    CEH('004')

                bpy.context.scene.world = appended_world_material
            
            if self.reset_settings == True:
                world_material = bpy.context.scene.world.node_tree
                Sky_Group = None

                for node in world_material.nodes:
                    if node.type == 'GROUP':
                        if "Mcblend Sky" in node.node_tree.name:
                            Sky_Group = node
                            for group in bpy.data.node_groups:
                                if node.node_tree.name in group.name:
                                    node.inputs["Moon Strenght"].default_value = group.interface.items_tree[6].default_value
                                    node.inputs["Sun Strength"].default_value = group.interface.items_tree[7].default_value
                                    node.inputs["Stars Strength"].default_value = group.interface.items_tree[8].default_value
                                    node.inputs["Camera Ambient Light Strenght"].default_value = group.interface.items_tree[9].default_value
                                    node.inputs["Non-Camera Ambient Light Strenght"].default_value = group.interface.items_tree[10].default_value
                                    node.inputs["Time"].default_value = group.interface.items_tree[1].default_value
                                    node.inputs["Rotation"].default_value[0] = group.interface.items_tree[2].default_value[0]
                                    node.inputs["Rotation"].default_value[1] = group.interface.items_tree[2].default_value[1]
                                    node.inputs["Rotation"].default_value[2] = group.interface.items_tree[2].default_value[2]
                                    node.inputs["Pixelated Stars"].default_value = group.interface.items_tree[3].default_value
                                    node.inputs["Moon Color"].default_value = group.interface.items_tree[12].default_value
                                    node.inputs["Sun Color"].default_value = group.interface.items_tree[13].default_value
                                    node.inputs["Sun Color In Sunset"].default_value = group.interface.items_tree[14].default_value
                                    node.inputs["Stars Color"].default_value  = group.interface.items_tree[15].default_value
                
                if Sky_Group == None:
                    CEH('m005')

            if self.recreate_clouds == True:
                for obj in bpy.context.scene.objects:
                    if obj.name == "Clouds":
                        bpy.data.objects.remove(obj, do_unlink=True)

                if clouds_node_tree_name not in bpy.data.node_groups:
                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator.blend"), link=False) as (data_from, data_to):
                        data_to.node_groups = [clouds_node_tree_name]
                else:
                    bpy.data.node_groups[clouds_node_tree_name]

                bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
                bpy.context.object.name = "Clouds"
                bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
                geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
                geonodes_modifier.node_group = bpy.data.node_groups.get(clouds_node_tree_name)
                geonodes_modifier["Socket_11"] = bpy.context.scene.camera
        else:
            bpy.ops.wm.recreate_sky('INVOKE_DEFAULT')
    else:
        try:
            if world_material_name not in bpy.data.worlds:
                with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                    data_to.worlds = [world_material_name]
                appended_world_material = bpy.data.worlds.get(world_material_name)
            else:
                appended_world_material = bpy.data.worlds[world_material_name]
            bpy.context.scene.world = appended_world_material
        except:
            CEH("004")

        for obj in scene.objects:
            if obj.name == "Clouds":
                clouds_exists = True
                break
            else:
                clouds_exists = False

        if scene.sky_properties.create_clouds and clouds_exists == False:                    
            if clouds_node_tree_name not in bpy.data.node_groups:
                with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Clouds Generator.blend"), link=False) as (data_from, data_to):
                    data_to.node_groups = [clouds_node_tree_name]
            else:
                bpy.data.node_groups[clouds_node_tree_name]

            bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
            bpy.context.object.name = "Clouds"
            bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
            geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
            geonodes_modifier.node_group = bpy.data.node_groups.get(clouds_node_tree_name)
            geonodes_modifier["Socket_11"] = scene.camera

    bpy.context.view_layer.update()

# Fix materials
    
def fix_materials():
    for selected_object in bpy.context.selected_objects:
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                if material != None:
                    image_texture_node = None
                    PBSDF = None

                    material.blend_method = 'HASHED'

                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            if ".00" not in node.name:
                                image_texture_node = node
                            node.interpolation = "Closest" 
                        
                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node

                    if (image_texture_node and PBSDF) != None:
                        material.node_tree.links.new(image_texture_node.outputs["Alpha"], PBSDF.inputs[4])
                else:
                    CEH('m002')
                
        else:
            CEH('m003', Data=selected_object)
            
        selected_object.data.update()

#
        
# Set Procedural PBR
        
def setproceduralpbr():
    for selected_object in bpy.context.selected_objects:
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                if material != None:
                    image_texture_node = None
                    PBSDF = None
                    bump_node = None
                    math_nodes = []
                    scene = bpy.context.scene
                    PProperties = scene.ppbr_properties

                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            if ".00" not in node.name:
                                image_texture_node = node

                        if node.type == "BUMP":
                            bump_node = node

                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node

                    if PBSDF != None:

                        # Use Bump
                        if PProperties.use_bump == True:
                            if image_texture_node and bump_node == None:
                                bump_node = material.node_tree.nodes.new(type='ShaderNodeBump')
                                bump_node.location = (PBSDF.location.x - 200, PBSDF.location.y - 100)
                                material.node_tree.links.new(image_texture_node.outputs["Color"], bump_node.inputs['Height'])
                                material.node_tree.links.new(bump_node.outputs['Normal'], PBSDF.inputs['Normal'])
                                bump_node.inputs[0].default_value = PProperties.bump_strenght
                            if bump_node != None:
                                bump_node.inputs[0].default_value = PProperties.bump_strenght
                        else:
                            if bump_node is not None:
                                material.node_tree.nodes.remove(bump_node)
                                

                        # Change PBSDF Settings                                
                        if PProperties.change_bsdf:
                            PBSDF.inputs["Roughness"].default_value = PProperties.roughness
                            PBSDF.inputs["Specular IOR Level"].default_value = PProperties.specular


                        # Use SSS                            
                        if PProperties.use_sss  == True and MaterialIn(SSS_Materials, material):
                            PBSDF.subsurface_method = PProperties.sss_type
                            PBSDF.inputs["Subsurface Weight"].default_value = PProperties.sss_weight
                            PBSDF.inputs["Subsurface Radius"].default_value[0] = 1.0
                            PBSDF.inputs["Subsurface Radius"].default_value[1] = 1.0
                            PBSDF.inputs["Subsurface Radius"].default_value[2] = 1.0
                            PBSDF.inputs["Subsurface Scale"].default_value = PProperties.sss_scale


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
                            Animate = False
                            
                            # Texture Check
                            for node in material.node_tree.nodes:
                                if node.type == "TEX_IMAGE":
                                    if ".00" not in node.name:
                                        image_texture_node = node

                            # Main Thing
                            if image_texture_node != None:

                                for node in material.node_tree.nodes:
                                    if node.type == 'GROUP':
                                        if BATGroup in node.node_tree.name:
                                            node_group = node

                                # BATGroup Import if BATGroup isn't in File
                                if node_group == None:
                                    
                                    if BATGroup not in bpy.data.node_groups:
                                        with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                                            data_to.node_groups = [BATGroup]

                                    node_group = material.node_tree.nodes.new(type='ShaderNodeGroup')
                                    node_group.node_tree = bpy.data.node_groups[BATGroup]

                                # Settings Set
                                for material_name, material_properties in Emissive_Materials.items():
                                    if material.name in Emissive_Materials:
                                        if material_name in material.name.lower():
                                            for property_name, property_value in material_properties.items():
                                                    if property_name != "Exclude":
                                                        node_group.inputs[property_name].default_value = property_value

                                            if "Middle Value" in material_properties and 9 in material_properties and 10 in material_properties and "Adder" in material_properties and "Divider" in material_properties:
                                                Animate = True
                                        
                                            node_group.inputs["Better Emission"].default_value = PProperties.make_better_emission
                                            node_group.inputs["Animate Textures"].default_value = (PProperties.animate_textures and Animate)

                                    else:
                                        if material_name == "Default":
                                             for property_name, property_value in material_properties.items():
                                                if property_name != "Exclude":
                                                    node_group.inputs[property_name].default_value = property_value
                                
                                # Color Connection if Nothing Connected
                                if not IsConnectedTo(None, None, None, "BSDF_PRINCIPLED", 26):
                                    material.node_tree.links.new(image_texture_node.outputs[0], PBSDF.inputs[26])

                                # Написать логику для присоединения к ноде IsConnectedTo(None, None, None, "BSDF_PRINCIPLED", 27)
                                    
                                for node in material.node_tree.nodes:
                                    if node.type == "BSDF_PRINCIPLED":
                                        for link in node.inputs[27].links:
                                            if link.from_node != node_group:
                                                for output in link.from_node.outputs:
                                                    for link in output.links:
                                                        if link.to_socket.node.name == node.name:
                                                            material.node_tree.links.new(link.from_socket, node_group.inputs["Multiply"])

                                node_group.location = (PBSDF.location.x - 200, PBSDF.location.y - 250)
                                material.node_tree.links.new(image_texture_node.outputs[0], node_group.inputs["Emission Color"])
                                material.node_tree.links.new(node_group.outputs["Emission Strength"], PBSDF.inputs[27])

                        if PProperties.make_better_emission == False and PProperties.animate_textures == False:
                            for node in material.node_tree.nodes:
                                if node.type == 'GROUP':
                                    if BATGroup in node.node_tree.name:
                                        material.node_tree.nodes.remove(node)
                else:
                    CEH('m002')
                
        else:
            CEH('m003', Data=selected_object)
            
        selected_object.data.update()
#
        
# TODO:
    # Upgrade World - Сделать так чтобы выбирались определённые фейсы у мира > они отделялись от него в отдельный объект > Как-то группировались > Производилась замена этих объектов на риги (Сундук)
    # Texture logic - Сделать использование текстур из папки, например из папки tex или из папки майнкрафта
    # Upgrade World - Сщединённое стекло: Импортировать текстуры соединённого > Выбираются фейсы с материалом стекла > Математически вычислить находятся ли стёкла рядом (if Glass.location.x + 1: поставить сообтветствующую текстуру стекла)