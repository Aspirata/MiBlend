import bpy, os, platform
from .Preferences import MiBlendPreferences
from .MIB_API import dprint
from .Data import materials_folder
from .Assets import update_assets
from .Utils.Absolute_Solver import *
from .Resource_Packs import update_default_pack
from .UI import *
from .Utils.AS_Solutions import *
from .Operators import *
from .Properties import *
from bpy.app.handlers import persistent

def init_on_start():
    try:
        if not bpy.context.scene.get("resource_packs", None):
            bpy.context.scene["resource_packs"] = {}
        update_default_pack()

        if not bpy.context.scene.get("mib_options", None):
            bpy.context.scene["mib_options"] = {}

        mib_options = bpy.context.scene["mib_options"]

        original_materials_list = {}
        with bpy.data.libraries.load(os.path.join(materials_folder, "Replaced Materials.blend"), link=False) as (data_from, data_to):
            for material_name in data_from.materials:
                split_name = material_name.split(" | ")
            
                if len(split_name) > 1 and "Dev" not in split_name:
                    original_materials_list[split_name[0]] = split_name[1]

        mib_options["is_replaced_materials"] = len(original_materials_list) > 0

        old_components_dict = dict(mib_options.get("components_vesion", {}))
        new_components_dict = {
            "MiBlend": "Snake",
        }
        
        new_miblend_hard_version_name = new_components_dict.get("MiBlend", "Snake")
        old_miblend_hard_version_name = old_components_dict.get("MiBlend", "")
        if old_miblend_hard_version_name != "" and old_miblend_hard_version_name != new_miblend_hard_version_name:
            Call_AS("w04", data=f'"MiBlend" {old_miblend_hard_version_name} -> {new_miblend_hard_version_name}')
            dprint(f'"MiBlend" {old_miblend_hard_version_name} -> {new_miblend_hard_version_name}')

        # Pre-0.7.0 properties cleanup
        for prop in ["world_properties", "resource_properties", "materials_properties", "env_properties", "ppbr_properties", "optimizationproperties", "utilsproperties", "assetsproperties"]:
            if hasattr(bpy.context.scene, prop):
                delattr(bpy.context.scene, prop)

        mib_options["components_vesion"] = new_components_dict

        if "temp_assets_paths" not in mib_options:
            mib_options["temp_assets_paths"] = []

        update_assets()

        if bpy.context.preferences.addons[__package__].preferences.dev_tools and bpy.context.preferences.addons[__package__].preferences.open_console_on_start and platform.platform() == "Windows":
            bpy.ops.wm.console_toggle()
    except Exception:
        Call_AS("n00", traceback.format_exc())

panels = [WorldAndMaterialsPanel, AssetPanel, Assets_List_UL_]
properties = [WorldProperties, ResourcePackProperties, CreateEnvProperties, PPBRProperties, AssetTagItem, 
            AssetsProperties, UtilsProperties, OptimizationProperties, AbsoluteSolverProperties, MiBlendProperties
]

special_classes = [MiBlendPreferences, AbsoluteSolverIgnore, AbsoluteSolverPanel, RecreateEnvironment]

operators = [
    RemoveAttributeOperator, OpenConsoleOperator, CopyToClipboardOperator, FixWorldOperator, SwapTexturesOperator, ResourcePackToggleOperator, 
    MoveResourcePackUp, MoveResourcePackDown, RemoveResourcePack, UpdateDefaultPack, AddResourcePack, ApplyResourcePack, CreateEnvOperator, 
    FixMaterialsOperator, UpgradeMaterialsOperator, SetProceduralPBROperator, AddAsset, RemoveAsset, ImportAssetOperator, 
    SavePropertiesOperator, ResetPropertiesOperator, ManualAssetsUpdateOperator, FixCompatibility, ClearIgnoredCodesOperator,
    SavePreferencesOperator, ResetPreferencesOperator
]

debug_classes = [DebugPanel, TriggerASErrorOperator, OpenMiBlendFolder]
deprecated_classes = [OptimizationPanel, OptimizeOperator, UtilsPanel, SetRenderSettingsOperator, AssingVertexGroupOperator]

classes = properties + special_classes + operators + panels + debug_classes + deprecated_classes

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