from .assets_properties import MIBLEND_PG_assets, MIBLEND_PG_asset_item
from .assets_ui import MIBLEND_PT_assets, MIBLEND_UL_assets
from .assets_operators import (MIBLEND_OT_import_asset, MIBLEND_OT_update_assets, MIBLEND_OT_add_asset, 
                                MIBLEND_OT_remove_asset, MIBLEND_OT_reset_properties, MIBLEND_OT_save_properties)

classes = [
    MIBLEND_PG_asset_item,
    MIBLEND_PG_assets,
    MIBLEND_UL_assets,
    MIBLEND_PT_assets,
    MIBLEND_OT_import_asset,
    MIBLEND_OT_update_assets,
    MIBLEND_OT_add_asset,
    MIBLEND_OT_remove_asset,
    MIBLEND_OT_reset_properties,
    MIBLEND_OT_save_properties
]