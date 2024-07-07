from .Data import *
from distutils.version import LooseVersion

def get_resource_packs(debug=None):
    if debug is not None:
        print(f"Resource Packs: {bpy.context.scene['resource_packs']}")

    return bpy.context.scene["resource_packs"]

def set_resource_packs(resource_packs, debug=None):
    bpy.context.scene["resource_packs"] = resource_packs

    if debug is not None:
        print(f"Resource Packs: {bpy.context.scene['resource_packs']}")

def update_default_pack():
    resource_packs = bpy.context.scene["resource_packs"]

    def version_formatter(launcher, version_name):
        if launcher == "Modrinth" and not any(char.isalpha() for char in version_name):
            return version_name.split("-")[0]
        return None

    def find_mc():
        versions = {}
        for launcher, path in Launchers.items():
            folders = os.listdir(os.path.join(os.getenv('APPDATA'), path))
            for folder in folders:
                if version := version_formatter(launcher, folder):
                    versions[version] = (folder, os.path.join(os.getenv('APPDATA'), path))
            
        if versions:
            latest_version = max(versions, key=lambda x: LooseVersion(x))
            latest_file, latest_path = versions[latest_version]
            return latest_version, os.path.join(latest_path, latest_file, f"{latest_file}.jar")
        else:
            return None, None

    MC = find_mc()
    if MC != (None, None):
        version, path = MC
        default_pack = f"Minecraft {version}"
        default_path = os.path.join(resource_packs_directory, default_pack)
        resource_packs[default_pack] = {"path": (path), "type": "Texture", "enabled": True}
    else:
        print("MC not found")

    default_pack = "Bare Bones 1.20.6"
    default_path = os.path.join(resource_packs_directory, default_pack)
    resource_packs[default_pack] = {"path": (default_path),"type": "Texture", "enabled": False}

    default_pack = "Better Emission"
    default_path = os.path.join(resource_packs_directory, default_pack)
    resource_packs[default_pack] = {"path": (default_path), "type": "PBR", "enabled": True}

    default_pack = "Embrace Pixels 2.1"
    default_path = os.path.join(resource_packs_directory, default_pack)
    resource_packs[default_pack] = {"path": (default_path), "type": "PBR", "enabled": True}