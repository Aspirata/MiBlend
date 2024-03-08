import bpy
import os
from .Data import *

def CShadows():
    if bpy.context.scene.utilsproperties.cshadowsselection == 'Only Selected Objects':
        for obj in bpy.context.selected_objects:
            if hasattr(obj.data, 'use_contact_shadow'):
                obj.data.use_contact_shadow = True
                obj.data.contact_shadow_thickness = 0.01
    else:
        for obj in bpy.context.scene.objects:
            if hasattr(obj.data, 'use_contact_shadow'):
                obj.data.use_contact_shadow = True
                obj.data.contact_shadow_thickness = 0.01

def sleep_after_render(dummy):
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    
def sleep_detector():
    bpy.app.handlers.render_complete.append(sleep_after_render)


def VertexRiggingTool():
    selected_objects = bpy.context.selected_objects

    vertex_group_name = bpy.context.scene.utilsproperties.vertex_group_name

    for obj in selected_objects:
        for vertex_group in obj.vertex_groups:
            if vertex_group.name == vertex_group_name:
                obj.vertex_groups.remove(vertex_group)
        
        vertex_group = obj.vertex_groups.new(name=vertex_group_name)
        
        vertex_group.add(range(len(obj.data.vertices)), 1.0, 'REPLACE')

def ConvertDBSDF2PBSDF():
    for selected_object in bpy.context.selected_objects:
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                if material != None:
                    DBSDF = None
                    MixShader = None
                    TBSDF = None
                    PBSDF = None
                    Output = None
                    Texture = None

                    for node in material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            Texture = node

                        if node.type == "BSDF_DIFFUSE":
                            DBSDF = node

                        if node.type == "MIX_SHADER":
                            MixShader = node

                        if node.type == "BSDF_TRANSPARENT":
                            TBSDF = node

                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node

                        if node.type == "OUTPUT_MATERIAL":
                            Output = node

                    if DBSDF != None:
                        material.node_tree.nodes.remove(DBSDF)

                    if MixShader != None:
                        material.node_tree.nodes.remove(MixShader)

                    if TBSDF != None:
                        material.node_tree.nodes.remove(TBSDF)
                    
                    if Texture != None:
                        if PBSDF == None:
                            PBSDF = material.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
                            PBSDF.location = (Output.location.x - 100, Output.location.x - 5)
                        material.node_tree.links.new(Texture.outputs["Alpha"], PBSDF.inputs[4])
                        material.node_tree.links.new(PBSDF.outputs[0], Output.inputs[0])
                        material.node_tree.links.new(Texture.outputs["Color"], PBSDF.inputs[0])
                else:
                    raise ValueError("Material doesn't exist on one of the slots, error code: m002")
        else:
            raise ValueError("Object:", selected_object.name, "has no materials, error code: m003")

def FixAutoSmooth():
    for selected_object in bpy.context.selected_objects:
        AutoSmoothed = False
        if bpy.app.version < (4, 1, 0):
            if selected_object.type == 'MESH':
                for modifier in selected_object.modifiers:
                    if modifier.type == 'NODES' and modifier.node_group == bpy.data.node_groups.get("Auto Smooth"):
                        AutoSmoothed = True
                        SmoothAngle = modifier["Socket_1"]

                if AutoSmoothed == True:
                    selected_object.data.use_auto_smooth = True
                    selected_object.data.auto_smooth_angle= SmoothAngle
        else:
            for modifier in selected_object.modifiers:
                if modifier.type == 'NODES' and modifier.node_group == bpy.data.node_groups.get("Smooth by Angle"):
                    return

            if "Smooth by Angle" not in bpy.data.node_groups:
                try:
                    with bpy.data.libraries.load(os.path.join(main_directory, "Materials", "Shade Auto Smooth.blend"), link=False) as (data_from, data_to):
                        data_to.node_groups = ["Smooth by Angle"]
                except:
                    raise ValueError(f"{os.path.basename(os.path.dirname(os.path.realpath(__file__)))} not found, error code: 004")
                    
            geonodes_modifier = selected_object.modifiers.new('Shade Auto Smooth', type='NODES')
            geonodes_modifier.node_group = bpy.data.node_groups.get("Smooth by Angle")

def Enchant():
    for selected_object in bpy.context.selected_objects:
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                if material != None:
                    node_group = None
                    PBSDF = None

                    for node in material.node_tree.nodes:
                        if node.type == 'GROUP' and "Enchantment" in node.node_tree.name:
                            node_group = node

                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node

                    if node_group == None:
                        if "Enchantment" not in bpy.data.node_groups:
                            with bpy.data.libraries.load(materials_file_path, link=False) as (data_from, data_to):
                                data_to.node_groups = ["Enchantment"]
                        else:
                            bpy.data.node_groups["Enchantment"]

                        node_group = material.node_tree.nodes.new(type='ShaderNodeGroup')
                        node_group.node_tree = bpy.data.node_groups["Enchantment"]
                        node_group.location = (PBSDF.location.x - 200, PBSDF.location.y - 280)
                        material.node_tree.links.new(node_group.outputs[0], PBSDF.inputs[26])
                        material.node_tree.links.new(node_group.outputs[1], PBSDF.inputs[27])
                        node_group.inputs["Divider"].default_value = bpy.context.scene.render.fps/30 * bpy.context.scene.utilsproperties.divider
                        node_group.inputs["Camera Strenght"].default_value = bpy.context.scene.utilsproperties.camera_strenght
                        node_group.inputs["Non-Camera Strenght"].default_value = bpy.context.scene.utilsproperties.non_camera_strenght
                    else:
                        material.node_tree.links.new(node_group.outputs[0], PBSDF.inputs[26])
                        material.node_tree.links.new(node_group.outputs[1], PBSDF.inputs[27])
                        node_group.inputs["Divider"].default_value = bpy.context.scene.render.fps/30 * bpy.context.scene.utilsproperties.divider
                        node_group.inputs["Camera Strenght"].default_value = bpy.context.scene.utilsproperties.camera_strenght
                        node_group.inputs["Non-Camera Strenght"].default_value = bpy.context.scene.utilsproperties.non_camera_strenght

                else:
                    raise ValueError("Material doesn't exist on one of the slots, error code: m002")
        else:
            raise ValueError("Object:", selected_object.name, "has no materials, error code: m003")