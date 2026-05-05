import os
import traceback
import bpy
from ...mib_utils import perf_time, GetConnectedSocketTo, create_node_group
from ...resources.data import resources_directory, nodes_file
from ..absolute_solver.absolute_solver_logic import trigger_absolute_solver


WORLD_MATERIAL_NAME = "MiBlend World"
CLOUDS_NODE_TREE_NAME = "Clouds Generator 2"
FOG_NODE_TREE_NAME = "Fog"


@perf_time
def recreate_env(self):
    scene = bpy.context.scene
    world = scene.world

    # Sky
    if self.reset_settings:
        world_material = bpy.context.scene.world.node_tree
        group = bpy.data.node_groups["MiBlend Sky"]

        for node in world_material.nodes:
            if node.type == 'GROUP' and "MiBlend Sky" in node.node_tree.name:
                for socket in node.inputs:
                    try:
                        for i, vector_value in enumerate(socket.default_value, 1):
                            vector_value = group.interface.items_tree[socket.name].default_value[i]
                    except Exception:
                        socket.default_value = group.interface.items_tree[socket.name].default_value

    if self.create_sky == 'Recreate Sky':
        if world == bpy.data.worlds.get(WORLD_MATERIAL_NAME) and bpy.data.worlds.get(WORLD_MATERIAL_NAME) is not None:
            bpy.data.worlds.remove(bpy.data.worlds.get(WORLD_MATERIAL_NAME), do_unlink=True)
        
        for group in bpy.data.node_groups:
            if "MiBlend" in group.name:
                bpy.data.node_groups.remove(group)

        create_env("Sky")

    elif self.create_sky == 'Create Sky' and WORLD_MATERIAL_NAME in bpy.data.worlds:
        bpy.context.scene.world = bpy.data.worlds.get(WORLD_MATERIAL_NAME)

    # Fog
    if self.create_fog == 'Recreate Fog':
        for obj in scene.objects:
            if obj.get("MiBlend ID") == "Fog":
                bpy.data.objects.remove(obj, do_unlink=True)

        if FOG_NODE_TREE_NAME in bpy.data.node_groups:
            bpy.data.node_groups.remove(bpy.data.node_groups.get(FOG_NODE_TREE_NAME))

        if "Fog" in bpy.data.materials:
            bpy.data.materials.remove(bpy.data.materials.get("Fog"))

        create_env("Fog")

    elif self.create_fog == 'Create Fog':
        
        if "Fog" in bpy.data.materials:
            bpy.data.materials["Fog"]

        if FOG_NODE_TREE_NAME in bpy.data.node_groups:
            if not any(obj.get("MiBlend ID") == "Fog" for obj in scene.objects):
                bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
                bpy.context.object.name = "Clouds"
                bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
                geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
                geonodes_modifier.node_group = bpy.data.node_groups.get(CLOUDS_NODE_TREE_NAME)

            bpy.context.object["MiBlend ID"] = "Clouds"

    # Clouds
    if self.create_clouds == 'Recreate Clouds':
        for obj in scene.objects:
            if obj.get("MiBlend ID") == "Clouds":
                bpy.data.objects.remove(obj, do_unlink=True)

        if CLOUDS_NODE_TREE_NAME in bpy.data.node_groups:
            bpy.data.node_groups.remove(bpy.data.node_groups.get(CLOUDS_NODE_TREE_NAME))

        if "Clouds" in bpy.data.materials:
            bpy.data.materials.remove(bpy.data.materials.get("Clouds"))
        
        create_env("Clouds")
    
    elif self.create_clouds == 'Create Clouds':
        
        if "Clouds" in bpy.data.materials:
            bpy.data.materials["Clouds"]

        if CLOUDS_NODE_TREE_NAME in bpy.data.node_groups:
            if not any(obj.get("MiBlend ID") == "Clouds" for obj in scene.objects):
                bpy.ops.mesh.primitive_plane_add(size=50.0, enter_editmode=False, align='WORLD', location=(0, 0, 100))
                bpy.context.object.name = "Clouds"
                bpy.context.object.data.materials.append(bpy.data.materials.get("Clouds"))
                geonodes_modifier = bpy.context.object.modifiers.new('Clouds Generator', type='NODES')
                geonodes_modifier.node_group = bpy.data.node_groups.get(CLOUDS_NODE_TREE_NAME)

            bpy.context.object["MiBlend ID"] = "Clouds"


