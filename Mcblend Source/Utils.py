import bpy
import os
from .Data import *

def CShadows(UProperties):
    if bpy.context.scene.utilsproperties.cshadowsselection == 'Only Selected Light Sources':
        for obj in bpy.context.selected_objects:
            if hasattr(obj.data, 'use_contact_shadow'):
                obj.data.use_contact_shadow = True
                obj.data.contact_shadow_distance = UProperties.distance
                obj.data.contact_shadow_bias = UProperties.bias
                obj.data.contact_shadow_thickness = UProperties.thickness
    else:
        for obj in bpy.context.scene.objects:
            if hasattr(obj.data, 'use_contact_shadow'):
                obj.data.use_contact_shadow = True
                obj.data.contact_shadow_distance = UProperties.distance
                obj.data.contact_shadow_bias = UProperties.bias
                obj.data.contact_shadow_thickness = UProperties.thickness


def VertexRiggingTool():
    selected_objects = bpy.context.selected_objects
    
    vertex_group_name = bpy.context.scene.utilsproperties.vertex_group_name
    
    for obj in selected_objects:
        if obj.type == "MESH":

            armature_modifier = None
            lattice_modifier = None

            for vertex_group in obj.vertex_groups:
                if vertex_group_name in vertex_group.name:
                    obj.vertex_groups.remove(vertex_group)
            
            vertex_group = obj.vertex_groups.new(name=vertex_group_name)
            
            vertex_group.add(range(len(obj.data.vertices)), 1.0, 'REPLACE')

            if bpy.context.scene.utilsproperties.lattice:
                for modifier in obj.modifiers:
                    if modifier.type == 'LATTICE':
                        lattice_modifier = modifier

                if lattice_modifier == None:
                    lattice_modifier =  obj.modifiers.new(type='LATTICE', name="Lattice")
                
                lattice_modifier.object = bpy.context.scene.utilsproperties.lattice
            else:
                for modifier in obj.modifiers:
                    if modifier.type == 'LATTICE':
                        obj.modifiers.remove(modifier)

            if bpy.context.scene.utilsproperties.armature:
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE':
                        armature_modifier = modifier

                if armature_modifier == None:
                    armature_modifier =  obj.modifiers.new(type='ARMATURE', name="Armature")

                armature_modifier.object = bpy.context.scene.utilsproperties.armature
            else:
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE':
                        obj.modifiers.remove(modifier)
        else:
            CEH("007", obj)

def Enchant():
    for selected_object in bpy.context.selected_objects:
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                if material != None:
                    node_group = None
                    PBSDF = None

                    for node in material.node_tree.nodes:
                        if node.type == 'GROUP':
                            if "Enchantment" in node.node_tree.name:
                                node_group = node

                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node

                    if node_group == None:
                        if "Enchantment" not in bpy.data.node_groups:
                            try:
                                with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                                    data_to.node_groups = ["Enchantment"]
                            except:
                                CEH("004")

                        node_group = material.node_tree.nodes.new(type='ShaderNodeGroup')
                        node_group.node_tree = bpy.data.node_groups["Enchantment"]
                        node_group.location = (PBSDF.location.x - 200, PBSDF.location.y - 280)

                    for node in material.node_tree.nodes:
                        if node.type == "BSDF_PRINCIPLED":
                            for link in node.inputs["Emission Strength"].links:                                            
                                if link.from_node.name != node_group.name:                                                
                                    for output in link.from_node.outputs:
                                        for link_out in output.links:
                                            if link_out.to_socket.node.name == node.name:                                                                                                                    
                                                material.node_tree.links.new(link_out.from_socket, node_group.inputs["Multiply"]) 
                                                break
                            
                            if blender_version("4.x.x"):
                                for link in node.inputs["Emission Color"].links:                                            
                                    if link.from_node.name != node_group.name:                                                
                                        for output in link.from_node.outputs:
                                            for link_out in output.links:
                                                if link_out.to_socket.node.name == node.name:                                                                                                                    
                                                    material.node_tree.links.new(link_out.from_socket, node_group.inputs["Multiply Color"]) 
                                                    break
                            else:
                                for link in node.inputs["Emission"].links:                                            
                                    if link.from_node.name != node_group.name:                                                
                                        for output in link.from_node.outputs:
                                            for link_out in output.links:
                                                if link_out.to_socket.node.name == node.name:                                                                                                                    
                                                    material.node_tree.links.new(link_out.from_socket, node_group.inputs["Multiply Color"]) 
                                                    break

                    if blender_version("4.x.x"):                        
                        material.node_tree.links.new(node_group.outputs[0], PBSDF.inputs["Emission Color"])
                    else:
                        material.node_tree.links.new(node_group.outputs[0], PBSDF.inputs["Emission"])
                    
                    material.node_tree.links.new(node_group.outputs[1], PBSDF.inputs["Emission Strength"])
                    node_group.inputs["Divider"].default_value = bpy.context.scene.render.fps/30 * bpy.context.scene.utilsproperties.divider
                    node_group.inputs["Camera Strenght"].default_value = bpy.context.scene.utilsproperties.camera_strenght
                    node_group.inputs["Non-Camera Strenght"].default_value = bpy.context.scene.utilsproperties.non_camera_strenght
                else:
                    CEH("m002")
        else:
            CEH("m003")
        
def SetRenderSettings(current_preset):
    for setting_name, value in Render_Settings[current_preset].items():
        property_names = setting_name.split('.')
        target = bpy.context.scene
        for sub_property in property_names[:-1]: 
            target = getattr(target, sub_property)
        property_name = property_names[-1] 
        try:
            setattr(target, property_name, value)
        except:
            raise ValueError(f"Error occurred in setting {setting_name}")
