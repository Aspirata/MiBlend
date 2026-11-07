import bpy
import traceback
from pathlib import Path
from ...mib_utils import perf_time, append_from_blend, move_to_collection
from ..absolute_solver.absolute_solver_logic import trigger_absolute_solver


class Environment:
    def __init__(self):
        self.FOG_NODE_TREE_NAME = "Fog"
        self.ENVIRONMENT_BLEND_FILE_PATH: Path = Path(__file__).parent / "MiBlend Environment v2.blend"
        self.environment_properties = bpy.context.scene.miblend_properties.environment_properties

    @perf_time
    def create_environment(self):
        if not self.environment_properties.create_clouds and not self.environment_properties.create_fog and not self.environment_properties.create_sky:
            return

        miblend_env_collection = bpy.data.collections.get("MiBlend Environment", None)
        if not miblend_env_collection:
            miblend_env_collection = bpy.data.collections.new("MiBlend Environment")
            bpy.context.scene.collection.children.link(miblend_env_collection)

        if self.environment_properties.create_sky and \
            not any(obj.get("miblend_id") in {"sky_controller", "stars_controller"} for obj in bpy.context.scene.objects) and \
            (bpy.context.scene.world is None or bpy.context.scene.world.name != "MiBlend Sky"):
            sky_world, sky_controller, sun_light_source, moon_light_source = self.create_sky(miblend_env_collection)
            self.migrate_sky(sky_world, sky_controller, sun_light_source, moon_light_source)

        if self.environment_properties.create_clouds and \
            not any(obj.get("miblend_id") == "clouds" for obj in bpy.context.scene.objects):
            clouds_obj = self.create_clouds(miblend_env_collection)
            self.migrate_clouds(clouds_obj)
        
        if self.environment_properties.create_fog and \
            not any(obj.get("miblend_id") == "fog" for obj in bpy.context.scene.objects):
            fog_obj = self.create_fog(miblend_env_collection)
            self.migrate_fog(fog_obj)

    def create_sky(self, miblend_env_collection):
        load_options = {"link": False}
        if bpy.app.version >= (5, 0, 0):
            load_options["reuse_local_id"] = True

        with bpy.data.libraries.load(str(self.ENVIRONMENT_BLEND_FILE_PATH.expanduser().resolve()), **load_options) as (_, data_to):
            data_to.worlds = ["MiBlend Sky"]
            data_to.objects = ["MiBlend Sky Controller", "MiBlend Stars Controller", "MiBlend Sky Internal Buffer", 
                                "MiBlend Sun Light Source", "MiBlend Moon Light Source"]
    
        sky_world = data_to.worlds[0] if data_to.worlds else None
        sky_controller = data_to.objects[0] if data_to.objects else None
        stars_controller = data_to.objects[1] if len(data_to.objects) > 1 else None
        sky_internal_buffer = data_to.objects[2] if len(data_to.objects) > 2 else None
        sun_light_source = data_to.objects[3] if len(data_to.objects) > 3 else None
        moon_light_source =  data_to.objects[4] if len(data_to.objects) > 4 else None

        if not sky_world or not sky_controller or not stars_controller or not sky_internal_buffer \
            or not sun_light_source or not moon_light_source:
            trigger_absolute_solver("n00", traceback.format_exc())
            return

        bpy.context.scene.world = sky_world
        move_to_collection([sky_controller, stars_controller, sky_internal_buffer, sun_light_source, moon_light_source], miblend_env_collection)
        return sky_world, sky_controller, sun_light_source, moon_light_source

    def create_clouds(self, miblend_env_collection):
        clouds_obj = append_from_blend(self.ENVIRONMENT_BLEND_FILE_PATH, "objects", "MiBlend Clouds")

        if clouds_obj is None:
            trigger_absolute_solver("n00", traceback.format_exc())
            return

        move_to_collection(clouds_obj, miblend_env_collection)
        return clouds_obj

    def create_fog(self, miblend_env_collection):
        fog_obj = append_from_blend(self.ENVIRONMENT_BLEND_FILE_PATH, "objects", "MiBlend Fog")

        if fog_obj is None:
            trigger_absolute_solver("n00", traceback.format_exc())
            return

        move_to_collection(fog_obj, miblend_env_collection)
        return fog_obj
    
    def migrate_sky(self, sky_world, sky_controller, sun_light_source, moon_light_source):
        return NotImplemented

    def migrate_clouds(self, clouds_obj):
        try:
            old_clouds_obj = next((obj for obj in bpy.data.objects if obj.get("MiBlend ID") == "Clouds"), None)
            
            clouds_obj.location.x, clouds_obj.location.y = old_clouds_obj.location.x, old_clouds_obj.location.y
            # convert location z with a scale factor
            clouds_obj.rotation_euler = old_clouds_obj.rotation_euler
            # Migrate material properties and geonode parameters
            bpy.data.objects.remove(old_clouds_obj, do_unlink=True)

        except Exception:
            trigger_absolute_solver("n00", traceback.format_exc()) # Replace with a custom error "Cannot Migrate data=Clouds"
        
    def migrate_fog(self, fog_obj):
        try:
            old_fog_obj = next((obj for obj in bpy.data.objects if obj.get("MiBlend ID") == "Fog"), None)
            old_fog_material_tree = old_fog_obj.material_slots[0].material.node_tree.nodes
            old_fog_node = next((node for node in old_fog_material_tree if node.type == 'GROUP' and "Fog" in node.node_tree.name), None)

            fog_material_tree = fog_obj.material_slots[0].material.node_tree.nodes
            fog_node = next((node for node in fog_material_tree if node.type == 'GROUP' and "Fog" in node.node_tree.name), None)
        
            fog_obj.location.x, fog_obj.location.y = old_fog_obj.location.x, old_fog_obj.location.y
            # convert location z with a scale factor
            fog_obj.rotation_euler = old_fog_obj.rotation_euler
            fog_node.inputs["Density"].default_value = old_fog_node.inputs["Density"].default_value
            fog_node.inputs["Max Distance"].default_value = old_fog_node.inputs["Max Distance"].default_value
            fog_node.inputs["Min Distance"].default_value = old_fog_node.inputs["Min Distance"].default_value
            fog_node.inputs["Anisotropy"].default_value = old_fog_node.inputs["Anisotropy"].default_value
            fog_node.inputs["Emission"].default_value = old_fog_node.inputs["Emission"].default_value
            bpy.data.objects.remove(old_fog_obj, do_unlink=True)
        except Exception:
            trigger_absolute_solver("n00", traceback.format_exc()) # Replace with a custom error "Cannot Migrate data=Fog"

    @perf_time
    def recreate_environment(self):
        pass
