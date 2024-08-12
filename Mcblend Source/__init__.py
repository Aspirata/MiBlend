from .Data import *
from .Preferences import McblendPreferences
from .MCB_API import *
from .Assets import update_assets
from .Utils.Absolute_Solver import AbsoluteSolverPanel
from .Resource_Packs import update_default_pack
from .UI import *
from .Operators import *
from .Properties import *
from bpy.app.handlers import persistent

bl_info = {
    "name": "Mcblend",
    "author": "Aspirata",
    "version": (0, 5, 0),
    "blender": (3, 6, 0),
    "doc_url": "https://github.com/Aspirata/Mcblend/wiki",
    "tracker_url": "https://github.com/Aspirata/Mcblend/issues",
    "location": "View3D > Addons Tab",
    "description": "A useful tool for creating minecraft content in blender",
}

def InitOnStart():

    if "resource_packs" not in bpy.context.scene:
        bpy.context.scene["resource_packs"] = {}
        update_default_pack()
        
    update_assets()

    if bpy.context.preferences.addons[__package__].preferences.dev_tools and bpy.context.preferences.addons[__package__].preferences.open_console_on_start:
        bpy.ops.wm.console_toggle()

@persistent
def load_post_handler(dummy):
    InitOnStart()

classes = [McblendPreferences, AbsoluteSolverPanel, RecreateEnvironment,                                                                                          # Special Panels
    WorldProperties, MaterialsProperties, ResourcePackProperties, CreateEnvProperties, PPBRProperties, OptimizationProperties, UtilsProperties, AssetsProperties, # Properties
    WorldAndMaterialsPanel, OptimizationPanel, UtilsPanel, AssetPanel, Assets_List_UL_,                                                                           # Panels
    RemoveAttributeOperator, OpenConsoleOperator, FixWorldOperator, SwapTexturesOperator, ResourcePackToggleOperator, MoveResourcePackUp, MoveResourcePackDown,   # Operators
    RemoveResourcePack, UpdateDefaultPack, FixPacks, AddResourcePack, ApplyResourcePack, CreateEnvOperator, FixMaterialsOperator, UpgradeMaterialsOperator,       
    SetProceduralPBROperator, OptimizeOperator, SetRenderSettingsOperator, EnchantOperator, AssingVertexGroupOperator, ImportAssetOperator,
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