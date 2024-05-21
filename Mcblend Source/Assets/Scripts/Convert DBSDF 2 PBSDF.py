import bpy
    
def GetConnectedSocketTo(input, tag, material):
    for node in material.node_tree.nodes:
        if node.type == tag:
            for link in node.inputs[input].links:
                for output in link.from_node.outputs:
                    for link in output.links:
                        if link.to_socket.node.name == node.name:
                            return link.from_socket

for selected_object in bpy.context.selected_objects:
    slot = 0
    if selected_object.material_slots:
        for material in selected_object.data.materials:
            slot += 1
            if material is not None:
                DBSDF = None
                MixShader = None
                TBSDF = None
                PBSDF = None
                Output = None

                for node in material.node_tree.nodes:
                    if node.type == "BSDF_DIFFUSE":
                        DBSDF = node

                    if node.type == "MIX_SHADER":
                        MixShader = node

                    if node.type == "BSDF_TRANSPARENT":
                        TBSDF = node

                    if node.type == "BSDF_PRINCIPLED":
                        PBSDF = node

                    if node.type == "OUTPUT_MATERIAL":
                        Output = node

                if DBSDF != None:
                    if PBSDF == None:
                        PBSDF = material.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
                        PBSDF.location = (Output.location.x - 280, Output.location.y)
                        PBSDF.inputs[0].default_value = DBSDF.inputs[0].default_value
                    
                    material.node_tree.links.new(GetConnectedSocketTo(0, "BSDF_DIFFUSE", material), PBSDF.inputs["Base Color"])

                    material.node_tree.links.new(GetConnectedSocketTo(0, "MIX_SHADER", material), PBSDF.inputs["Alpha"])
                    
                    if MixShader != None:
                        material.node_tree.nodes.remove(MixShader)

                    if TBSDF != None:
                        material.node_tree.nodes.remove(TBSDF)

                    if DBSDF != None:
                        material.node_tree.nodes.remove(DBSDF)

                    material.node_tree.links.new(PBSDF.outputs[0], Output.inputs[0])
            else:
                raise ValueError(f"Material doesn't exist on slot {slot}. Error code: m002 DO NOT REPORT")
    else:
        raise ValueError(f"Object: {selected_object.name} has no materials. Error code: m003 DO NOT REPORT")