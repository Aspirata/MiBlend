import bpy

texture_nodes = [node for node in bpy.data.materials["glass"].node_tree.nodes if node.type == "TEX_IMAGE"]
image_to_nodes = {}

for node in texture_nodes:
    image = node.image
    if image is not None:
        if image in image_to_nodes:
            image_to_nodes[image].append(node)
        else:
            image_to_nodes[image] = [node]

def get_node_suffix_number(node_name):
    parts = node_name.split(".")
    if len(parts) > 1 and parts[-1].isdigit():
        return int(parts[-1])
    return 0

for image, nodes in image_to_nodes.items():
    if len(nodes) > 1:
        nodes.sort(key=lambda node: ('.' in node.name, get_node_suffix_number(node.name)))
        
        node_to_keep = nodes[0]
        nodes_to_remove = nodes[1:]

        for node in nodes_to_remove:
            output_number = -1
            for output in node.outputs:
                output_number += 1
                for link in output.links:
                    bpy.data.materials["glass"].node_tree.links.new(node_to_keep.outputs[output_number], link.to_socket)
            
            bpy.data.materials["glass"].node_tree.nodes.remove(node)

print("Remaining nodes:")
for node in bpy.data.materials["glass"].node_tree.nodes:
    if node.type == "TEX_IMAGE":
        print(node.name, node.image)
