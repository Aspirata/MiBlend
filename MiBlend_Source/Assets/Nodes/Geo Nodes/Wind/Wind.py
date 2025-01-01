import bpy

windy_objects = []
for selected_object in bpy.context.selected_objects:
    if selected_object.type == "MESH":
        if len(selected_object.data.materials) > 1 and properties.get("Auto Detect"):
            materials_to_separate = [material for material in selected_object.data.materials if material and any(part in format_material_name(material.name) for part in properties.get("Materials", "").split()) and 
                                     all(part not in format_material_name(material.name) for part in ("side", "snow", "mushroom", "top"))]
            for material in materials_to_separate:
                windy_objects.append(SeparateMeshByMaterial(selected_object, material))

        elif len(selected_object.data.materials) == 1 and (material := selected_object.data.materials[0]):
            materials = properties.get("Materials", "").split()
            formated_material_name = format_material_name(material.name)

            if any(part in formated_material_name for part in materials) and all(part not in formated_material_name for part in ("side", "snow", "mushroom", "top")): 
                windy_objects.append(selected_object)

for windy_object in windy_objects:
    geonodes_modifier = None
    for modifier in windy_object.modifiers:
        if modifier.type == "NODES":
            if modifier.node_group.name == "Wind":
                geonodes_modifier = modifier
                break
    
    if geonodes_modifier is None:
        geonodes_modifier = windy_object.modifiers.new("Wind", type='NODES')
        geonodes_modifier.node_group = bpy.data.node_groups.get("Wind")

    geonodes_modifier["Socket_9"] = properties.get("Speed")
    geonodes_modifier["Socket_21"] = properties.get("Optimize Mode")