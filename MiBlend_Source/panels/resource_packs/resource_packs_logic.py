import bpy, os, json, zipfile, shutil, re, platform, http.client
from urllib.request import urlretrieve
from urllib.parse import urlparse
from distutils.version import LooseVersion
from ...mib_utils import *
from ..absolute_solver.absolute_solver_logic import trigger_absolute_solver

def get_resource_packs() -> dict[str, dict[str, str | bool]]:
    try:
        return bpy.context.scene["resource_packs"]
    except Exception as error:
        dprint(error, "Сannot find resource packs attr, creating new one with update_default_pack()")
        update_default_pack()
        return bpy.context.scene["resource_packs"]

def set_resource_packs(resource_packs):
    bpy.context.scene["resource_packs"] = resource_packs

    for pack, pack_info in bpy.context.scene["resource_packs"].items():
        print(f"{pack}, {pack_info['path']}, {pack_info['type']}")

Launchers = {
    "Windows": {
        "Mojang": ".minecraft\\versions",
        "Prism Launcher": "PrismLauncher\\libraries\\com\\mojang\\minecraft",
        "New_Modrinth": "ModrinthApp\\meta\\versions",
        "Old_Modrinth": "com.modrinth.theseus\\meta\\versions",
        "TL Legacy": ".tlauncher\\legacy\\Minecraft\\game\\versions",
    },

    "Linux": {
        "Mojang": "Unknown",
        "Prism Launcher": ".local/share/PrismLauncher/libraries/com/mojang/minecraft",
        "New_Modrinth": ".local/share/ModrinthApp/meta/versions",
        "Old_Modrinth": "Unknown",
        "TL Legacy": "Unknown",
    },

    "Darwin": {
        "Mojang": "Library/Application Support/minecraft/versions",
        "Prism Launcher": "Library/Application Support/PrismLauncher/libraries/com/mojang/minecraft",
        "New_Modrinth": "Library/Application Support/ModrinthApp/meta/versions",
        "Old_Modrinth": "Unknown",
        "TL Legacy": "Unknown",
    }
}

def find_mc() -> tuple[str, str]:
    versions = {}
    Preferences = get_preferences()
    current_os = platform.system()
    os_env = os.getenv('APPDATA') if current_os == "Windows" else os.path.expanduser("~")

    for launcher, path in Launchers.get(current_os).items():
        if path == "Unknown" and current_os != "Windows":
            os_apps_dir = "Library/Application Support" if current_os == "Darwin" else ".local/share"
            guessed_path = os.path.join(os_env, os_apps_dir, Launchers.get("Windows").get(launcher).replace("\\", "/"))
            print(f"Guessing {guessed_path}...")
            if not os.path.exists(guessed_path):
                print(f"Cannot find {guessed_path}")
                continue
            print(f"Using {guessed_path}")
            path = guessed_path

        folders = Preferences.mc_instances_path if Preferences.mc_instances_path else os.path.join(os_env, path)
        if not os.path.isdir(folders):
            continue
        
        for folder in os.listdir(folders):
            instance_dir = os.path.join(folders, folder)
            if not os.path.isdir(instance_dir):
                continue

            jar_file = next((f for f in os.listdir(instance_dir) if f.endswith('.jar')), None)
            if not jar_file:
                continue

            instance_path = os.path.join(instance_dir, jar_file)
            version = mc_version_formatter(folder)
            if version and os.path.isfile(instance_path):
                versions[version] = (jar_file, instance_path)
                dprint(f"{instance_path} valid", is_deep=True, zone="rp")
            else:
                dprint(f"{instance_path} invalid", is_deep=True, zone="rp")
        
    if versions:
        latest_version = max(versions, key=lambda x: LooseVersion(x))
        _latest_file, latest_path = versions[latest_version]
        return latest_version, latest_path
    
    return "", ""

