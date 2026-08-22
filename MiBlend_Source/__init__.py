import bpy
import traceback
from pathlib import Path
from bpy.app.handlers import persistent
from .preferences import MiBlendPreferences, MIBLEND_OT_save_preferences
from .mib_utils import dprint
from .panels.assets.assets_logic import update_assets
from .panels.absolute_solver.absolute_solver_logic import trigger_absolute_solver, cancel_absolute_solver_queue, cancel_reverse_all_changes
from .panels.resource_packs.resource_packs_logic import update_default_pack
from .panels import classes as panel_classes, MIBLEND_PG_properties

def init_on_start():
    try:
        if not bpy.context.scene.get("resource_packs", None):
            bpy.context.scene["resource_packs"] = {}
        update_default_pack()

        if not bpy.context.scene.get("mib_options", None):
            bpy.context.scene["mib_options"] = {}

        mib_options = bpy.context.scene["mib_options"]

        old_components_dict = dict(mib_options.get("components_vesion", {}))
        new_components_dict = {
            "MiBlend": "Snake",
        }
        
        new_miblend_hard_version_name = new_components_dict.get("MiBlend", "Snake")
        old_miblend_hard_version_name = old_components_dict.get("MiBlend", "")
        if old_miblend_hard_version_name != "" and old_miblend_hard_version_name != new_miblend_hard_version_name:
            trigger_absolute_solver("w04", data=f'"MiBlend" {old_miblend_hard_version_name} -> {new_miblend_hard_version_name}')
            dprint(f'"MiBlend" {old_miblend_hard_version_name} -> {new_miblend_hard_version_name}')

        # Pre-0.7.0 properties cleanup
        for prop in ["world_properties", "resource_properties", "materials_properties", "env_properties", "ppbr_properties", "optimizationproperties", "utilsproperties", "assetsproperties"]:
            if hasattr(bpy.context.scene, prop):
                delattr(bpy.context.scene, prop)

        mib_options["components_vesion"] = new_components_dict

        if "temp_assets_paths" not in mib_options:
            mib_options["temp_assets_paths"] = []

        update_assets()

        miblend_legacy_addon_folder = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "addons" / "MiBlend_Source"
        dprint(miblend_legacy_addon_folder, is_deep=True)
        if miblend_legacy_addon_folder.is_dir():
            trigger_absolute_solver("e10")

    except Exception:
        trigger_absolute_solver("n00", traceback.format_exc())


panel_classes.extend([MiBlendPreferences, MIBLEND_OT_save_preferences])
cls_register, cls_unregister = bpy.utils.register_classes_factory(panel_classes)


@persistent
def on_scene_load(dummy):
    bpy.app.timers.register(init_on_start, first_interval=0.1)

def register():
    cls_register()
    
    bpy.types.Scene.miblend_properties = bpy.props.PointerProperty(type=MIBLEND_PG_properties)
    
    if on_scene_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(on_scene_load)
        
    bpy.app.timers.register(init_on_start, first_interval=0.4)

def unregister():
    if on_scene_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_scene_load)

    cancel_absolute_solver_queue()
    cancel_reverse_all_changes()

    if hasattr(bpy.types.Scene, "miblend_properties"):
        del bpy.types.Scene.miblend_properties

    cls_unregister()

if __name__ == "__main__":
    register()
