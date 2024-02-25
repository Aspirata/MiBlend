import bpy
import os
def CShadows():
    if bpy.context.scene.cshadowsselection == 'Only Selected Objects':
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
        for material in selected_object.data.materials:
            DBSDF = None
            MixShader = None
            TBSDF = None
            PBSDF = None

            for node in material.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    Texture = node

                if node.name == "Diffuse BSDF":
                    DBSDF = node

                if node.name == "Mix Shader":
                    MixShader = node

                if node.name == "Transparent BSDF":
                    TBSDF = node

                if node.name == "Principled BSDF":
                    PBSDF = node

                if node.name == "Material Output":
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

def FixAutoSmooth():
    for selected_object in bpy.context.selected_objects:
        AutoSmoothed = False
        if bpy.app.version < (4, 1, 0):
            if selected_object.type == 'MESH':
                for modifier in selected_object.modifiers:
                    if modifier.type == 'NODES' and modifier.node_group == bpy.data.node_groups.get("Auto Smooth"):
                        AutoSmoothed = True
                        SmoothD = modifier["Socket_1"]

                if AutoSmoothed == True:
                    selected_object.data.use_auto_smooth = True
                    selected_object.data.auto_smooth_angle= SmoothD
        else:
            if selected_object.modifiers.get("Smooth by Angle") != None: 
                return
            #selected_object.modifier_add(type='SUBSURF')