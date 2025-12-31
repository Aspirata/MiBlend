import bpy
from .Data import Render_Settings

def VertexRiggingTool(vertex_group_name=None):
    selected_objects = bpy.context.selected_objects
    
    if vertex_group_name is None:
        vertex_group_name = bpy.context.scene.miblend_properties.utils_properties.vertex_group_name
    
    for obj in selected_objects:
        if obj.type == "MESH":

            armature_modifier = None
            lattice_modifier = None

            while len(obj.vertex_groups) > 0:
                obj.vertex_groups.remove(obj.vertex_groups[0])

            vertex_group = obj.vertex_groups.new(name=vertex_group_name)
            
            vertex_group.add(range(len(obj.data.vertices)), 1.0, 'REPLACE')

            if bpy.context.scene.miblend_properties.utils_properties.lattice:
                for modifier in obj.modifiers:
                    if modifier.type == 'LATTICE':
                        lattice_modifier = modifier

                if lattice_modifier == None:
                    lattice_modifier =  obj.modifiers.new(type='LATTICE', name="Lattice")
                
                lattice_modifier.object = bpy.context.scene.miblend_properties.utils_properties.lattice
            else:
                for modifier in obj.modifiers:
                    if modifier.type == 'LATTICE':
                        obj.modifiers.remove(modifier)

            if bpy.context.scene.miblend_properties.utils_properties.armature:
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE':
                        armature_modifier = modifier

                if armature_modifier == None:
                    armature_modifier =  obj.modifiers.new(type='ARMATURE', name="Armature")

                armature_modifier.object = bpy.context.scene.miblend_properties.utils_properties.armature
            else:
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE':
                        obj.modifiers.remove(modifier)
        
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