def update_pack(pack: str, connection=None):
    resource_packs_directory = get_resource_path()
    
    try:
        with open(os.path.join(resource_packs_directory, "packs_info.json"), "r") as file:
            data = json.load(file)
            pack_data = data.get(pack, {})
            pack_info = (pack_data.get("mc_version", "Unknown"), pack_data.get("pack_version", "Unknown"))
            link = pack_data.get("link")
        
        if not link or "modrinth" not in link:
            return None
        
        if connection is None:
            connection = http.client.HTTPSConnection("api.modrinth.com")
            created_connection = True
        else:
            created_connection = False
        
        api_path = f"/v2/project/{pack.lower().replace(' ', '-')}/version"
        connection.request("GET", api_path)
        response = connection.getresponse()
        
        if response.status != 200:
            dprint(f"Error {response.status}", is_deep=True, zone="rp")
            if created_connection:
                connection.close()
            return None
        
        versions = json.loads(response.read().decode("utf-8"))
        
        if not versions:
            if created_connection:
                connection.close()
            return None
        
        latest_version = max(versions, key=lambda v: v["date_published"])
        latest_pack_info = (latest_version["game_versions"], latest_version["version_number"], latest_version["files"][0]["url"])
        pack_path = os.path.join(resource_packs_directory, pack)
        
        needs_update = (
            not all(LooseVersion(pack_info[0]) >= LooseVersion(v) for v in latest_pack_info[0]) or
            LooseVersion(pack_info[1]) < LooseVersion(latest_pack_info[1]) or
            not os.path.exists(pack_path) or
            pack_info == ("Unknown", "Unknown")
        )
        
        if needs_update:
            dprint(f"Downloading pack: {pack} from {latest_pack_info[2]}", is_deep=True, zone="rp")
            if os.path.exists(pack_path):
                shutil.rmtree(pack_path)
            
            filename = os.path.join(resource_packs_directory, os.path.basename(urlparse(latest_pack_info[2]).path))
            urlretrieve(latest_pack_info[2], filename)
            
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall(pack_path)
            os.remove(filename)
            
            with open(os.path.join(resource_packs_directory, "packs_info.json"), "r+") as f:
                data = json.load(f)
                data[pack].update({
                    "mc_version": str(max(latest_pack_info[0], key=lambda x: LooseVersion(x))),
                    "pack_version": latest_pack_info[1]
                })
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
            
            dprint("Successfully Downloaded!", is_deep=True, zone="rp")
        
        if created_connection:
            connection.close()
    
    except Exception as e:
        dprint(f"Error: {e}", is_deep=True, zone="rp")
        if connection and created_connection:
            connection.close()
        return None

@perf_time
def update_default_pack():
    if "resource_packs" not in bpy.context.scene:
        bpy.context.scene["resource_packs"] = {}

    resource_packs = dict(bpy.context.scene["resource_packs"])
    Preferences = get_preferences()
    resource_packs_directory = get_resource_path()
    
    packs_to_remove = [pack for pack, pack_info in resource_packs.items() if pack_info.get("is_default", False)]
    for pack in packs_to_remove:
        del resource_packs[pack]
    
    version, path = find_mc()
    if version and path:
        default_pack = f"Minecraft {version}"
        default_path = os.path.join(resource_packs_directory, default_pack)
        resource_packs[default_pack] = {"path": path, "type": "Texture", "enabled": True, "is_default": True, "is_built_in": True}
        dprint(resource_packs[default_pack]["path"])
    else:
        print("MC instance not found")
    
    if not os.path.exists(resource_packs_directory):
        set_resource_packs(resource_packs)
        return
    
    with open(os.path.join(resource_packs_directory, "packs_info.json"), "r") as f:
        data = json.load(f)
        
        if Preferences.update_packs:
            connection = http.client.HTTPSConnection("api.modrinth.com")
        
        for pack in data:
            if pack not in os.listdir(resource_packs_directory):
                resource_packs[pack] = {
                    "path": os.path.join(resource_packs_directory, pack),
                    "type": data[pack]["type"],
                    "enabled": True,
                    "is_default": False,
                    "is_built-in": False
                }
            
            if Preferences.update_packs:
                update_pack(pack, connection=connection)
            
            default_pack = pack
            default_path = os.path.join(resource_packs_directory, default_pack)
            default_type = get_pack_info_properties(default_pack).get("type", "Texture & PBR")
            is_built_in = get_pack_info_properties(default_pack).get("is_built_in", False)
            resource_packs[default_pack] = {
                "path": default_path,
                "type": default_type,
                "enabled": False,
                "is_default": True,
                "is_built_in": is_built_in
            }
        
        if Preferences.update_packs:
            connection.close()
    
    set_resource_packs(resource_packs)

