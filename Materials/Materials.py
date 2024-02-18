import bpy
import os
from ..Data import *
from bpy.props import (IntProperty, BoolProperty, FloatProperty)

#Replace Materials

script_directory = os.path.dirname(os.path.realpath(__file__))
blend_file_path = os.path.join(script_directory, "Materials.blend")

def MaterialIn(Array, material):
    for keyword in Array:
        if keyword in material.name.lower():
            return True
        else:
            return False

def append_materials(upgraded_material_name, selected_object, i):
    if upgraded_material_name not in bpy.data.materials:
        with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
            data_to.materials = [upgraded_material_name]
        appended_material = bpy.data.materials.get(upgraded_material_name)
        selected_object.data.materials[i] = appended_material
    else:
        selected_object.data.materials[i] = bpy.data.materials[upgraded_material_name]

def upgrade_materials():
    for selected_object in bpy.context.selected_objects:
        for i, material in enumerate(selected_object.data.materials):
            for original_material, upgraded_material in Materials.items():
                if original_material in material.name.lower() and upgraded_material != "Exclude":
                    append_materials(upgraded_material, selected_object, i)

# Fix World
                        
def fix_world():
    for selected_object in bpy.context.selected_objects:
        for material in selected_object.data.materials:
            PBSDF = None
            mix_node = None

            if material != None:
                if MaterialIn(Alpha_Blend_Materials, material):
                    material.blend_method = 'BLEND'
                else:
                    material.blend_method = 'HASHED'

                if material.node_tree.nodes.get("Principled BSDF") != None:
                    PBSDF = material.node_tree.nodes.get("Principled BSDF")

                for node in material.node_tree.nodes:
                    if node.type == "TEX_IMAGE":
                        image_texture_node = material.node_tree.nodes[node.name]
                        image_texture_node.interpolation = "Closest"
                        
                if (image_texture_node and PBSDF) != None:
                    material.node_tree.links.new(image_texture_node.outputs["Alpha"], PBSDF.inputs[4])
                    if PBSDF.inputs[27].default_value != 0:
                        material.node_tree.links.new(image_texture_node.outputs["Color"], PBSDF.inputs[26])

                    if bpy.context.scene.ppbr_properties.backface_culling:
                        if MaterialIn(Backface_Culling_Materials, material):
                            geometry_node = None
                            invert_node = None
                            mix_node = None

                            material.use_backface_culling = True
                            for node in material.node_tree.nodes:
                                if node.name == "Geometry":
                                    geometry_node = node

                                if node.name == "Invert Color":
                                    invert_node = node

                                if node.name == "Mix":
                                    mix_node = node
                            
                            if geometry_node == None:
                                geometry_node = material.node_tree.nodes.new(type='ShaderNodeNewGeometry')
                                geometry_node.location = (image_texture_node.location.x + 100, image_texture_node.location.y + 230)
                                gemetry_exists = True
                            
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
                        if MaterialIn(Backface_Culling_Materials, material):
                            material.use_backface_culling = False

                selected_object.data.update()
            else:
                raise ValueError("Material doesn't exist on one of the slots, error code: 002")

def create_sky():

    script_directory = os.path.dirname(os.path.realpath(__file__))
    node_tree_name = "Clouds Generator 2"
    world_material_name = "Mcblend World"
    world = bpy.context.scene.world
    clouds_exists = False
    
    if world != None and world == bpy.data.worlds.get(world_material_name):
        bpy.ops.wm.recreate_sky('INVOKE_DEFAULT')
    else:
        try:
            if world_material_name not in bpy.data.worlds:
                with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
                    data_to.worlds = [world_material_name]
                appended_world_material = bpy.data.worlds.get(world_material_name)
            else:
                appended_world_material = bpy.data.worlds[world_material_name]
            bpy.context.scene.world = appended_world_material

        except FileNotFoundError as err:
            print(f"Не найден файл мира, код ошибки 003: {err}")

        if bpy.context.scene.sky_properties.create_clouds:                    
            for obj in bpy.context.scene.objects:
                if obj.name == "Clouds":
                    clouds_exists = True

            if clouds_exists == False:
                if node_tree_name not in bpy.data.node_groups:
                    with bpy.data.libraries.load(os.path.join(script_directory, "Clouds Generator.blend"), link=False) as (data_from, data_to):
                        data_to.node_groups = [node_tree_name]
                else:
                    bpy.data.node_groups[node_tree_name]

                bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
                bpy.context.object.name = "Clouds"
                bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
                geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
                geonodes_modifier.node_group = bpy.data.node_groups.get(node_tree_name)
                geonodes_modifier["Socket_11"] = bpy.context.scene.camera

            bpy.context.view_layer.update()

