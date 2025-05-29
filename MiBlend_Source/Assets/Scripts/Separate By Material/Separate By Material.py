import bpy

def separate_by_material(obj):
    material_name = properties.get("Material Name")

    obj_name = obj.name

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.select_all(action='DESELECT')

    if len(obj.material_slots) <= 1 or not obj.material_slots:
        return

    if material_name != "":
        material = bpy.data.materials.get(material_name)
        if bpy.data.collections.get(obj_name.split('__')[0].replace("Main | ", "")) is None:
            new_collection = bpy.data.collections.new(obj_name.split("__")[0].replace("Main | ", ""))
            obj.users_collection[-1].children.link(new_collection)

            for col in obj.users_collection:
                col.objects.unlink(obj)

            new_collection.objects.link(obj)

        for i, mat in enumerate(obj.data.materials):
            if mat == material:
                bpy.context.object.active_material_index = i
                break

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.material_slot_select()
        bpy.ops.mesh.separate(type="SELECTED")
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = bpy.context.view_layer.objects.get(obj_name)
        if not obj.name.startswith("Main | "):
            obj.name = f"Main | {obj_name}"
        bpy.ops.object.material_slot_remove()
        new_obj = bpy.context.selected_objects[-1]
        bpy.context.view_layer.objects.active = new_obj
        bpy.ops.object.material_slot_remove_unused()
        new_obj.name = f"{material.name} | {obj_name.replace('Main | ', '')}"
    else:
        new_collection = bpy.data.collections.new(obj_name.split("__")[0].replace("Main | ", ""))
        obj.users_collection[-1].children.link(new_collection)

        for col in obj.users_collection:
            col.objects.unlink(obj)

        new_collection.objects.link(obj)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.separate(type="MATERIAL")
        bpy.ops.object.mode_set(mode='OBJECT')

        for new_obj in new_collection.objects:
            if new_obj in bpy.context.selected_objects and obj_name in new_obj.name:
                new_obj.name = f"{new_obj.material_slots[0].material.name} | {obj_name.replace('Main | ', '')}"

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.update()

obj = bpy.context.active_object
separate_by_material(obj)
