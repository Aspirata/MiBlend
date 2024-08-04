import bpy

UAS_API = {

    "Properties": {

        "distance": {
            "Type": "FloatProperty",
            "Name": "Distance",
            "Default": 0.2
        }
    }
}

mode = 1
distance = 0.2
bias = 0.03
thickness = 0.01

if mode == 0:
    for obj in bpy.context.selected_objects:
        try:
            obj.data.use_contact_shadow = True
            obj.data.contact_shadow_distance = distance
            obj.data.contact_shadow_bias = bias
            obj.data.contact_shadow_thickness = thickness
        except:
            pass
else:
    for obj in bpy.context.scene.objects:
        try:
            obj.data.use_contact_shadow = True
            obj.data.contact_shadow_distance = distance
            obj.data.contact_shadow_bias = bias
            obj.data.contact_shadow_thickness = thickness
        except:
            pass