from ..Data import *
from ..MIB_API import *
from ..Utils.Absolute_Solver import Absolute_Solver

def Camera_Culling(obj, OProperties, geonodes_modifier):

    if OProperties.camera_culling_type == 'Vector':
        if bpy.app.version >= (4,1,0):
            geonodes_modifier["Socket_17"] = 0
        else:
            geonodes_modifier["Socket_17"] = True

        geonodes_modifier["Socket_21"] = OProperties.threshold
        geonodes_modifier["Socket_20"] = OProperties.backface_culling
        #geonodes_modifier["Input_2"] = 0.9/(bpy.context.scene.camera.data.angle/2)

    else:
        if bpy.app.version >= (4,1,0):
            geonodes_modifier["Socket_17"] = 1
        else:
            geonodes_modifier["Socket_17"] = False

        if bpy.app.version >= (4,1,0):
            geonodes_modifier["Socket_23"] = OProperties.culling_distance
        else:
            geonodes_modifier["Socket_24"] = OProperties.culling_distance

        if OProperties.predict_fov == True:
            max_fov = 0.0
            current_frame = bpy.context.scene.frame_current

            for frame in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1):
                bpy.context.scene.frame_set(frame)
                active_camera = bpy.context.scene.camera
                if active_camera and active_camera.data.angle > max_fov:
                    max_fov = active_camera.data.angle

            bpy.context.scene.frame_set(current_frame)

            geonodes_modifier["Socket_5"] = OProperties.scale * (max_fov*1.6)
        else:
            geonodes_modifier["Socket_5"] = OProperties.scale * (bpy.context.scene.camera.data.angle*1.6)
            
        geonodes_modifier["Socket_6"] = OProperties.merge_distance
        geonodes_modifier["Socket_10"] = OProperties.backface_culling
        geonodes_modifier["Socket_11"] = OProperties.merge_by_distance
        geonodes_modifier["Socket_12"] = OProperties.backface_culling_distance

        if OProperties.culling_mode == 'Simplify Faces':
            if bpy.app.version >= (4,1,0):
                geonodes_modifier["Socket_13"] = 1
            else:
                geonodes_modifier["Socket_13"] = True
        else:
            if bpy.app.version >= (4,1,0):
                geonodes_modifier["Socket_13"] = 0
            else:
                geonodes_modifier["Socket_13"] = False

    if bpy.app.version < (4, 1, 0):
        geonodes_modifier["Socket_23"] = bpy.context.scene.camera
    
def Optimize():
    selected_objects = bpy.context.selected_objects
    OProperties = bpy.context.scene.optimizationproperties
    if OProperties.use_camera_culling == True:
        if bpy.context.scene.camera != None:
            script_directory = os.path.dirname(os.path.realpath(__file__))

            geonodes_modifier = None

            if bpy.app.version >= (4, 1, 0):
                if "Universal Camera Culling" not in bpy.data.node_groups:
                    try:
                        with bpy.data.libraries.load(os.path.join(script_directory, "Universal Camera Culling 4.1.blend"), link=False) as (data_from, data_to):
                            data_to.node_groups = ["Universal Camera Culling"]
                    except:
                        Absolute_Solver('004', "Universal Camera Culling 4.1", traceback.format_exc())
            else:
                if "Universal Camera Culling" not in bpy.data.node_groups:
                    try:
                        with bpy.data.libraries.load(os.path.join(script_directory, "Universal Camera Culling 4.0.blend"), link=False) as (data_from, data_to):
                            data_to.node_groups = ["Universal Camera Culling"]
                    except:
                        Absolute_Solver('004', "Universal Camera Culling 4.0", traceback.format_exc())
            
            for obj in selected_objects:
                if obj.modifiers.get("Universal Camera Culling") == None: 
                    geonodes_modifier = obj.modifiers.new('Universal Camera Culling', type='NODES')
                    geonodes_modifier.node_group = bpy.data.node_groups.get("Universal Camera Culling")
                else:
                    geonodes_modifier = obj.modifiers.get("Universal Camera Culling")

                Camera_Culling(obj, OProperties, geonodes_modifier)

                obj.data.update()
        else:
            Absolute_Solver("None", error_name="Scene Camera Doesn't Exist", description="There is no camera in the scene")
    else:
        for obj in selected_objects:
            if obj.modifiers.get("Universal Camera Culling") != None:
                obj.modifiers.remove(obj.modifiers['Universal Camera Culling'])