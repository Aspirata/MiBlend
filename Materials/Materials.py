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
                if original_material in material.name.lower():
                    append_materials(upgraded_material, selected_object, i)

# Fix World
                        
def fix_world():
    for selected_object in bpy.context.selected_objects:
        for material in selected_object.data.materials:
            PBSDF = None
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
                    if MaterialIn(Emissive_Materials, material):
                        material.node_tree.links.new(image_texture_node.outputs["Color"], PBSDF.inputs[26])

                    if MaterialIn(Backface_Culling_Materials, material):
                        material.use_backface_culling = True
                        geometry_node = material.node_tree.nodes.new(type='ShaderNodeNewGeometry')
                        geometry_node.location = (image_texture_node.location.x + 100, image_texture_node.location.y + 230)
                        invert_node = material.node_tree.nodes.new(type='ShaderNodeInvert')
                        invert_node.location = (image_texture_node.location.x + 260, image_texture_node.location.y - 200)
                        mix_node = material.node_tree.nodes.new(type='ShaderNodeMix')
                        mix_node.location = (invert_node.location.x + 170, image_texture_node.location.y - 110)
                        mix_node.blend_type = 'MULTIPLY'
                        mix_node.data_type =  'RGBA'
                        mix_node.inputs[0].default_value = 1
                        material.node_tree.links.new(geometry_node.outputs["Backfacing"], invert_node.inputs[1])
                        material.node_tree.links.new(invert_node.outputs["Color"], mix_node.inputs["A"])
                        material.node_tree.links.new(image_texture_node.outputs["Alpha"], mix_node.inputs["B"])
                        material.node_tree.links.new(mix_node.outputs["Result"], PBSDF.inputs["Alpha"])
                selected_object.data.update()
            else:
                raise ValueError("Материал на одном из слоёв не существует, код ошибки: 002")

def create_sky():

    world_material_name = "Mcblend World"
    world = bpy.context.scene.world
    
    if hasattr(bpy.context.scene.world, 'Rotation') or bpy.context.scene.world == bpy.data.worlds.get(world_material_name):
        bpy.ops.wm.recreate_sky('INVOKE_DEFAULT')
    else:
        world["Rotation"] = 0.0
        bpy.types.World.Rotation = FloatProperty(name="Rotation", description="Rotation For World", default=0.0, min=0.0, max=960.0, subtype='ANGLE')

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

#def create_clouds():


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
                raise ValueError("Материал на одном из слоёв не существует, код ошибки: 002")
            
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

                    if scene.ppbr_properties.change_bsdf_settings:
                        PBSDF.inputs["Roughness"].default_value = bpy.context.scene.ppbr_properties.roughness
                        PBSDF.inputs[12].default_value = bpy.context.scene.ppbr_properties.specular
                    
                    if scene.ppbr_properties.make_metal == True:
                        if MaterialIn(Metal, material):
                            PBSDF.inputs["Roughness"].default_value = 0.2
                            PBSDF.inputs["Metallic"].default_value = 0.7
                    else:
                        if MaterialIn(Metal, material):
                            PBSDF.inputs["Metallic"].default_value = 0.0

                    if MaterialIn(Reflective, material):
                        PBSDF.inputs["Roughness"].default_value = 0.1

                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            image_texture_node = material.node_tree.nodes[node.name]
                        if node.type == "BUMP":
                            bump_node = material.node_tree.nodes[node.name]

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
            else:
                raise ValueError("Материал на одном из слоёв не существует, код ошибки: 002")
            
        selected_object.data.update()
#
        
# TODO:
    # Upgrade World - Сделать так чтобы выбирались определённые фейсы у мира > они отделялись от него в отдельный объект > Как-то группировались > Производилась замена этих объектов на риги (Сундук)
    # Texture logic - Сделать использование текстур из папки, например из папки tex или из папки майнкрафта
    # Upgrade World - Сщединённое стекло: Импортировать текстуры соединённого > Выбираются фейсы с материалом стекла > Математически вычислить находятся ли стёкла рядом (if Glass.location.x + 1: поставить сообтветствующую текстуру стекла)