from .MCB_API import *
from .Data import *
import sys
from distutils.version import LooseVersion

def get_resource_packs():
    return bpy.context.scene["resource_packs"]

def set_resource_packs(resource_packs, debug=None):
    bpy.context.scene["resource_packs"] = resource_packs

    if debug is not None:
        print(f"Resource Packs: {bpy.context.scene['resource_packs']}")

Launchers = {
    "Mojang": ".minecraft\\versions",
    "Modrinth": "com.modrinth.theseus\\meta\\versions",
}

def update_default_pack():
    resource_packs = bpy.context.scene["resource_packs"]
    Preferences = bpy.context.preferences.addons[__package__].preferences

    def version_formatter(version_name):
        version_parts = re.split(r'[ -]', version_name)
        for part in version_parts:
            if not any(char.isalpha() for char in part):
                return part
        return None

    def find_mc():
        versions = {}
        for launcher, path in Launchers.items():
            folders = os.path.join(os.getenv("HOME") if sys.platform.startswith('linux') else os.getenv('APPDATA'), path)
            if os.path.isdir(folders):
                for folder in os.listdir(folders):
                    if version := version_formatter(folder):
                        versions[version] = (folder, os.path.join(os.getenv('APPDATA'), path))
        
        if Preferences.mc_instances_path:
            folders = Preferences.mc_instances_path
            if os.path.isdir(folders):
                for folder in os.listdir(folders):
                    if version := version_formatter(folder):
                        versions[version] = (folder, Preferences.mc_instances_path)
            
        if versions:
            latest_version = max(versions, key=lambda x: LooseVersion(x))
            latest_file, latest_path = versions[latest_version]
            return latest_version, os.path.join(latest_path, latest_file, f"{latest_file}.jar")
        
        return None, None

    MC = find_mc()
    if MC != (None, None):
        version, path = MC
        default_pack = f"Minecraft {version}"
        default_path = os.path.join(resource_packs_directory, default_pack)
        resource_packs[default_pack] = {"path": (path), "type": "Texture", "enabled": True}
        debugger(resource_packs[default_pack]["path"])
    else:
        print("MC instance not found")

    if Preferences.dev_tools and Preferences.dev_packs_path:
        dev_resource_packs_directory = Preferences.dev_packs_path
        default_pack = "Bare Bones 1.21"
        default_path = os.path.join(dev_resource_packs_directory, default_pack)
        resource_packs[default_pack] = {"path": (default_path),"type": "Texture", "enabled": False}

        default_pack = "Better Emission"
        default_path = os.path.join(dev_resource_packs_directory, default_pack)
        resource_packs[default_pack] = {"path": (default_path), "type": "PBR", "enabled": True}

        default_pack = "Embrace Pixels PBR"
        default_path = os.path.join(dev_resource_packs_directory, default_pack)
        resource_packs[default_pack] = {"path": (default_path), "type": "PBR", "enabled": True}
    else:
        default_pack = "Bare Bones 1.21"
        default_path = os.path.join(resource_packs_directory, default_pack)
        resource_packs[default_pack] = {"path": (default_path),"type": "Texture", "enabled": False}

        default_pack = "Better Emission"
        default_path = os.path.join(resource_packs_directory, default_pack)
        resource_packs[default_pack] = {"path": (default_path), "type": "PBR", "enabled": True}

        default_pack = "Embrace Pixels PBR"
        default_path = os.path.join(resource_packs_directory, default_pack)
        resource_packs[default_pack] = {"path": (default_path), "type": "PBR", "enabled": True}