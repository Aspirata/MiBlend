from .Data import *

def get_asset_path(category, asset_name):

    try:
        asset_data = Assets[category][asset_name]
        asset_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Assets", category, asset_data["File_name"])
        return asset_path, asset_data
    except KeyError:
        print(f"Asset '{asset_name}' in category '{category}' not found.")
        return None, None
    
def append_asset(asset_name, asset_category):
    asset_path, asset_data = get_asset_path(asset_category, asset_name)
    if asset_path is None:
        return
    
    try:
        if asset_category == "Rigs":
            collection_name = asset_data["Collection_name"]

            with bpy.data.libraries.load(asset_path, link=False) as (data_from, data_to):
                data_to.collections = [collection_name]

            for collection in data_to.collections:
                bpy.context.collection.children.link(collection)

        elif asset_category == "Scripts":
            run_python_script(asset_path)
        
    except Exception as e:
        print(f"Failed to append asset '{asset_name}' from category '{asset_category}': {e}")

def update_assets(idk_lol):
    items = bpy.context.scene.assetsproperties.asset_items
    items.clear()

    for category, assets in Assets.items():
        for key in assets.keys():
            item = items.add()
            item.name = key
    
def run_python_script(file_path):
    try:
        with open(file_path, 'r') as file:
            exec(file.read(), {'__name__': '__main__'})
    except Exception as e:
        print(f"Failed to run script '{file_path}': {e}")