@perf_time
def apply_resources():

    resource_packs = get_resource_packs()
    r_props = bpy.context.scene.miblend_properties.resource_properties

    def fast_find_image(textures_paths: list, texture_name: str) -> str | None:
        for texture_path in filter(None, textures_paths):
            dir_path = os.path.dirname(texture_path)
            predicted_texture = os.path.join(dir_path, texture_name)
            if os.path.isfile(predicted_texture):
                return predicted_texture
        return None
    
    def find_image(image_name: str, root_folder: str, obj_type: str = "unknown", entity_name: str = "") -> str | None:

        if r_props.combine_duplicates:
            image_name = format_duplicate_name(image_name)

        if root_folder.endswith(('.zip', '.jar')):
            try:
                return zip_unpacker(root_folder, image_name, obj_type, entity_name=entity_name)
            except zipfile.BadZipFile:
                print("Bad Zip File")

        for dirpath, dirnames, files in os.walk(root_folder):
            if "textures" not in dirpath:
                continue

            if entity_name and "entity" in entity_name:
                dprint(f"{image_name} is {obj_type} using entity filter...", is_deep=True, zone="rp")
                if "sign" in entity_name:
                    dirpath = os.path.join(dirpath, obj_type, entity_name, "hanging" if "hang" in entity_name else "signs")
                else:
                    dirpath = os.path.join(dirpath, obj_type, entity_name)
            elif obj_type != "unknown":
                dprint(f"{image_name} is {obj_type} using texture filter...", is_deep=True, zone="rp")
                dirpath = os.path.join(dirpath, obj_type)
            else:
                dprint(f"{image_name} is {obj_type}", is_deep=True, zone="rp")
                dprint(f"Switching to hybrid mode...", is_deep=True, zone="rp")

            fast_image = os.path.join(dirpath, image_name)

            if os.path.isfile(fast_image):
                dprint(f"{fast_image} is found", is_deep=True, zone="rp")
                return fast_image
            else:
                dprint(f"{fast_image} isn't found, searching for the {image_name}...", is_deep=True, zone="rp")

            if not os.path.exists(dirpath):
                continue

            for dirpath, dirnames, files in os.walk(dirpath):
                for file in files:
                    if "colormap" in dirnames:
                        continue

                    if file == image_name:
                        return os.path.join(dirpath, file)
                    
                    if "grass" in image_name and (file == f"short_{image_name}" or file == image_name.replace("short_", "") or file == image_name):
                        return os.path.join(dirpath, file)

                    if file.endswith(('.zip', '.jar')):
                        try:
                            return zip_unpacker(os.path.join(dirpath, file), image_name, obj_type, file, entity_name)
                        except zipfile.BadZipFile:
                            trigger_absolute_solver("n00", traceback.format_exc())
        return None
    
    def zip_unpacker(root_folder: str, image_name: str, obj_type: str = "Unknown", file=None, entity_name: str = "") -> str | None:
        resource_packs_directory = get_resource_path()
        extract_path = os.path.join(resource_packs_directory, os.path.splitext(file if file is not None else os.path.basename(root_folder))[0])
        with zipfile.ZipFile(root_folder, 'r') as zip_ref:
            namelist = zip_ref.namelist()
            
            if entity_name and "entity" in entity_name:
                dprint(f"{image_name} is {obj_type} using entity filter...", is_deep=True, zone="rp")
                if "sign" in entity_name:
                    filtered_namelist = [item for item in namelist if f"textures/{obj_type}/{entity_name}/{'hanging' if 'hang' in entity_name else 'signs'}" in item and "colormap" not in item]
                else:
                    filtered_namelist = [item for item in namelist if f"textures/{obj_type}/{entity_name}" in item and "colormap" not in item]
            elif obj_type == "unknown":
                dprint(f"{image_name} is {obj_type}", is_deep=True, zone="rp")
                dprint(f"Switching to hybrid mode...", is_deep=True, zone="rp")
                filtered_namelist = [item for item in namelist if "textures" in item and "colormap" not in item]
            else:
                dprint(f"{image_name} is {obj_type} using texture filter...", is_deep=True, zone="rp")
                filtered_namelist = [item for item in namelist if f"textures/{obj_type}" in item and "colormap" not in item]
            namelist = filtered_namelist

            if not namelist:
                return None
            
            fast_image = namelist[0].replace(os.path.basename(namelist[0]), image_name)
            fast_mcmeta = namelist[0].replace(os.path.basename(namelist[0]), image_name + ".mcmeta")
            extracted_file_path = os.path.join(extract_path, fast_image)
            
            if fast_image in namelist:
                dprint(f"{fast_image} is found", is_deep=True, zone="rp")
                if not os.path.isfile(os.path.join(extract_path, fast_image)):
                    zip_ref.extract(fast_image, extract_path)

                if r_props.animate_textures and fast_mcmeta in namelist:
                    dprint(f"{fast_mcmeta} is found", is_deep=True, zone="rp")
                    if not os.path.isfile(os.path.join(extract_path, fast_mcmeta)):
                        zip_ref.extract(fast_mcmeta, extract_path)

                return extracted_file_path
            else:
                dprint(f"{fast_image} isn't found, searching for the {image_name}...", is_deep=True, zone="rp")

            if r_props.animate_textures:
                for zip_info in namelist:
                    if not zip_info.endswith(".mcmeta"):
                        continue

                    texture = os.path.basename(zip_info).replace(".mcmeta", "")
                    extracted_file_path = os.path.join(extract_path, zip_info)

                    if (texture == image_name) or ("grass" in image_name and (texture == f"short_{image_name}" or texture == image_name.replace("short_", "") or texture == image_name)) \
                        and not os.path.isfile(extracted_file_path):
                        zip_ref.extract(zip_info, extract_path)

            for zip_info in namelist:
                if not zip_info.endswith(".png"):
                    continue

                texture = os.path.basename(zip_info)
                extracted_file_path = os.path.join(extract_path, zip_info)

                if (texture == image_name) or ("grass" in image_name and (texture == f"short_{image_name}" or texture == image_name.replace("short_", "") or texture == image_name)):

                    if not os.path.isfile(extracted_file_path):
                        zip_ref.extract(zip_info, extract_path)

                    return extracted_file_path

        return None
    
    def find_texture_users(texture) -> list:
        Texture_users = []
        Textures_to_remove = []

        for material in bpy.data.materials:
            if not material or not material.use_nodes:
                continue

            for node in material.node_tree.nodes:

                if node.type != 'TEX_IMAGE' or not node.image:
                    continue

                if "MWO" not in node.image.name and format_duplicate_name(node.image.name) == format_duplicate_name(texture):
                    Texture_users.append(node)
                    Textures_to_remove.append(node.image)
    
        for group in bpy.data.node_groups:
            for node in group.nodes:
                if node.type != 'TEX_IMAGE' or not node.image:
                    continue

                if "MWO" not in node.image.name and format_duplicate_name(node.image.name) == format_duplicate_name(texture):
                    Texture_users.append(node)
                    Textures_to_remove.append(node.image)
        
        for tex in list(set(Textures_to_remove)):
            bpy.data.images.remove(tex, do_unlink=True)
    
        return list(set(Texture_users))
    
    def update_texture(new_image_path, image_texture, texture_node=None, colorspace=None):
        Users = find_texture_users(image_texture)

        new_image_texture = os.path.basename(new_image_path)
        if texture_node:
            if not texture_node.image:
                if image_texture in bpy.data.images:
                    texture_node.image = bpy.data.images[new_image_texture]
                else:
                    texture_node.image = bpy.data.images.load(new_image_path)

        if not Users:
            return
        
        if new_image_texture in bpy.data.images:
            user_texture = bpy.data.images[new_image_texture]
        else:
            bpy.data.images.load(new_image_path)
            user_texture = bpy.data.images[new_image_texture]

        if colorspace is not None:
            for user in Users:
                user.image = user_texture
                try:
                    user.image.colorspace_settings.name = colorspace
                except:
                    pass
        else:
            for user in Users:
                user.image = user_texture

    def animate_texture(texture_node, new_image_texture_path, ITexture_Animator, Current_node_tree, image_path=None, object: object=None):
        Texture_Animator = None
        auvf_node = None
        frames = 1
        
        if new_image_texture_path == "" and texture_node is None:
            return
        
        if new_image_texture_path != "":
            image_texture = bpy.data.images.get(os.path.basename(new_image_texture_path))
        else:
            image_texture = texture_node.image

        for node in material.node_tree.nodes:
            if node.type == "GROUP":
                if "Texture Animator" in node.node_tree.name:
                    Texture_Animator = node
                
                elif "Animated UV Fix" in node.node_tree.name:
                    auvf_node = node

        if r_props.animate_textures:
            x_divider = 1.0

            if name_in(["lava flow"], image_texture.name, True)[0]:
                frames = int(image_texture.size[1] / image_texture.size[0])*2
                x_divider = 2.0
            else:
                frames = int(image_texture.size[1] / image_texture.size[0])

            if frames <= 1:
                return
            
            animation_file = new_image_texture_path + ".mcmeta"

            if os.path.isfile(animation_file) and image_path is not None:
                animation_file = image_path + ".mcmeta"

            frametime = 20
            interpolate = False

            if os.path.isfile(animation_file):
                with open(animation_file, 'r') as file:
                    data = json.load(file).get('animation', {})
                    frametime = data.get('frametime', 20)
                    interpolate = data.get('interpolate', False)
            
            if r_props.randomize_speed:
                add_modifier(object, "Random Face Value")
            
            if auvf_node:
                 material.node_tree.nodes.remove(auvf_node)
                
            if interpolate and r_props.interpolate:
                if Texture_Animator is not None:
                    material.node_tree.nodes.remove(Texture_Animator)

                if ITexture_Animator is None:
                    
                    ITexture_Animator = material.node_tree.nodes.new(type='ShaderNodeGroup')
                    ITexture_Animator.location = texture_node.location

                    if f"Animated; {image_texture.name.replace('.png', '')}" in bpy.data.node_groups:
                        Current_node_tree = bpy.data.node_groups[f"Animated; {image_texture.name.replace('.png', '')}"]
                        ITexture_Animator.node_tree = Current_node_tree
                    else:
                        if "Texture Animator" not in bpy.data.node_groups:
                            with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                                data_to.node_groups = ["Texture Animator"]
                        
                        with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                            data_to.node_groups = ["Texture Animator"]

                        bpy.data.node_groups[f"Texture Animator.001"].name = f"Animated; {image_texture.name.replace('.png', '')}"
                        ITexture_Animator.node_tree = bpy.data.node_groups[f"Animated; {image_texture.name.replace('.png', '')}"]
                        for node in ITexture_Animator.node_tree.nodes:
                            if node.type == "TEX_IMAGE":
                                node.image = image_texture

                    if texture_node:
                        color_connection = GetConnectedSocketFrom("Color", texture_node)
                        if color_connection:
                            for socket in color_connection:
                                material.node_tree.links.new(ITexture_Animator.outputs["Color"], socket)
                    
                        alpha_connection = GetConnectedSocketFrom("Alpha", texture_node)
                        if alpha_connection:
                            for socket in alpha_connection:
                                material.node_tree.links.new(ITexture_Animator.outputs["Alpha"], socket)
                        
                        vector_connection = GetConnectedSocketTo("Vector", texture_node)

                        if vector_connection and vector_connection.node != ITexture_Animator:
                            material.node_tree.links.new(vector_connection, ITexture_Animator.inputs["Vector"])

                        material.node_tree.nodes.remove(texture_node)

                ITexture_Animator.inputs["Frames"].default_value = frames
                ITexture_Animator.inputs["X Divider"].default_value = x_divider
                ITexture_Animator.inputs["Frametime"].default_value = frametime
                ITexture_Animator.inputs["Interpolate"].default_value = True
                ITexture_Animator.inputs["Randomize Speed"].default_value = r_props.randomize_speed

            else:
                if ITexture_Animator:
                    texture_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')
                    texture_node.location = ITexture_Animator.location
                    texture_node.image = image_texture
                    texture_node.interpolation = "Closest"

                    color_connection = GetConnectedSocketFrom("Color", ITexture_Animator)
                    if color_connection:
                        for socket in color_connection:
                            material.node_tree.links.new(texture_node.outputs["Color"], socket)
                    
                    alpha_connection = GetConnectedSocketFrom("Alpha", ITexture_Animator)
                    if alpha_connection:
                        for socket in alpha_connection:
                            material.node_tree.links.new(texture_node.outputs["Alpha"], socket)

                    material.node_tree.nodes.remove(ITexture_Animator)

                if Texture_Animator is None:
                   Texture_Animator = create_node_group(material, "Texture Animator", (texture_node.location.x - 200, texture_node.location.y - 60))

                vector_connection = GetConnectedSocketTo("Vector", texture_node)

                if vector_connection is not None and vector_connection.node != Texture_Animator:
                    material.node_tree.links.new(vector_connection, Texture_Animator.inputs["Vector"])

                material.node_tree.links.new(Texture_Animator.outputs["Current Frame"], texture_node.inputs["Vector"])
            
                Texture_Animator.inputs["Frames"].default_value = frames
                Texture_Animator.inputs["X Divider"].default_value = x_divider
                Texture_Animator.inputs["Frametime"].default_value = frametime
                Texture_Animator.inputs["Interpolate"].default_value = False
                Texture_Animator.inputs["Randomize Speed"].default_value = r_props.randomize_speed
        else:
            if ITexture_Animator:
                texture_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')
                texture_node.location = ITexture_Animator.location
                texture_node.image = image_texture
                texture_node.interpolation = "Closest"

                for socket in GetConnectedSocketFrom("Color", ITexture_Animator):
                    material.node_tree.links.new(texture_node.outputs["Color"], socket)

                for socket in GetConnectedSocketFrom("Alpha", ITexture_Animator):
                    material.node_tree.links.new(texture_node.outputs["Alpha"], socket)

                material.node_tree.nodes.remove(ITexture_Animator)

            if Texture_Animator is not None:
                material.node_tree.nodes.remove(Texture_Animator)

            if auvf_node is not None and frames > 1:
                material.node_tree.links.new(auvf_node.outputs["Fixed UV"], texture_node.inputs["Vector"])

    def normal_texture_change(new_normal_image_path, normal_texture_node, normal_map_node, PBSDF, image_texture_node, image_path):
        NTexture_Animator = None
        Current_node_tree = None

        if new_normal_image_path is None:
            return False
        
        if normal_texture_node is None:
            normal_texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
            for node in material.node_tree.nodes:
                if node.type == "GROUP":
                    if "Animated;" in node.node_tree.name:
                        if re.search(r'_n$', node.node_tree.name.replace(".png", "")):
                            NTexture_Animator = node
                        elif re.search(r'_s$', node.node_tree.name.replace(".png", "")):
                            STexture_Animator = node
                        elif re.search(r'_e$', node.node_tree.name.replace(".png", "")):
                            ETexture_Animator = node
                        else:
                            ITexture_Animator = node
                        Current_node_tree = node.node_tree
            try:
                normal_texture_node.location = (image_texture_node.location.x, image_texture_node.location.y - 562)
            except:
                normal_texture_node.location = (ITexture_Animator.location.x, ITexture_Animator.location.y - 562)

            normal_texture_node.interpolation = "Closest"
        
        update_texture(new_normal_image_path, normal_image_name, normal_texture_node)
        
        try:
            normal_texture_node.image.colorspace_settings.name = "Non-Color"
        except:
            pass

        normal_map_node = create_node_group(material, "Normal Map Fixed", (normal_texture_node.location.x + 280, normal_texture_node.location.y), exists_check=True)
        material.node_tree.links.new(normal_texture_node.outputs["Color"], normal_map_node.inputs["Color"])
        material.node_tree.links.new(normal_map_node.outputs["Normal"], PBSDF.inputs["Normal"])
        
        animate_texture(normal_texture_node, new_normal_image_path, NTexture_Animator, Current_node_tree, image_path, object=selected_object)
        return True
        
    def specular_texture_change(path, specular_texture_node, LabPBR_s, new_normal_image_path, PBSDF, image_texture_node, image_texture, new_image_path, image_path):
        STexture_Animator = None
        Current_node_tree = None

        if not r_props.roughness and not r_props.metallic and not r_props.specular and not r_props.sss:
            return False

        if specular_texture_node is None:
            specular_image_name = image_texture.replace(".png", "_s.png")
        else:
            specular_image_name = specular_texture_node.image.name

        predicted_texture_path = fast_find_image([new_normal_image_path, new_image_path], specular_image_name)
        if predicted_texture_path is None and len([pack for pack in get_resource_packs().values() if "PBR" in pack.get("type", "")]) >= 1:
            new_specular_image_path = find_image(specular_image_name, path, entity_name=material.name)
        else:
            if not r_props.use_i or not r_props.use_n:
                new_specular_image_path = find_image(specular_image_name, path, entity_name=material.name)
            else:
                new_specular_image_path = predicted_texture_path

        if new_specular_image_path is not None:
            for node in material.node_tree.nodes:
                if node.type == "GROUP":
                    if "Animated;" in node.node_tree.name:
                        if re.search(r'_n$', node.node_tree.name.replace(".png", "")):
                            NTexture_Animator = node
                        elif re.search(r'_s$', node.node_tree.name.replace(".png", "")):
                            STexture_Animator = node
                        elif re.search(r'_e$', node.node_tree.name.replace(".png", "")):
                            ETexture_Animator = node
                        else:
                            ITexture_Animator = node
                            image_texture = node.node_tree.name.replace("Animated; ", "") + ".png"
                        Current_node_tree = node.node_tree

            if specular_texture_node is None and STexture_Animator is None:
                specular_texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
                try:
                    specular_texture_node.location = (image_texture_node.location.x, image_texture_node.location.y - 280)
                except:
                    specular_texture_node.location = (ITexture_Animator.location.x, ITexture_Animator.location.y - 280)

                specular_texture_node.interpolation = "Closest"

            update_texture(new_specular_image_path, specular_image_name, specular_texture_node, "Non-Color")

            if LabPBR_s is None:
                if "LabPBR Specular" not in bpy.data.node_groups:
                    with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                        data_to.node_groups = ["LabPBR Specular"]

                LabPBR_s = material.node_tree.nodes.new("ShaderNodeGroup")
                LabPBR_s.node_tree = bpy.data.node_groups["LabPBR Specular"]
                LabPBR_s.location = (specular_texture_node.location.x + 280, specular_texture_node.location.y)

            if STexture_Animator is None:
                material.node_tree.links.new(specular_texture_node.outputs["Color"], LabPBR_s.inputs["Color"])
                material.node_tree.links.new(specular_texture_node.outputs["Alpha"], LabPBR_s.inputs["Alpha"])
            else:
                material.node_tree.links.new(STexture_Animator.outputs["Color"], LabPBR_s.inputs["Color"])
                material.node_tree.links.new(STexture_Animator.outputs["Alpha"], LabPBR_s.inputs["Alpha"])

            if r_props.roughness:
                material.node_tree.links.new(LabPBR_s.outputs["Roughness"], PBSDF.inputs["Roughness"])
            else:
                RemoveLinksFrom(LabPBR_s.outputs["Roughness"])

            if r_props.metallic:
                material.node_tree.links.new(LabPBR_s.outputs["Reflectance (Metallic)"], PBSDF.inputs["Metallic"])
            else:
                RemoveLinksFrom(LabPBR_s.outputs["Reflectance (Metallic)"])
            
            if r_props.specular:
                material.node_tree.links.new(LabPBR_s.outputs["Porosity (Specular)"], PBSDF.inputs["Specular IOR Level"])
            else:
                RemoveLinksFrom(LabPBR_s.outputs["Porosity (Specular)"])

            if r_props.sss:
                material.node_tree.links.new(LabPBR_s.outputs["SSS"], PBSDF.inputs["Subsurface Weight"])

                PBSDF.inputs["Subsurface Radius"].default_value = (1,1,1)

                PBSDF.subsurface_method = 'BURLEY'
            else:
                RemoveLinksFrom(LabPBR_s.outputs["SSS"])

            if r_props.emission:
                try:
                    try:
                        material.node_tree.links.new(image_texture_node.outputs["Color"], PBSDF.inputs["Emission Color"])
                    except:
                        material.node_tree.links.new(ITexture_Animator.outputs["Color"], PBSDF.inputs["Emission Color"])
                except:
                    pass
            
                material.node_tree.links.new(LabPBR_s.outputs["Emission Strength"], PBSDF.inputs["Emission Strength"])
            else:
                RemoveLinksFrom(LabPBR_s.outputs["Emission Strength"])
                RemoveLinksFrom(PBSDF.inputs["Emission Color"])

            animate_texture(specular_texture_node, new_specular_image_path, STexture_Animator, Current_node_tree, image_path, object=selected_object)
            return new_specular_image_path
        
        return False
        
    def emission_texture_change(new_emission_image_path, emission_texture_node, PBSDF, image_texture_node, image_path):
        ETexture_Animator = None
        ITexture_Animator = None
        Current_node_tree = None

        if not (r_props.use_color or r_props.use_strength) or new_emission_image_path is None:
            return False
        
        if emission_texture_node is None:
            emission_texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")

        for node in material.node_tree.nodes:
            if node.type == "GROUP":
                if "Animated;" in node.node_tree.name:
                    if re.search(r'_n$', node.node_tree.name.replace(".png", "")):
                        NTexture_Animator = node
                    elif re.search(r'_s$', node.node_tree.name.replace(".png", "")):
                        STexture_Animator = node
                    elif re.search(r'_e$', node.node_tree.name.replace(".png", "")):
                        ETexture_Animator = node
                    else:
                        ITexture_Animator = node
                    Current_node_tree = node.node_tree

            try:
                emission_texture_node.location = (image_texture_node.location.x, image_texture_node.location.y - 850)
            except:
                emission_texture_node.location = (ITexture_Animator.location.x, ITexture_Animator.location.y - 850)

            emission_texture_node.interpolation = "Closest"

        update_texture(new_emission_image_path, emission_image_name, emission_texture_node)

        if r_props.use_color:
            material.node_tree.links.new(emission_texture_node.outputs["Color"], PBSDF.inputs["Emission Color"])
        else:
            RemoveLinksFrom(emission_texture_node.outputs["Color"])
        
        if r_props.use_strength:
            material.node_tree.links.new(emission_texture_node.outputs["Alpha"], PBSDF.inputs["Emission Strength"])
        else:
            RemoveLinksFrom(emission_texture_node.outputs["Alpha"])

        animate_texture(emission_texture_node, new_emission_image_path, ETexture_Animator, Current_node_tree, image_path, object=selected_object)
        return True

    for selected_object in bpy.context.selected_objects:
        if not selected_object.material_slots and not is_code_ignored("w01") and get_preferences().show_warnings:
            trigger_absolute_solver("w01", selected_object)
            continue
        
        elif not selected_object.material_slots:
            continue

        for slot, material in enumerate(selected_object.data.materials):
            if material is None or not material.use_nodes:
                continue
            
            if detect_world_exporter(selected_object) != "unknown" and selected_object.get("MiBlend ID", "") != "World" and not is_code_ignored("w02") and get_preferences().show_warnings:
                trigger_absolute_solver("w02", data=selected_object.name)
                continue
            
            PBSDF = None
            image_texture_node = None
            additional_texture_nodes = []
            image_path = None
            normal_texture_node = None
            normal_map_node = None
            specular_texture_node = None
            emission_texture_node = None
            LabPBR_s = None
            image_texture = None
            ITexture_Animator = None
            NTexture_Animator = None
            STexture_Animator = None
            ETexture_Animator = None
            Current_node_tree = None

            new_image_path = None
            new_normal_image_path = None
            new_specular_image_path = None

            obj_type = detect_obj_type(selected_object.name, material.name)

            nodes_list = get_nodes_list(material, True)

            for node in nodes_list:
                if node.type == "BSDF_PRINCIPLED":
                    PBSDF = node

                if node.type == "GROUP":
                    if "Animated;" in node.node_tree.name:
                        if re.search(r'_n$', node.node_tree.name.replace(".png", "")):
                            NTexture_Animator = node
                        elif re.search(r'_s$', node.node_tree.name.replace(".png", "")):
                            STexture_Animator = node
                        elif re.search(r'_e$', node.node_tree.name.replace(".png", "")):
                            ETexture_Animator = node
                        else:
                            ITexture_Animator = node
                            image_texture = node.node_tree.name.replace("Animated; ", "") + ".png"
                        Current_node_tree = node.node_tree

                    elif node.node_tree.name == "LabPBR Specular":
                        LabPBR_s = node
                    
                    elif node.node_tree.name == "Normal Map Fixed":
                        normal_map_node = node

                if node.type == "TEX_IMAGE" and node.image:
                    image_name = node.image.name.replace(".png", "")
                    if re.search(r'_n$', image_name):
                        normal_texture_node = node
                    elif re.search(r'_s$', image_name):
                        specular_texture_node = node
                    elif re.search(r'_e$', image_name):
                        emission_texture_node = node
                    else:
                        additional_texture_nodes.append(node)
            
            if ITexture_Animator:
                image_texture_node = None
            else:
                image_texture_node = detect_texture_node(PBSDF)
                
                if image_texture_node:
                    if image_texture_node in additional_texture_nodes:
                        additional_texture_nodes.remove(image_texture_node)
                    image_texture = image_texture_node.image.name
                else:
                    image_texture_node = None
                    image_texture = None

            if image_texture is None or (image_texture_node is None and ITexture_Animator is None):
                dprint(f"{material} skipped, image or image node not found", is_deep=True, zone="rp")
                continue

            try:
                relevant_node = image_texture_node or ITexture_Animator
                if abs(relevant_node.location.x - PBSDF.location.x) < 500:
                    relevant_node.location.x = PBSDF.location.x - 500
            except:
                pass

            # Image Texture Update
            if "MWO" in image_texture:
                continue

            if not r_props.use_i:
                animate_texture(image_texture_node, "", ITexture_Animator, Current_node_tree, object=selected_object)
            else:
                for pack, pack_info in resource_packs.items():
                    path, Type, enabled = pack_info["path"], pack_info["type"], pack_info["enabled"]
                    if not enabled or "Texture" not in Type or not os.path.exists(path):
                        continue

                    new_image_path = find_image(image_texture, path, obj_type, material.name)

                    if new_image_path is not None and os.path.isfile(new_image_path):
                        update_texture(new_image_path, image_texture)
                        animate_texture(image_texture_node, new_image_path, ITexture_Animator, Current_node_tree, object=selected_object)
                        image_path = new_image_path
                        
                        for additional_node in additional_texture_nodes:
                            additional_texture_name = additional_node.image.name
                            additional_path = find_image(additional_texture_name, path, obj_type, material.name)
                            if additional_path is not None and os.path.isfile(additional_path):
                                update_texture(additional_path, additional_texture_name)
                        
                        break

            # Normal Texture Update
            if r_props.use_n and r_props.use_additional_textures:
                for pack, pack_info in resource_packs.items():
                    path, Type, enabled = pack_info["path"], pack_info["type"], pack_info["enabled"]
                    if not enabled or "PBR" not in Type or not os.path.exists(path):
                        continue

                    if normal_texture_node is None:
                        normal_image_name = image_texture.replace(".png", "_n.png")
                    else:
                        normal_image_name = normal_texture_node.image.name

                    new_normal_image_path = fast_find_image([new_image_path], normal_image_name)

                    if new_normal_image_path is None and len([pack for pack in get_resource_packs().values() if "PBR" in pack.get("type", "")]) >= 1:
                        new_normal_image_path = find_image(normal_image_name, path, obj_type, material.name)
                    elif r_props.use_i == False:
                        new_normal_image_path = find_image(normal_image_name, path, obj_type, material.name)

                    if normal_texture_change(new_normal_image_path, normal_texture_node, normal_map_node, PBSDF, image_texture_node, image_path):
                        break
            else:
                if NTexture_Animator:
                    material.node_tree.nodes.remove(NTexture_Animator)
                    NTexture_Animator = None

                elif normal_texture_node:
                    if GetConnectedSocketTo(0, normal_texture_node):
                        material.node_tree.nodes.remove(GetConnectedSocketTo(0, normal_texture_node).node)
                        
                    material.node_tree.nodes.remove(normal_texture_node)
                    normal_texture_node = None

                if normal_map_node:
                    material.node_tree.nodes.remove(normal_map_node)
                    normal_map_node = None

            # Specular Texture Update
            if r_props.use_s and r_props.use_additional_textures:
                for pack, pack_info in resource_packs.items():
                    path, Type, enabled = pack_info["path"], pack_info["type"], pack_info["enabled"]
                    if not enabled or "PBR" not in Type or not os.path.exists(path):
                        continue

                    if specular_texture_change(path, specular_texture_node, LabPBR_s, new_normal_image_path, PBSDF, image_texture_node, image_texture, new_image_path, image_path):
                        break
            
            else:
                if STexture_Animator:
                    material.node_tree.nodes.remove(STexture_Animator)
                    STexture_Animator = None

                elif specular_texture_node:
                    if GetConnectedSocketTo(0, specular_texture_node):
                        material.node_tree.nodes.remove(GetConnectedSocketTo(0, specular_texture_node).node)

                    material.node_tree.nodes.remove(specular_texture_node)
                    specular_texture_node = None

                if LabPBR_s:
                    material.node_tree.nodes.remove(LabPBR_s)
                    LabPBR_s = None
            
            # Emission Texture Update
            if r_props.use_e and r_props.use_additional_textures:
                for pack, pack_info in resource_packs.items():
                    path, Type, enabled = pack_info["path"], pack_info["type"], pack_info["enabled"]
                    if not enabled or "PBR" not in Type or not os.path.exists(path):
                        continue
                        
                    if emission_texture_node is None:
                        emission_image_name = image_texture.replace(".png", "_e.png")
                    else:
                        emission_image_name = emission_texture_node.image.name

                    new_emission_image_path = fast_find_image([new_image_path, new_normal_image_path, new_specular_image_path], emission_image_name)

                    if new_emission_image_path is None and len([pack for pack in get_resource_packs().values() if "PBR" in pack.get("type", "")]) >= 1:
                        new_emission_image_path = find_image(emission_image_name, path, obj_type, material.name)
                    elif r_props.use_i == False or r_props.use_n == False or r_props.use_s == False:
                        new_emission_image_path = find_image(emission_image_name, path, obj_type, material.name)

                    if emission_texture_change(new_emission_image_path, emission_texture_node, PBSDF, image_texture_node, image_path):
                        break

            else:
                if ETexture_Animator:
                    material.node_tree.nodes.remove(ETexture_Animator)
                    ETexture_Animator = None

                elif emission_texture_node:
                    if GetConnectedSocketTo(0, emission_texture_node):
                        material.node_tree.nodes.remove(GetConnectedSocketTo(0, emission_texture_node).node)
                    material.node_tree.nodes.remove(emission_texture_node)
                    emission_texture_node = None