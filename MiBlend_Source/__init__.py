import bpy, os
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

bl_info = {
    "name": "MiBlend",
    "author": "Aspirata",
    "version": (0, 7, 1),
    "blender": (3, 6, 0),
    "doc_url": "https://docs.page/Aspirata/MiBlend",
    "tracker_url": "https://github.com/Aspirata/MiBlend/issues",
    "location": "View3D > Addons Tab",
    "description": "A useful tool for creating minecraft content in blender",
}

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
            "MiBlend": "Butterfly",
            "UAS": "v2.1.4",
        }
        
        for component, component_version in old_components_dict.items():
            if component in ["Absolute Solver", "Index", "Milestone"]:
                continue
                
            if component not in new_components_dict or component_version != new_components_dict.get(component):
                Call_AS("w04", data=f"Component: {component} is outdated ({component_version} -> {new_components_dict.get(component)})")
                dprint(f"Component: {component} is outdated ({component_version} -> {new_components_dict.get(component)})")

        for prop in ["world_properties", "resource_properties", "materials_properties", "env_properties", "ppbr_properties", "optimizationproperties", "utilsproperties", "assetsproperties"]:
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

panels = [WorldAndMaterialsPanel, AssetPanel, Assets_List_UL_]
properties = [WorldProperties, MaterialsProperties, ResourcePackProperties, CreateEnvProperties,
    PPBRProperties, AssetTagItem, AssetsProperties, UtilsProperties, OptimizationProperties, AbsoluteSolverProperties, MiBlendProperties
]
special_classes = [MiBlendPreferences, AbsoluteSolverIgnore, AbsoluteSolverPanel, RecreateEnvironment]

operators = [
    RemoveAttributeOperator, OpenConsoleOperator, CopyToClipboardOperator, FixWorldOperator, SwapTexturesOperator, ResourcePackToggleOperator, 
    MoveResourcePackUp, MoveResourcePackDown, RemoveResourcePack, UpdateDefaultPack, AddResourcePack, ApplyResourcePack, CreateEnvOperator, 
    FixMaterialsOperator, UpgradeMaterialsOperator, SetProceduralPBROperator, AddAsset, RemoveAsset, ImportAssetOperator, SavePropertiesOperator,
    ResetPropertiesOperator, ManualAssetsUpdateOperator, FixCompatibility, ClearIgnoredCodesOperator, SavePreferencesOperator, ResetPreferencesOperator
]

debug_classes = [DebugPanel, TriggerASErrorOperator, OpenMiBlendFolder]
deprecated_classes = [OptimizationPanel, OptimizeOperator, UtilsPanel, SetRenderSettingsOperator, AssingVertexGroupOperator]

classes = properties + special_classes + operators + panels + debug_classes + deprecated_classes

@persistent
def on_scene_load(dummy):
    bpy.app.timers.register(init_on_start, first_interval=0.1)

def register():
    if on_scene_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(on_scene_load)
   
    # Safe registration of the classes
    for cls in classes:
        try:
            # Attempt to unregister if class already exists
            if hasattr(bpy.types, cls.__name__):
                try:
                    bpy.utils.unregister_class(cls)
                except (ValueError, RuntimeError):
                    # Class might be registered by another addon
                    pass
           
            # Register class
            bpy.utils.register_class(cls)
           
        except ValueError as e:
            dprint(f"Error registering class {cls.__name__}: {e}")
            # Logic for handling specific errors can be added here
            continue

    # Scene properties registration
    try:
        bpy.types.Scene.miblend_properties = bpy.props.PointerProperty(type=MiBlendProperties)
    except Exception as e:
        dprint(f"Error registering scene properties: {e}")
    
    bpy.app.timers.register(init_on_start, first_interval=0.4)

def unregister():
    if on_scene_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_scene_load)
       
    # Remove scene properties
    if hasattr(bpy.types.Scene, "miblend_properties"):
        del bpy.types.Scene.miblend_properties
   
    for cls in reversed(classes):
        try:
            if hasattr(bpy.types, cls.__name__):
                bpy.utils.unregister_class(cls)
        except (ValueError, RuntimeError) as e:
            dprint(f"Error unregistering class {cls.__name__}: {e}")
            continue

if __name__ == "__main__":
    register()