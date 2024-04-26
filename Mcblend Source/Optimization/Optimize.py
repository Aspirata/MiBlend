from ..Data import *

def Camera_Culling(obj, OProperties, geonodes_modifier):
    mat_excuder = None

    if OProperties.camera_culling_type == 'Vector':
        if blender_version("4.1.x"):
            geonodes_modifier["Socket_17"] = 0
        else:
            geonodes_modifier["Socket_17"] = True

        geonodes_modifier["Socket_21"] = OProperties.threshold
        geonodes_modifier["Socket_20"] = OProperties.backface_culling
        #geonodes_modifier["Input_2"] = 0.9/(bpy.context.scene.camera.data.angle/2)

    else:
        if blender_version("4.1.x"):
            geonodes_modifier["Socket_17"] = 1
        else:
            geonodes_modifier["Socket_17"] = False

        if blender_version("4.1.x"):
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
            if blender_version("4.1.x"):
                geonodes_modifier["Socket_13"] = 1
            else:
                geonodes_modifier["Socket_13"] = True
        else:
            if blender_version("4.1.x"):
                geonodes_modifier["Socket_13"] = 0
            else:
                geonodes_modifier["Socket_13"] = False
        
        #if OProperties.Exclude_Materials:
            #for node in node_group:
                #if node.type == "GROUP":
                    #if "Material Excluder" in node.node_tree.name:
                        #mat_excuder = node
                        #break

            #if mat_excuder == None:
                #Create new Node Group with name "Material Excluder"

            #Set Settings
                    #Add Materials to exclude

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
                        CEH('004')
            else:
                if "Universal Camera Culling" not in bpy.data.node_groups:
                    try:
                        with bpy.data.libraries.load(os.path.join(script_directory, "Universal Camera Culling 4.0.blend"), link=False) as (data_from, data_to):
                            data_to.node_groups = ["Universal Camera Culling"]
                    except:
                        CEH('004')
            
            for obj in selected_objects:
                if obj.modifiers.get("Universal Camera Culling") == None: 
                    geonodes_modifier = obj.modifiers.new('Universal Camera Culling', type='NODES')
                    geonodes_modifier.node_group = bpy.data.node_groups.get("Universal Camera Culling")
                else:
                    geonodes_modifier = obj.modifiers.get("Universal Camera Culling")

                Camera_Culling(obj, OProperties, geonodes_modifier)

                obj.data.update()
        else:
            CEH("006")
    else:
        for obj in selected_objects:
            if obj.modifiers.get("Universal Camera Culling") != None:
                obj.modifiers.remove(obj.modifiers['Universal Camera Culling'])