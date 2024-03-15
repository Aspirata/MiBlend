from ..Data import *

#Replace Materials

def MaterialIn(Array, material):
    for keyword in Array:
        if keyword in material.name.lower():
            return True

def IsConnectedTo(NodeFromName, NodeFromType, index, nodeTo, NodeToName, NodeToType, type=None):
    if nodeTo is None:
        for selected_object in bpy.context.selected_objects:
            if selected_object.material_slots:
                for material in selected_object.data.materials:
                    if material is not None:                                               # Materials Check
                        for Node in material.node_tree.nodes:                              # Every Node in Material Check
                            if NodeToName is not None:
                                if NodeToName in Node.name:
                            
                                    if NodeFromName is not None and NodeFromType is None:
                                        for link in Node.inputs[index].links:
                                            if NodeFromName in link.from_node.name:
                                                if type == "if":
                                                    return True
                                                else:
                                                    return Node
                                    
                                    if NodeFromType is not None and NodeFromName is None:
                                        if NodeFromType == link.from_node.type:
                                            if type == "if":
                                                return True
                                            else:
                                                return Node
                                        
                                    if NodeFromName is not None and NodeFromType is not None:
                                        if NodeFromName in link.from_node.name and NodeFromType == link.from_node.type:
                                            if type == "if":
                                                return True
                                            else:
                                                return Node
                                            
                            if NodeToType is not None:
                                if NodeToType == Node.type:
                                    if NodeFromName is not None and NodeFromType is None:
                                        for link in Node.inputs[index].links:
                                            if NodeFromName in link.from_node.name:
                                                if type == "if":
                                                    return True
                                                else:
                                                    return Node
                                    
                                    if NodeFromType is not None and NodeFromName is None:
                                        if NodeFromType == link.from_node.type:
                                            if type == "if":
                                                return True
                                            else:
                                                return Node
                                        
                                    if NodeFromName is not None and NodeFromType is not None:
                                        if NodeFromName in link.from_node.name and NodeFromType == link.from_node.type:
                                            if type == "if":
                                                return True
                                            else:
                                                return Node

                            if NodeToName is not None and NodeToType is not None:
                                if NodeToName == Node.name and NodeToType == Node.type:
                                    if NodeFromName is not None and NodeFromType is None:
                                        for link in Node.inputs[index].links:
                                            if NodeFromName in link.from_node.name:
                                                if type == "if":
                                                    return True
                                                else:
                                                    return Node
                                    
                                    if NodeFromType is not None and NodeFromName is None:
                                        if NodeFromType == link.from_node.type:
                                            if type == "if":
                                                return True
                                            else:
                                                return Node
                                        
                                    if NodeFromName is not None and NodeFromType is not None:
                                        if NodeFromName in link.from_node.name and NodeFromType == link.from_node.type:
                                            if type == "if":
                                                return True
                                            else:
                                                return Node

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

                if bpy.context.scene.ppbr_properties.emissiondetection == 'Automatic & Manual' and ((material_name in material.name.lower() and Excluded == False) or PBSDF.inputs[27].default_value != 0):
                    return 1

                if bpy.context.scene.ppbr_properties.emissiondetection == 'Automatic' and PBSDF.inputs[27].default_value != 0:
                    return 2

                if bpy.context.scene.ppbr_properties.emissiondetection == 'Manual' and (material_name in material.name.lower() and Excluded == False):
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
                    mix_node = None
                    image_texture_node = None
                    scene = bpy.context.scene

                    if MaterialIn(Alpha_Blend_Materials, material):
                        material.blend_method = 'BLEND'
                    else:
                        material.blend_method = 'HASHED'

                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
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
                        if scene.ppbr_properties.backface_culling:
                            if MaterialIn(Backface_Culling_Materials, material):
                                if bpy.context.scene.render.engine == 'CYCLES':
                                    geometry_node = None
                                    invert_node = None
                                    mix_node = None

                                    
                                    for node in material.node_tree.nodes:
                                        if node.type == "NEW_GEOMETRY":
                                            geometry_node = node

                                        if node.type == "INVERT":
                                            invert_node = node

                                        if node.type == "MIX":
                                            mix_node = node
                                    
                                    if geometry_node == None:
                                        geometry_node = material.node_tree.nodes.new(type='ShaderNodeNewGeometry')
                                        geometry_node.location = (image_texture_node.location.x + 100, image_texture_node.location.y + 230)
                                    
                                    if  invert_node == None:
                                        invert_node = material.node_tree.nodes.new(type='ShaderNodeInvert')
                                        invert_node.location = (image_texture_node.location.x + 260, image_texture_node.location.y - 200)

                                    if mix_node == None:
                                        mix_node = material.node_tree.nodes.new(type='ShaderNodeMix')
                                        mix_node.location = (invert_node.location.x + 170, image_texture_node.location.y - 110)
                                        mix_node.blend_type = 'MULTIPLY'
                                        mix_node.data_type =  'RGBA'
                                        mix_node.inputs[0].default_value = 1
                                        material.node_tree.links.new(image_texture_node.outputs["Alpha"], mix_node.inputs["B"])
                                        material.node_tree.links.new(mix_node.outputs["Result"], PBSDF.inputs["Alpha"])
                                    else:
                                        material.node_tree.links.new(image_texture_node.outputs["Alpha"], mix_node.inputs["B"])
                                        material.node_tree.links.new(mix_node.outputs["Result"], PBSDF.inputs["Alpha"])
                                    
                                    material.node_tree.links.new(geometry_node.outputs["Backfacing"], invert_node.inputs[1])
                                    material.node_tree.links.new(invert_node.outputs["Color"], mix_node.inputs["A"])
                                else:
                                    material.use_backface_culling = True
                        else:
                            if MaterialIn(Backface_Culling_Materials, material):
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
                    scene = bpy.context.scene
                    PProperties = scene.ppbr_properties

                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            image_texture_node = material.node_tree.nodes[node.name]
                        if node.type == "BUMP":
                            bump_node = material.node_tree.nodes[node.name]
                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node

                    if PBSDF != None:
                        # Change PBSDF Settings
                        if scene.ppbr_properties.change_bsdf_settings:
                            PBSDF.inputs["Roughness"].default_value = scene.ppbr_properties.roughness
                            PBSDF.inputs[12].default_value = scene.ppbr_properties.specular
                        
                        # Make Metals
                        if scene.ppbr_properties.make_metal == True and MaterialIn(Metal, material):
                            PBSDF.inputs["Roughness"].default_value = PProperties.metal_roughness
                            PBSDF.inputs["Metallic"].default_value = PProperties.metal_metallic

                        if scene.ppbr_properties.make_reflections == True and MaterialIn(Reflective, material):
                            PBSDF.inputs["Roughness"].default_value = PProperties.reflections_roughness

                        # Use Bump
                        if scene.ppbr_properties.use_bump == True:
                            if image_texture_node and bump_node == None:
                                bump_node = material.node_tree.nodes.new(type='ShaderNodeBump')
                                bump_node.location = (PBSDF.location.x - 200, PBSDF.location.y - 100)
                                material.node_tree.links.new(image_texture_node.outputs["Color"], bump_node.inputs['Height'])
                                material.node_tree.links.new(bump_node.outputs['Normal'], PBSDF.inputs['Normal'])
                                bump_node.inputs[0].default_value = scene.ppbr_properties.bump_strenght
                            if bump_node != None:
                                bump_node.inputs[0].default_value = scene.ppbr_properties.bump_strenght
                        else:
                            if material.node_tree.nodes.get("Bump") is not None:
                                bump_node = material.node_tree.nodes.get("Bump")
                                material.node_tree.nodes.remove(bump_node)

                        # Make Better Emission
                        if scene.ppbr_properties.make_better_emission == True:
                                
                                if EmissionMode(PBSDF, material):

                                    image_texture_node = None

                                    for node in material.node_tree.nodes:
                                        if node.type == "TEX_IMAGE":
                                            image_texture_node = node

                                    if image_texture_node != None:

                                        math_node = None
                                        map_range_node = None

                                        for node in material.node_tree.nodes:
                                            if node.type == "MAP_RANGE":
                                                map_range_node = node

                                            if node.type == "MATH" and "Mcblend's Node" in node.name:
                                                if node.operation == 'MULTIPLY':
                                                    math_node = node


                                        if map_range_node == None:
                                            map_range_node = material.node_tree.nodes.new(type='ShaderNodeMapRange')
                                            map_range_node.name = "Mcblend's Node"
                                            map_range_node.location = (PBSDF.location.x - 400, PBSDF.location.y - 240)
                                        else:
                                            map_range_node.location = (PBSDF.location.x - 400, PBSDF.location.y - 240)

                                        for material_name, material_properties in Emissive_Materials.items():
                                            if material_name in material.name:
                                                for property_name, property_value in material_properties.items():
                                                    if property_name == "Interpolation Type":
                                                        map_range_node.interpolation_type = property_value

                                                    if type(property_name) == int:
                                                        map_range_node.inputs[property_name].default_value = property_value
                                            else:
                                                if material_name == "Default":
                                                    for property_name, property_value in material_properties.items():
                                                        if property_name == "Interpolation Type":
                                                            map_range_node.interpolation_type = property_value

                                                        if type(property_name) == int:
                                                            map_range_node.inputs[property_name].default_value = property_value
                                            

                                        if math_node == None:
                                            math_node = material.node_tree.nodes.new(type='ShaderNodeMath')
                                            math_node.location = (PBSDF.location.x - 200, PBSDF.location.y - 280)
                                            math_node.operation = 'MULTIPLY'
                                            math_node.inputs[1].default_value = 1.0
                                            math_node.name = "Mcblend's Node"

                                        math_node.location = (PBSDF.location.x - 200, PBSDF.location.y - 280)
                                        material.node_tree.links.new(image_texture_node.outputs["Color"], map_range_node.inputs[0])
                                        material.node_tree.links.new(map_range_node.outputs[0], math_node.inputs[0])
                                        material.node_tree.links.new(math_node.outputs[0], PBSDF.inputs[27])

                                        if not IsConnectedTo(None, None, 26, None, None, "BSDF_PRINCIPLED"):
                                            material.node_tree.links.new(image_texture_node.outputs[0], PBSDF.inputs[26])

                        else:
                            for node in material.node_tree.nodes:
                                if node.type == "MAP_RANGE":
                                    material.node_tree.nodes.remove(node)

                        # Animate Textures
                        if scene.ppbr_properties.animate_textures == True:

                            if EmissionMode(PBSDF, material):

                                for material_name, material_properties in Emissive_Materials.items():
                                    for property_name, property_value in material_properties.items():
                                        if property_name == "Animate":
                                            Animate = property_value

                                if Animate == True:
                                    map_range_node = None
                                    math_node = None
                                    node_group = None

                                    for node in material.node_tree.nodes:
                                        if node.type == "MAP_RANGE":
                                            map_range_node = node

                                        if node.type == "MATH" and "Mcblend's Node" in node.name:
                                            if node.operation == 'MULTIPLY':
                                                math_node = node
                                        
                                        if node.type == 'GROUP':
                                            if PAGroup in node.node_tree.name:
                                                node_group = node


                                    if node_group == None:
                                        if PAGroup not in bpy.data.node_groups:
                                            with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                                                data_to.node_groups = [PAGroup]
                                        else:
                                            bpy.data.node_groups[PAGroup]

                                        node_group = material.node_tree.nodes.new(type='ShaderNodeGroup')
                                        node_group.name = "Mcblend's Node"
                                        node_group.node_tree = bpy.data.node_groups[PAGroup]

                                        for material_name, material_properties in Emissive_Materials.items():
                                            if material_name in material.name:
                                                for property_name, property_value in material_properties.items():
                                                    if property_name != "Exclude" and property_name != "Interpolation Type" and property_name != "Animate" and type(property_name) == str:
                                                        if property_name == "Divider":
                                                            node_group.inputs[property_name].default_value = bpy.context.scene.render.fps/30 * property_value
                                                        else:
                                                            node_group.inputs[property_name].default_value = property_value
                                            else:
                                                if material_name == "Default":
                                                    for property_name, property_value in material_properties.items():
                                                        if property_name != "Exclude" and property_name != "Interpolation Type" and property_name != "Animate" and type(property_name) == str:
                                                            if property_name == "Divider":
                                                                node_group.inputs[property_name].default_value = bpy.context.scene.render.fps/30 * property_value
                                                            else:
                                                                node_group.inputs[property_name].default_value = property_value

                                    if math_node != None:
                                        if IsConnectedTo("Mcblend's Node", None, 0, math_node, None, None) and IsConnectedTo(None, None, 1, math_node, None, None) and not IsConnectedTo("Mcblend's Node", 'GROUP', 1, math_node, None, None):
                                            old_math_node = math_node
                                            math_node = material.node_tree.nodes.new(type='ShaderNodeMath')
                                            math_node.location = (PBSDF.location.x - 200, PBSDF.location.y - 280)
                                            math_node.operation = 'MULTIPLY'
                                            material.node_tree.links.new(old_math_node.outputs[0], math_node.inputs[0])
                                            math_node.inputs[1].default_value = 1.0
                                            math_node.name = "Mcblend's Node"
                                            material.node_tree.links.new(math_node.outputs[0], PBSDF.inputs[27])

                                    else:
                                        math_node = material.node_tree.nodes.new(type='ShaderNodeMath')
                                        math_node.location = (PBSDF.location.x - 200, PBSDF.location.y - 280)
                                        math_node.operation = 'MULTIPLY'
                                        math_node.inputs[0].default_value = 1.0
                                        math_node.inputs[1].default_value = 1.0
                                        math_node.name = "Mcblend's Node"
                                        material.node_tree.links.new(math_node.outputs[0], PBSDF.inputs[27])

                                    material.node_tree.links.new(node_group.outputs[0], math_node.inputs[1])
                                    node_group.location = (PBSDF.location.x - 400, PBSDF.location.y - 460)

                                    if not IsConnectedTo(None, None, 26, None, None, "BSDF_PRINCIPLED"):
                                        material.node_tree.links.new(image_texture_node.outputs[0], PBSDF.inputs[26])

                        else:
                            for node in material.node_tree.nodes:
                                if node.type == 'GROUP' and "Mcblend's Node" in node.name:
                                    if PAGroup in node.node_tree.name:
                                        material.node_tree.nodes.remove(node)
                                #try:
                            for node in material.node_tree.nodes:
                                if node.type == "MATH" and "Mcblend's Node" in node.name:
                                    if node.operation == 'MULTIPLY':
                                        if not IsConnectedTo(None, None, 0, node, None, None) and not IsConnectedTo(None, None, 1, node, None, None):
                                            material.node_tree.nodes.remove(node)
                                #except:
                                    #print("PPBR 621 Error Ingored LoL Do not report this")
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