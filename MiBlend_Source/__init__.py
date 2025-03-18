from .Data import *
from .Preferences import MiBlendPreferences
from .MIB_API import *
from .Assets import update_assets
from .Utils.Absolute_Solver import AbsoluteSolverPanel
from .Resource_Packs import update_default_pack
from .UI import *
from .Utils.AS_Solutions import *
from .Operators import *
from .Properties import *
from bpy.app.handlers import persistent

bl_info = {
    "name": "MiBlend",
    "author": "Aspirata",
    "version": (0, 7, 0),
    "blender": (3, 6, 0),
    "doc_url": "https://docs.page/Aspirata/MiBlend",
    "tracker_url": "https://github.com/Aspirata/MiBlend/issues",
    "location": "View3D > Addons Tab",
    "description": "A useful tool for creating minecraft content in blender",
}

def init_on_start():
    try:
        if "resource_packs" not in bpy.context.scene:
            bpy.context.scene["resource_packs"] = {}
            update_default_pack()
        
        if "mib_options" not in bpy.context.scene:
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
            "MiBlend": "Butterfly",
            "UAS": "v2.1.3",
            "Absolute Solver": "v2.0",
        }

        for component, component_version in old_components_dict.items():
            if component not in ["Absolute Solver", "Index"]:
                if component not in new_components_dict or component_version != new_components_dict.get(component):
                    Call_AS("e01", data=f"Component: {component} is outdated ({component_version} -> {new_components_dict.get(component)})")
                    dprint(f"Component: {component} is outdated ({component_version} -> {new_components_dict.get(component)})")

        if hasattr(bpy.context.scene, "world_properties") or hasattr(bpy.context.scene, "resource_properties") or hasattr(bpy.context.scene, "materials_properties") \
        or hasattr(bpy.context.scene, "env_properties") or hasattr(bpy.context.scene, "ppbr_properties") or hasattr(bpy.context.scene, "assetsproperties"):
            for prop in ["world_properties", "resource_properties", "materials_properties", "env_properties", "ppbr_properties", "optimizationproperties", "utilsproperties", "assetsproperties", "script_asset_properties"]:
                if hasattr(bpy.context.scene, prop):
                    delattr(bpy.context.scene, prop)
                    
        mib_options["components_vesion"] = new_components_dict

        if "temp_assets_paths" not in mib_options:
            mib_options["temp_assets_paths"] = []

        update_assets()

        if bpy.context.preferences.addons[__package__].preferences.dev_tools and bpy.context.preferences.addons[__package__].preferences.open_console_on_start and not sys.platform.startswith('linux'):
            bpy.ops.wm.console_toggle()
    except:
        Call_AS("n00", traceback.format_exc())

classes = [
    MiBlendPreferences, AbsoluteSolverPanel, RecreateEnvironment,
    WorldProperties, MaterialsProperties, ResourcePackProperties, CreateEnvProperties,
    PPBRProperties, AssetTagItem, AssetsProperties, UtilsProperties, OptimizationProperties, MiBlendProperties,
    WorldAndMaterialsPanel, AssetPanel, Assets_List_UL_,
    RemoveAttributeOperator, OpenConsoleOperator, CopyToClipboardOperator, FixWorldOperator, SwapTexturesOperator, ResourcePackToggleOperator, MoveResourcePackUp, MoveResourcePackDown,
    RemoveResourcePack, UpdateDefaultPack, AddResourcePack, ApplyResourcePack, CreateEnvOperator, FixMaterialsOperator, UpgradeMaterialsOperator,
    SetProceduralPBROperator, AddAsset, CreateAsset, ImportAssetOperator, SavePropertiesOperator,
    ResetPropertiesOperator, ManualAssetsUpdateOperator, FixCompatibility,
]

deprecated_classes = [OptimizationPanel, OptimizeOperator, UtilsPanel, SetRenderSettingsOperator, AssingVertexGroupOperator]

@persistent
def on_scene_load(dummy):
    init_on_start()

def delayed_init():
    if bpy.context.scene is not None:
        init_on_start()
        return None
    return 0.1

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    if bpy.context.preferences.addons[__package__].preferences.enable_deprecated_features:
        for cls in deprecated_classes:
            bpy.utils.register_class(cls)

    bpy.types.Scene.miblend_properties = bpy.props.PointerProperty(type=MiBlendProperties)
    
    if on_scene_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(on_scene_load)

    bpy.app.timers.register(delayed_init)

def unregister():
    if bpy.context.preferences.addons[__package__].preferences.enable_deprecated_features:
        for cls in deprecated_classes:
            bpy.utils.unregister_class(cls)
        
        del bpy.types.Scene.utils_properties
        del bpy.types.Scene.optimization_properties
            
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.miblend_properties

    if on_scene_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_scene_load)

if __name__ == "__main__":
    register()