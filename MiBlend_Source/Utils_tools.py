import bpy
import os
from .MIB_API import *

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
            Absolute_Solver("None", obj, error_name="Object Has No Vertext Groups", 
                description='Object "{Data.name}" has type {Data.type}, this type has no vertex groups')
        
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