# Fix materials
    
def fix_materials():
    for selected_object in bpy.context.selected_objects:
        for material in selected_object.data.materials:
            if material != None:
                image_texture_node = None
                PBSDF = None

                material.blend_method = 'HASHED'

                for node in material.node_tree.nodes:
                    if node.type == "TEX_IMAGE":
                        image_texture_node = material.node_tree.nodes[node.name]
                        material.node_tree.nodes[node.name].interpolation = "Closest" 
                
                if material.node_tree.nodes.get("Principled BSDF") != None:
                    PBSDF = material.node_tree.nodes.get("Principled BSDF")

                if (image_texture_node and PBSDF) != None:
                    material.node_tree.links.new(image_texture_node.outputs["Alpha"], PBSDF.inputs[4])
            else:
                raise ValueError("Material doesn't exist on one of the slots, error code: 002")
            
        selected_object.data.update()

#
        
# Set Procedural PBR
        
def setproceduralpbr():
    for selected_object in bpy.context.selected_objects:
        for material in selected_object.data.materials:
            if material != None:
                scene = bpy.context.scene
                image_texture_node = None
                PBSDF = None
                bump_node = None
                

                if material.node_tree.nodes.get("Principled BSDF") is not None:
                    PBSDF = material.node_tree.nodes.get("Principled BSDF")

                    # Change PBSDF Settings
                    if scene.ppbr_properties.change_bsdf_settings:
                        PBSDF.inputs["Roughness"].default_value = bpy.context.scene.ppbr_properties.roughness
                        PBSDF.inputs[12].default_value = bpy.context.scene.ppbr_properties.specular
                    
                    # Make Metals
                    if scene.ppbr_properties.make_metal == True and MaterialIn(Metal, material):
                        PBSDF.inputs["Roughness"].default_value = 0.2
                        PBSDF.inputs["Metallic"].default_value = 0.7

                    if MaterialIn(Reflective, material):
                        PBSDF.inputs["Roughness"].default_value = 0.1

                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            image_texture_node = material.node_tree.nodes[node.name]
                        if node.type == "BUMP":
                            bump_node = material.node_tree.nodes[node.name]

                    # Use Bump
                    if scene.ppbr_properties.use_bump == True:
                        if image_texture_node and bump_node == None:
                            bump_node = material.node_tree.nodes.new(type='ShaderNodeBump')
                            bump_node.location = (PBSDF.location.x - 200, PBSDF.location.y - 100)
                            material.node_tree.links.new(image_texture_node.outputs["Color"], bump_node.inputs['Height'])
                            material.node_tree.links.new(bump_node.outputs['Normal'], PBSDF.inputs['Normal'])
                            bump_node.inputs[0].default_value = bpy.context.scene.ppbr_properties.bump_strenght
                        if bump_node != None:
                            bump_node.inputs[0].default_value = bpy.context.scene.ppbr_properties.bump_strenght
                    else:
                        if material.node_tree.nodes.get("Bump") is not None:
                            bump_node = material.node_tree.nodes.get("Bump")
                            material.node_tree.nodes.remove(bump_node)

                    # Make Better Emission
                    if scene.ppbr_properties.make_better_emission == True and PBSDF.inputs[27].default_value != 0:

                        image_texture_node = None

                        for node in material.node_tree.nodes:
                            if node.type == "TEX_IMAGE":
                                image_texture_node = material.node_tree.nodes[node.name]

                        if image_texture_node != None:

                            math_node = None
                            map_range_node = None

                            for node in material.node_tree.nodes:
                                if node.name == "Map Range":
                                    map_range_node = node

                                if node.name == "Math":
                                    if node.operation == 'MULTIPLY':
                                        math_node = node

                            if map_range_node == None:
                                map_range_node = material.node_tree.nodes.new(type='ShaderNodeMapRange')
                                map_range_node.location = (PBSDF.location.x - 400, PBSDF.location.y - 240)
                            else:
                                map_range_node.location = (PBSDF.location.x - 400, PBSDF.location.y - 240)

                            for material_name, material_properties in Emissive_Materials.items():
                                for property_name, property_value in material_properties.items():
                                    if property_name == "Interpolation Type":
                                        map_range_node.interpolation_type = property_value
                                    else:
                                        map_range_node.inputs[property_name].default_value = property_value

                            if math_node == None:
                                math_node = material.node_tree.nodes.new(type='ShaderNodeMath')
                                math_node.location = (PBSDF.location.x - 200, PBSDF.location.y - 280)
                                math_node.operation = 'MULTIPLY'

                            math_node.location = (PBSDF.location.x - 200, PBSDF.location.y - 280)
                            material.node_tree.links.new(image_texture_node.outputs["Color"], map_range_node.inputs[0])
                            material.node_tree.links.new(map_range_node.outputs[0], math_node.inputs[0])
                            material.node_tree.links.new(math_node.outputs[0], PBSDF.inputs[27])

                    # Animate Textures
                    if scene.ppbr_properties.animate_textures == True and PBSDF.inputs[27].default_value != 0:
                        node_tree_name = "Procedural Animation V1.1"
                        
                        map_range_node = None
                        math_node = None

                        for node in material.node_tree.nodes:
                            if node.name == "Map Range":
                                map_range_node = node

                            if node.name == "Math":
                                if node.operation == 'MULTIPLY':
                                    math_node = node
                        
                        if node.type == 'GROUP' and node_tree_name in node.node_tree.name:
                                node_group = node
                        else:
                            if node_tree_name not in bpy.data.node_groups:
                                with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
                                    data_to.node_groups = [node_tree_name]
                            else:
                                bpy.data.node_groups[node_tree_name]

                            node_group = material.node_tree.nodes.new(type='ShaderNodeGroup')
                            node_group.node_tree = bpy.data.node_groups[node_tree_name]

                            if material.name in Animatable_Materials.keys():
                                for input_name, value in Animatable_Materials[material.name].items():
                                    node_group.inputs[input_name].default_value = value

                        if scene.ppbr_properties.make_better_emission == True or (map_range_node and math_node) != None:
                            material.node_tree.links.new(node_group.outputs[0], math_node.inputs[1])
                            node_group.location = (PBSDF.location.x - 400, PBSDF.location.y - 460)
                        else:
                            material.node_tree.links.new(node_group.outputs[0], PBSDF.inputs[27])
                            node_group.location = (PBSDF.location.x - 200, PBSDF.location.y - 300)
                            
            else:
                raise ValueError("Material doesn't exist on one of the slots, error code: 002")
            
        selected_object.data.update()
#
        
# TODO:
    # Upgrade World - Сделать так чтобы выбирались определённые фейсы у мира > они отделялись от него в отдельный объект > Как-то группировались > Производилась замена этих объектов на риги (Сундук)
    # Texture logic - Сделать использование текстур из папки, например из папки tex или из папки майнкрафта
    # Upgrade World - Сщединённое стекло: Импортировать текстуры соединённого > Выбираются фейсы с материалом стекла > Математически вычислить находятся ли стёкла рядом (if Glass.location.x + 1: поставить сообтветствующую текстуру стекла)