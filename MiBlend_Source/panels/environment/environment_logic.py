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
            not any(obj.get("miblend_id") == "sky_controller" for obj in bpy.context.scene.objects) and \
            not any(obj.get("miblend_id") == "stars_controller" for obj in bpy.context.scene.objects) and \
            bpy.context.scene.world.name != "MiBlend Sky":
            self.create_sky(miblend_env_collection)

        if self.environment_properties.create_clouds and \
            not any(obj.get("miblend_id") == "clouds" for obj in bpy.context.scene.objects):
            self.create_clouds(miblend_env_collection)
        
        if self.environment_properties.create_fog and \
            not any(obj.get("miblend_id") == "fog" for obj in bpy.context.scene.objects):
            self.create_fog(miblend_env_collection)

    def create_sky(self, miblend_env_collection):
        with bpy.data.libraries.load(str(self.ENVIRONMENT_BLEND_FILE_PATH.expanduser().resolve()), link=False, reuse_local_id=True) as (_, data_to):
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

    def create_clouds(self, miblend_env_collection):
        clouds_obj = append_from_blend(self.ENVIRONMENT_BLEND_FILE_PATH, "objects", "MiBlend Clouds")

        if clouds_obj is None:
            trigger_absolute_solver("n00", traceback.format_exc())
            return

        move_to_collection(clouds_obj, miblend_env_collection)

    def create_fog(self, miblend_env_collection):
        pass

    @perf_time
    def recreate_environment(self):
        pass

    