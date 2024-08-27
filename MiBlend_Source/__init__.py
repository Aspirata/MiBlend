from .Data import *
from .Preferences import MiBlendPreferences
from .MIB_API import *
from .Assets import update_assets
from .Utils.Absolute_Solver import AbsoluteSolverPanel
from .Resource_Packs import update_default_pack
from .UI import *
from .Operators import *
from .Properties import *
from bpy.app.handlers import persistent

bl_info = {
    "name": "MiBlend",
    "author": "Aspirata",
    "version": (0, 6, 0),
    "blender": (3, 6, 0),
    "doc_url": "https://github.com/Aspirata/Mcblend/wiki",
    "tracker_url": "https://github.com/Aspirata/Mcblend/issues",
    "location": "View3D > Addons Tab",
    "description": "A useful tool for creating minecraft content in blender",
}

def InitOnStart():
    
    bpy.context.scene["mib_options"] = {}
    mib_options = bpy.context.scene["mib_options"]

    if "resource_packs" not in bpy.context.scene:
        bpy.context.scene["resource_packs"] = {}
        update_default_pack()
    
    original_materials_list = {}
    with bpy.data.libraries.load(os.path.join(materials_folder, "Replaced Materials.blend"), link=False) as (data_from, data_to):
        for material_name in data_from.materials:
            split_name = material_name.split(" | ")
        
            if len(split_name) > 1 and "Dev" not in split_name:
                original_materials_list[split_name[0]] = split_name[1]

    if len(original_materials_list) > 0:
        mib_options["is_replaced_materials"] = True
    else:
        mib_options["is_replaced_materials"] = False

    update_assets()

    if bpy.context.preferences.addons[__package__].preferences.dev_tools and bpy.context.preferences.addons[__package__].preferences.open_console_on_start:
        bpy.ops.wm.console_toggle()

@persistent
def load_post_handler(dummy):
    InitOnStart()

classes = [MiBlendPreferences, AbsoluteSolverPanel, RecreateEnvironment,                                                                                          # Special Panels
    WorldProperties, MaterialsProperties, ResourcePackProperties, CreateEnvProperties, PPBRProperties, OptimizationProperties,                                    # Properties
    UtilsProperties, AssetTagItem, AssetsProperties,                                                                                                               
    WorldAndMaterialsPanel, OptimizationPanel, UtilsPanel, AssetPanel, Assets_List_UL_,                                                                           # Panels
    RemoveAttributeOperator, OpenConsoleOperator, FixWorldOperator, SwapTexturesOperator, ResourcePackToggleOperator, MoveResourcePackUp, MoveResourcePackDown,   # Operators
    RemoveResourcePack, UpdateDefaultPack, FixPacks, AddResourcePack, ApplyResourcePack, CreateEnvOperator, FixMaterialsOperator, UpgradeMaterialsOperator,       
    SetProceduralPBROperator, OptimizeOperator, SetRenderSettingsOperator, AssingVertexGroupOperator, AddAsset, ImportAssetOperator, SavePropertiesOperator,
    ManualAssetsUpdateOperator,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.world_properties = bpy.props.PointerProperty(type=WorldProperties)
    bpy.types.Scene.resource_properties = bpy.props.PointerProperty(type=ResourcePackProperties)
    bpy.types.Scene.materials_properties = bpy.props.PointerProperty(type=MaterialsProperties)
    bpy.types.Scene.env_properties = bpy.props.PointerProperty(type=CreateEnvProperties)
    bpy.types.Scene.ppbr_properties = bpy.props.PointerProperty(type=PPBRProperties)
    bpy.types.Scene.optimizationproperties = bpy.props.PointerProperty(type=OptimizationProperties)
    bpy.types.Scene.utilsproperties = bpy.props.PointerProperty(type=UtilsProperties)
    bpy.types.Scene.assetsproperties = bpy.props.PointerProperty(type=AssetsProperties)

    bpy.app.handlers.load_post.append(load_post_handler)

def unregister():
    del bpy.types.Scene.world_properties
    del bpy.types.Scene.resource_properties
    del bpy.types.Scene.materials_properties
    del bpy.types.Scene.env_properties
    del bpy.types.Scene.ppbr_properties
    del bpy.types.Scene.optimizationproperties
    del bpy.types.Scene.utilsproperties
    del bpy.types.Scene.assetsproperties

    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    bpy.app.handlers.load_post.remove(load_post_handler)


if __name__ == "__main__":
    register()

# TODO:
    # - World & Materials - Сделать ветер -- 20.06.24 Добавить как скрипт в UAS