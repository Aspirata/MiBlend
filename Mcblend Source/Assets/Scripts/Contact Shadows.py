
import bpy

UAS_API = {

    "Properties": {

        "distance": {
            "Type": "FloatProperty",
            "Name": "Distance",
            "Default": 0.2,
            "Min": 0.0,
            "Max": 100000.0
        }
    }
}

distance = 0.2

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