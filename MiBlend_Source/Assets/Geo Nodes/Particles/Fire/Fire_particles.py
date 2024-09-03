import bpy
import sys

addon_dir = os.path.dirname(os.path.abspath(__file__))
if addon_dir not in sys.path:
    sys.path.append(addon_dir)

from MCB_API import SeparateMeshBy

mode = "auto", "fast", "accurately"

for selected_object in bpy.context.selected_objects:
    if 
        if (geonodes_modifier := selected_object.modifiers.get("Fire Particles")) == None: 
            geonodes_modifier = selected_object.modifiers.new('Fire Particles', type='NODES')
            geonodes_modifier.node_group = bpy.data.node_groups.get("Fire Particles")