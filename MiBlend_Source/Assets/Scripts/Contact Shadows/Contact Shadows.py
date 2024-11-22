import bpy

only_selected_objects = properties.get("Only Selected Objects", False)
distance = clamp(0, properties.get("Distance", 0.2), 9999)
bias = clamp(0.001, properties.get("Bias", 0.03), 5.0)
thickness = clamp(0, properties.get("Thickness", 0.01), 100)

if only_selected_objects:
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