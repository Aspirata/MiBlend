import bpy
from pathlib import Path
from bpy.app.handlers import persistent
from .Preferences import MiBlendPreferences
from .MIB_API import dprint
from .Assets import update_assets
from .Utils.Absolute_Solver import *
from .Resource_Packs import update_default_pack
from .UI import *
from .Utils.AS_Solutions import *
from .Operators import *
from .Properties import *

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

panels = [WorldAndMaterialsPanel, AssetPanel, Assets_List_UL_]
properties = [WorldProperties, ResourcePackProperties, CreateEnvProperties, PPBRProperties, AssetTagItem, 
            AssetsProperties, AbsoluteSolverProperties, MiBlendProperties
]

special_classes = [MiBlendPreferences, AbsoluteSolverIgnore, AbsoluteSolverPanel, RecreateEnvironment]

operators = [
    RemoveAttributeOperator, CopyToClipboardOperator, FixWorldOperator, SwapTexturesOperator, ResourcePackToggleOperator,
    MoveResourcePackUp, MoveResourcePackDown, RemoveResourcePack, UpdateDefaultPack, AddResourcePack, ApplyResourcePack, CreateEnvOperator,
    FixMaterialsOperator, SetProceduralPBROperator, AddAsset, RemoveAsset, ImportAssetOperator, SavePropertiesOperator,
    ResetPropertiesOperator, ManualAssetsUpdateOperator, FixCompatibility, ClearIgnoredCodesOperator, DeleteMiblendAddon,
    SavePreferencesOperator, ResetPreferencesOperator, SaveBlendFile
]

debug_classes = [DebugPanel, TriggerASErrorOperator, OpenMiBlendFolder]

classes = properties + special_classes + operators + panels + debug_classes

cls_register, cls_unregister = bpy.utils.register_classes_factory(classes)

@persistent
def on_scene_load(dummy):
    bpy.app.timers.register(init_on_start, first_interval=0.1)

def register():
    cls_register()
    
    bpy.types.Scene.miblend_properties = bpy.props.PointerProperty(type=MiBlendProperties)
    
    if on_scene_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(on_scene_load)
        
    bpy.app.timers.register(init_on_start, first_interval=0.4)

def unregister():
    if on_scene_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_scene_load)

    if hasattr(bpy.types.Scene, "miblend_properties"):
        del bpy.types.Scene.miblend_properties

    cls_unregister()

if __name__ == "__main__":
    register()