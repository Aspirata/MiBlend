import bpy
import os
from ..Data import *


def Camera_Culling(obj, OProperties):
    if OProperties.camera_culling_type == False:

        if obj.modifiers.get("Raycast Camera Culling") != None: 
            obj.modifier_remove(modifier="Raycast Camera Culling")

        if obj.modifiers.get("Camera Culling") == None: 
            geonodes_modifier = obj.modifiers.new('Camera Culling', type='NODES')
            geonodes_modifier.node_group = bpy.data.node_groups.get("Camera Culling")
        else:
            geonodes_modifier = obj.modifiers.get("Camera Culling")
        
        geonodes_modifier["Input_2"] = OProperties.threshold
        geonodes_modifier["Input_3"] = bpy.context.scene.camera
        geonodes_modifier["Input_4"] = OProperties.backface_culling
        #geonodes_modifier["Input_2"] = 0.9/(bpy.context.scene.camera.data.angle/2)

    else:
        if obj.modifiers.get("Camera Culling") != None: 
            obj.modifier_remove(modifier="Camera Culling")

        if obj.modifiers.get("Raycast Camera Culling") == None: 
            geonodes_modifier = obj.modifiers.new('Raycast Camera Culling', type='NODES')
            geonodes_modifier.node_group = bpy.data.node_groups.get("Raycast Camera Culling")
        else:
            geonodes_modifier = obj.modifiers.get("Raycast Camera Culling")
        
        geonodes_modifier["Socket_5"] = OProperties.scale * (bpy.context.scene.camera.data.angle*1.5)
        geonodes_modifier["Socket_6"] = OProperties.merge_distance
        geonodes_modifier["Socket_10"] = OProperties.backface_culling
        geonodes_modifier["Socket_11"] = OProperties.merge_by_distance
        geonodes_modifier["Socket_12"] = OProperties.backface_culling_distance

    
def Optimize():
    selected_objects = bpy.context.selected_objects
    scene = bpy.context.scene
    OProperties = bpy.context.scene.optimizationproperties
    if OProperties.use_camera_culling == True:
        script_directory = os.path.dirname(os.path.realpath(__file__))
        
        if "Camera Culling" not in bpy.data.node_groups:
            if OProperties.camera_culling_type == False:
                blend_file_path = os.path.join(script_directory, "Camera Culling.blend")
                try:
                    with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
                        data_to.node_groups = ["Camera Culling"]
                except:
                    CEH('004')
            else:
                blend_file_path = os.path.join(script_directory, "Raycast Camera Culling.blend")
                try:
                    with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
                        data_to.node_groups = ["Raycast Camera Culling"]
                except:
                    CEH('004')

        for obj in selected_objects:
            Camera_Culling(obj, OProperties)
            obj.data.update()

    if scene.optimizationproperties.set_render_settings == True and scene.render.engine == 'CYCLES':
        scene.cycles.use_preview_adaptive_sampling = True
        scene.cycles.preview_adaptive_threshold = 0.1
        scene.cycles.preview_samples = 128
        scene.cycles.preview_adaptive_min_samples = 0

        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = 0.01
        scene.cycles.samples = 128
        scene.cycles.adaptive_min_samples = 40
        scene.cycles.use_denoising = True
        scene.cycles.denoiser = 'OPENIMAGEDENOISE'
        scene.render.use_persistent_data = True