@perf_time
def create_env(mode=None):
    scene = bpy.context.scene
    MIB_env_collection = bpy.data.collections.get("MiBlend Environment", None)
    clouds_path = os.path.join(resources_directory, "Clouds Generator.blend")
    world = scene.world
    sky_exists = False
    fog_exists = False
    clouds_exists = False

    if any(obj.get("MiBlend ID") == "Clouds" for obj in scene.objects):
        clouds_exists = True
    
    if any(obj.get("MiBlend ID") == "Fog" for obj in scene.objects):
        fog_exists = True

    if world is not None and "MiBlend Sky" in bpy.data.node_groups:
        if WORLD_MATERIAL_NAME in bpy.data.worlds:
            sky_exists = True
    
    if (clouds_exists or sky_exists or fog_exists) and mode is None:
        bpy.ops.miblend.recreate_env('INVOKE_DEFAULT')

    else:
        # Create Sky
        if (scene.miblend_properties.environment_properties.create_sky and mode is None) or mode == "Sky":
            if not os.path.exists(nodes_file):
                trigger_absolute_solver("e03", traceback.format_exc(), "Nodes.blend")

            if WORLD_MATERIAL_NAME not in bpy.data.worlds:
                with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                    data_to.worlds = [WORLD_MATERIAL_NAME]
                appended_world_material = bpy.data.worlds.get(WORLD_MATERIAL_NAME)
            else:
                appended_world_material = bpy.data.worlds[WORLD_MATERIAL_NAME]
            bpy.context.scene.world = appended_world_material

        # Create Fog
        if (scene.miblend_properties.environment_properties.create_fog and mode is None) or mode == "Fog":
    
            if not MIB_env_collection:
                MIB_env_collection = bpy.data.collections.new("MiBlend Environment")
                bpy.context.scene.collection.children.link(MIB_env_collection)

            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_cube_add(size=1.0, enter_editmode=False, align='WORLD', location=(0, 0, 50))
            fog_cube = bpy.context.active_object

            for collection in fog_cube.users_collection:
                collection.objects.unlink(fog_cube)
            MIB_env_collection.objects.link(fog_cube)

            fog_cube.name = "Fog"
            #fog_cube.display_type = "BOUNDS"
            fog_cube.scale = (500, 500, 75)

            fog_material = bpy.data.materials.new(name="Fog")
            fog_material.use_nodes = True
            fog_cube.data.materials.append(fog_material)

            output_node = [node for node in fog_material.node_tree.nodes if node.type == "OUTPUT_MATERIAL"][0]
            fog_material.node_tree.nodes.remove(GetConnectedSocketTo(0, output_node).node)
            fog_node = create_node_group(fog_material, FOG_NODE_TREE_NAME, (output_node.location.x - 200, output_node.location.y))
            fog_material.node_tree.links.new(fog_node.outputs[0], output_node.inputs["Volume"])

            bpy.context.scene.eevee.volumetric_end = fog_node.inputs["Max Distance"].default_value + 400.0
    
            bpy.context.object["MiBlend ID"] = "Fog"

            bpy.ops.object.select_all(action='DESELECT')

        # Create Clouds
        if (scene.miblend_properties.environment_properties.create_clouds and mode is None) or mode == "Clouds":
            if not os.path.exists(clouds_path):
                trigger_absolute_solver("e03", traceback.format_exc(),  "Clouds Generator.blend")

            if CLOUDS_NODE_TREE_NAME not in bpy.data.node_groups:
                with bpy.data.libraries.load(clouds_path, link=False) as (data_from, data_to):
                    data_to.node_groups = [CLOUDS_NODE_TREE_NAME]
            else:
                bpy.data.node_groups[CLOUDS_NODE_TREE_NAME]
    
            if "Clouds" not in bpy.data.materials:
                with bpy.data.libraries.load(clouds_path, link=False) as (data_from, data_to):
                    data_to.materials = ["Clouds"]
            else:
                bpy.data.materials["Clouds"]

            if not MIB_env_collection:
                MIB_env_collection = bpy.data.collections.new("MiBlend Environment")
                bpy.context.scene.collection.children.link(MIB_env_collection)

            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_plane_add(size=1.0, enter_editmode=False, align='WORLD', location=(0, 0, 500))
            clouds_obj = bpy.context.active_object

            for collection in clouds_obj.users_collection:
                collection.objects.unlink(clouds_obj)
            MIB_env_collection.objects.link(clouds_obj)

            clouds_obj.name = "Clouds"
            clouds_obj.scale = (400, 400, 1)
            clouds_obj.data.materials.append(bpy.data.materials.get("Clouds"))
            geonodes_modifier = clouds_obj.modifiers.new('Clouds Generator', type='NODES')
            geonodes_modifier.node_group = bpy.data.node_groups.get(CLOUDS_NODE_TREE_NAME)

            clouds_obj["MiBlend ID"] = "Clouds"

            bpy.ops.object.select_all(action='DESELECT')