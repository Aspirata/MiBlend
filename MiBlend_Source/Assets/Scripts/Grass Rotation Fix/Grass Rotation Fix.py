import bpy, bmesh
from mathutils import Vector, Matrix
from math import atan2, radians, degrees

direction = properties.get("Direction X/Y")
texture_name = properties.get("Texture Name").split()

for selected_object in bpy.context.selected_objects:
    if selected_object.type != 'MESH':
        continue

    bpy.ops.object.mode_set(mode='EDIT')
    mesh = bmesh.from_edit_mesh(selected_object.data)

    uv_layer = mesh.loops.layers.uv.active
    if not uv_layer:
        bpy.ops.object.mode_set(mode='OBJECT')
        continue
    
    for material in selected_object.data.materials:
        if material is None or not material.use_nodes:
            continue

        pbsdf_node = next((node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
        if not pbsdf_node:
            continue

        image_texture_node = detect_texture_node(pbsdf_node)

        if not image_texture_node:
            continue

        texture_parts = format_texture_name(image_texture_node.image.name)
        if not all(part in texture_parts for part in texture_name):
            continue

        threshold = 0.001
        filtered_faces = filter(lambda x: x.material_index < len(selected_object.data.materials) and selected_object.data.materials[x.material_index] == material, mesh.faces)

        for face in filtered_faces:
            center = sum((loop[uv_layer].uv for loop in face.loops), Vector((0, 0))) / len(face.loops)
            tangent = face.loops[1][uv_layer].uv - face.loops[0][uv_layer].uv
            if tangent.length_squared <= 0:
                continue
            tangent.normalize()

            target_vector = Vector((1.0, 0.0)) if direction else Vector((0.0, 1.0))
            
            current_angle = degrees(atan2(tangent.y, tangent.x))
            target_angle = degrees(atan2(target_vector.y, target_vector.x))
            
            angle_diff = (target_angle - current_angle) % 180
            if angle_diff > 90:
                angle_diff -= 180
            
            if abs(angle_diff) > threshold:
                align_matrix = Matrix.Rotation(radians(-angle_diff), 2)
                for loop in face.loops:
                    uv = loop[uv_layer].uv
                    uv -= center
                    uv = uv @ align_matrix
                    uv += center
                    loop[uv_layer].uv = uv
        
        bmesh.update_edit_mesh(selected_object.data, loop_triangles=False, destructive=True)
        if bpy.context.area:
            bpy.context.area.tag_redraw()
        bpy.ops.object.mode_set(mode='OBJECT')
        break
