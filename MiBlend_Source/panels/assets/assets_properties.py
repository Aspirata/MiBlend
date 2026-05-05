import os
import json
from bpy.props import BoolProperty, StringProperty, CollectionProperty, IntProperty, EnumProperty
from bpy.types import PropertyGroup
from ...resources.data import assets_directory


class MIBLEND_PG_asset_item(PropertyGroup):
    name: StringProperty()
    enabled: BoolProperty(default=False)


class MIBLEND_PG_assets(PropertyGroup):
    asset_items: CollectionProperty(type=PropertyGroup)

    asset_index: IntProperty(default=0)

    filters: BoolProperty(
        name="Filters",
        default=False
    )

    def get_tags(self):
        unique_tags = set()

        for root, dirs, files in os.walk(assets_directory):
            for file in files:
                if file.endswith(".json"):
                    json_path = os.path.join(root, file)
                    with open(json_path, 'r') as f:
                        asset_data = json.load(f)
                        tags = asset_data.get("Tags", [])
                        unique_tags.update(tags)

        unique_tags = sorted(unique_tags)
        return [('All', "All", "")] + [(tag, tag, "") for tag in unique_tags]

    tags: CollectionProperty(type=MIBLEND_PG_asset_item)
    
    properties_toggle: BoolProperty(
        name="Properties Toggle",
        default=True
    )
    
    tags_mode: EnumProperty(
        items=[("and", "And", ""), ("or", "Or", "")],
        name="tags_mode",
        default='or',
    )

    filter_by_version: BoolProperty(
        name="Filter By Blender Version",
        default=True
    )
