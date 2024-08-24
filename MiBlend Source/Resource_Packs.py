from .MIB_API import *
from .Data import *
from .Utils.Absolute_Solver import Absolute_Solver
import sys, re
from distutils.version import LooseVersion

def get_resource_packs():
    return bpy.context.scene["resource_packs"]

def set_resource_packs(resource_packs):
    bpy.context.scene["resource_packs"] = resource_packs

    dprint(f"Resource Packs: {bpy.context.scene['resource_packs']}")

Launchers = {
    "Mojang": ".minecraft\\versions",
    "Modrinth": "com.modrinth.theseus\\meta\\versions",
    "TL Legacy": ".tlauncher\\legacy\\Minecraft\\game\\versions",
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
                    if (version := version_formatter(folder)) and os.path.isfile(instance_path := os.path.join(os.getenv('APPDATA'), path, folder, f"{folder}.jar")):
                        versions[version] = (folder, os.path.join(os.getenv('APPDATA'), path))
                        dprint(f"{instance_path} valid")
                    else:
                        dprint(f"{instance_path} invalid")
        
        if Preferences.mc_instances_path:
            folders = Preferences.mc_instances_path
            if os.path.isdir(folders):
                for folder in os.listdir(folders):
                    if (version := version_formatter(folder)) and os.path.isfile(os.path.join(os.getenv('APPDATA'), path, folder, f"{folder}.jar")):
                        versions[version] = (folder, Preferences.mc_instances_path)
                        dprint(f"{instance_path} valid")
                    else:
                        dprint(f"{instance_path} invalid")
            
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
        dprint(resource_packs[default_pack]["path"])
    else:
        print("MC instance not found")

    if Preferences.dev_tools and Preferences.dev_packs_path and Preferences.enable_custom_packs_path:
        resource_packs_dir = Preferences.dev_packs_path
    else:
        resource_packs_dir = resource_packs_directory
        
    default_pack = "Bare Bones 1.21"
    default_path = os.path.join(resource_packs_dir, default_pack)
    resource_packs[default_pack] = {"path": (default_path),"type": "Texture", "enabled": False}

    default_pack = "Better Emission"
    default_path = os.path.join(resource_packs_dir, default_pack)
    resource_packs[default_pack] = {"path": (default_path), "type": "PBR", "enabled": False}

    default_pack = "Embrace Pixels PBR"
    default_path = os.path.join(resource_packs_dir, default_pack)
    resource_packs[default_pack] = {"path": (default_path), "type": "PBR", "enabled": False}

@ Perf_Time
def apply_resources():

    resource_packs = get_resource_packs()
    r_props = bpy.context.scene.resource_properties


    def fast_find_image(textures_paths, texture_name):
        for texture_path in filter(None, textures_paths):
            dir_path = os.path.dirname(texture_path)
            predicted_texture = os.path.join(dir_path, texture_name)
            if os.path.isfile(predicted_texture):
                return predicted_texture
        return None
    

    def zip_unpacker(root_folder, image_name, file=None):
        extract_path = os.path.join(resource_packs_directory, os.path.splitext(file if file is not None else os.path.basename(root_folder))[0])
        with zipfile.ZipFile(root_folder, 'r') as zip_ref:

            for zip_info in filter(lambda x: ".png" in x.filename, zip_ref.infolist()):
                texture = os.path.basename(zip_info.filename)
                base_texture = texture.replace(".mcmeta", "")

                extracted_file_path = os.path.join(extract_path, zip_info.filename)

                if not os.path.isfile(extracted_file_path):
                    zip_ref.extract(zip_info, extract_path)

                if base_texture == image_name and texture.endswith(".png"):
                    return extracted_file_path

                if "grass" in image_name and (base_texture == f"short_{image_name}" or base_texture == image_name.replace("short_", "")) and texture.endswith(".png"):
                    return extracted_file_path
        return None
    

    def find_image(image_name, root_folder):
        if root_folder.endswith(('.zip', '.jar')):
            try:
                return zip_unpacker(root_folder, image_name)
            except zipfile.BadZipFile:
                print("Bad Zip File")
        else:
            for dirpath, _, files in os.walk(root_folder):
                for file in files:
                    if file == image_name:
                        return os.path.join(dirpath, file)
                    
                    if "grass" in image_name and (file == f"short_{image_name}" or file == image_name.replace("short_", "")):
                        return os.path.join(dirpath, file)

                    if file.endswith(('.zip', '.jar')):
                        try:
                            return zip_unpacker(os.path.join(dirpath, file), image_name, file)
                        except zipfile.BadZipFile:
                            print("Bad Zip File")
        return None


    def find_texture_users(texture):
        Texture_users = []
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for material in selected_object.data.materials:
                    if material and material.use_nodes:
                        for node in material.node_tree.nodes:
                            if node.type == 'TEX_IMAGE' and node.image == texture:
                                Texture_users.append(node)
        
        for group in bpy.data.node_groups:
            for node in group.nodes:
                if node.type == 'TEX_IMAGE' and node.image == texture:
                    Texture_users.append(node)
        
        return Texture_users


    def update_texture(new_image_path, image_texture, texture_node=None, colorspace=None):
        Users = None

        if image_texture in bpy.data.images:
            Users = find_texture_users(bpy.data.images[image_texture])
            if not r_props.ignore_dublicates:
                for texture in bpy.data.images:
                    if image_texture in texture.name:
                        parts = texture.name.split(".")
                        if len(parts) > 1 and parts[-1].isdigit() and texture.name.replace("." + str(parts[-1]), "") == image_texture:
                            Users.extend(find_texture_users(blender_texture := bpy.data.images.get(texture)))
                            bpy.data.images.remove(blender_texture)

            bpy.data.images.remove(bpy.data.images[image_texture], do_unlink=True)
        
        new_image_texture = os.path.basename(new_image_path)
        if texture_node is not None:
            if not texture_node.image:
                if image_texture in bpy.data.images:
                    texture_node.image = bpy.data.images[new_image_texture]
                else:
                    texture_node.image = bpy.data.images.load(new_image_path)

        if Users is not None:

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
                        Absolute_Solver("u006", colorspace)
            else:
                for user in Users:
                    user.image = user_texture


    def animate_texture(texture_node, new_image_texture_path, ITexture_Animator, Current_node_tree, image_path=None):
        Texture_Animator = None
        image_texture = bpy.data.images.get(os.path.basename(new_image_texture_path))

        for node in material.node_tree.nodes:
            if node.type == "GROUP":
                if "Texture Animator" in node.node_tree.name:
                    Texture_Animator = node

        if r_props.animate_textures:
            if int(image_texture.size[1] / image_texture.size[0]) != 1:

                interpolate = False
                frametime = 20
                animation_file = new_image_texture_path + ".mcmeta"
                if not os.path.isfile(animation_file) and image_path is not None:
                    animation_file = image_path + ".mcmeta"

                if os.path.isfile(animation_file):
                    with open(animation_file, 'r') as file:
                        data = json.load(file).get('animation', {})
                        if data.get('frametime') is not None:
                            frametime = data.get('frametime')

                        if data.get('interpolate') is not None:
                            interpolate = data.get('interpolate')
                    
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

                        if texture_node is not None:
                            for socket in GetConnectedSocketFrom("Color", texture_node):
                                material.node_tree.links.new(ITexture_Animator.outputs["Color"], socket)
                        
                            for socket in GetConnectedSocketFrom("Alpha", texture_node):
                                material.node_tree.links.new(ITexture_Animator.outputs["Alpha"], socket)

                            material.node_tree.nodes.remove(texture_node)
                    
                    ITexture_Animator.inputs["Frames"].default_value = int(image_texture.size[1] / image_texture.size[0])
                    ITexture_Animator.inputs["Only Fix UV"].default_value = False
                    ITexture_Animator.inputs["Frametime"].default_value = frametime
                    ITexture_Animator.inputs["Interpolate"].default_value = interpolate
                    ITexture_Animator.inputs["Only Fix UV"].default_value = r_props.only_fix_uv

                else:
                    if ITexture_Animator is not None:
                        texture_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')
                        texture_node.location = ITexture_Animator.location
                        texture_node.image = image_texture
                        texture_node.interpolation = "Closest"

                        for socket in GetConnectedSocketFrom("Color", ITexture_Animator):
                            material.node_tree.links.new(texture_node.outputs["Color"], socket)
                        
                        for socket in GetConnectedSocketFrom("Alpha", ITexture_Animator):
                            material.node_tree.links.new(texture_node.outputs["Alpha"], socket)

                        material.node_tree.nodes.remove(ITexture_Animator)

                    if Texture_Animator is None:
                        if "Texture Animator" not in bpy.data.node_groups:
                            try:
                                with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
                                    data_to.node_groups = ["Texture Animator"]
                            except:
                                Absolute_Solver("004", "Materials", traceback.format_exc())
                    
                        Texture_Animator = material.node_tree.nodes.new(type='ShaderNodeGroup')
                        Texture_Animator.node_tree = bpy.data.node_groups["Texture Animator"]
                        Texture_Animator.location = (texture_node.location.x - 200, texture_node.location.y - 60)

                    material.node_tree.links.new(Texture_Animator.outputs["Current Frame"], texture_node.inputs["Vector"])
                
                    Texture_Animator.inputs["Frames"].default_value = int(image_texture.size[1] / image_texture.size[0])
                    Texture_Animator.inputs["Only Fix UV"].default_value = False
                    Texture_Animator.inputs["Frametime"].default_value = frametime
                    Texture_Animator.inputs["Interpolate"].default_value = interpolate
                    Texture_Animator.inputs["Only Fix UV"].default_value = r_props.only_fix_uv
        else:
            if ITexture_Animator is not None:
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

    def normal_texture_change(path, normal_texture_node, normal_map_node, PBSDF, image_texture_node, image_texture, new_image_path, image_path):
        NTexture_Animator = None
        Current_node_tree = None

        if normal_texture_node is None:
            normal_image_name = image_texture.replace(".png", "_n.png")
        else:
            normal_image_name = normal_texture_node.image.name

        predicted_texture_path = fast_find_image([new_image_path], normal_image_name)
        if predicted_texture_path is None:
            new_normal_image_path = find_image(normal_image_name, path)
        else:
            if r_props.use_i:
                new_normal_image_path = predicted_texture_path
            else:
                new_normal_image_path = find_image(normal_image_name, path)
            

        if new_normal_image_path is not None:
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
                                image_texture = node.node_tree.name.replace("Animated; ", "") + ".png"
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
                Absolute_Solver("u006", "Non-Color")

            if normal_map_node is None:
                normal_map_node = material.node_tree.nodes.new("ShaderNodeNormalMap")
                normal_map_node.location = (normal_texture_node.location.x + 280, normal_texture_node.location.y)
                material.node_tree.links.new(normal_texture_node.outputs["Color"], normal_map_node.inputs["Color"])
                material.node_tree.links.new(normal_map_node.outputs["Normal"], PBSDF.inputs["Normal"])
            
            animate_texture(normal_texture_node, new_normal_image_path, NTexture_Animator, Current_node_tree, image_path)
            return new_normal_image_path
        return False
    
    def specular_texture_change(path, specular_texture_node, LabPBR_s, new_normal_image_path, PBSDF, image_texture_node, image_texture, new_image_path, image_path):
        STexture_Animator = None
        Current_node_tree = None

        if specular_texture_node is None:
            specular_image_name = image_texture.replace(".png", "_s.png")
        else:
            specular_image_name = specular_texture_node.image.name

        predicted_texture_path = fast_find_image([new_normal_image_path, new_image_path], specular_image_name)
        if predicted_texture_path is None and len([pack for pack in get_resource_packs().values() if "PBR" in pack.get("type", "")]) > 1:
            new_specular_image_path = find_image(specular_image_name, path)
        else:
            if not r_props.use_i or not r_props.use_n:
                new_specular_image_path = find_image(specular_image_name, path)
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
                material.node_tree.links.new(LabPBR_s.outputs["SSS"], PBSDF.inputs[PBSDF_compability("Subsurface Weight")])

                PBSDF.inputs["Subsurface Radius"].default_value = (1,1,1)

                PBSDF.subsurface_method = 'BURLEY'
            else:
                RemoveLinksFrom(LabPBR_s.outputs["SSS"])

            if r_props.emission:
                try:
                    try:
                        material.node_tree.links.new(image_texture_node.outputs["Color"], PBSDF.inputs[PBSDF_compability("Emission Color")])
                    except:
                        material.node_tree.links.new(ITexture_Animator.outputs["Color"], PBSDF.inputs[PBSDF_compability("Emission Color")])
                except:
                    pass
            
                material.node_tree.links.new(LabPBR_s.outputs["Emission Strength"], PBSDF.inputs["Emission Strength"])
            else:
                RemoveLinksFrom(LabPBR_s.outputs["Emission Strength"])
                RemoveLinksFrom(PBSDF.inputs[PBSDF_compability("Emission Color")])

            animate_texture(specular_texture_node, new_specular_image_path, STexture_Animator, Current_node_tree, image_path)
            return new_specular_image_path
        
        return False
        
    def emission_texture_change(path, emission_texture_node, new_normal_image_path, new_specular_image_path, PBSDF, image_texture_node, image_texture, new_image_path, image_path):
        ETexture_Animator = None
        ITexture_Animator = None
        Current_node_tree = None

        if emission_texture_node is None:
            emission_image_name = image_texture.replace(".png", "_e.png")
        else:
            emission_image_name = emission_texture_node.image.name

        predicted_texture_path = fast_find_image([new_image_path, new_normal_image_path, new_specular_image_path], emission_image_name)
        if predicted_texture_path is None and len([pack for pack in get_resource_packs().values() if "PBR" in pack.get("type", "")]) > 1:
            new_emission_image_path = find_image(emission_image_name, path)
        else:
            if r_props.use_i == False or r_props.use_n == False or r_props.use_s == False:
                new_emission_image_path = find_image(emission_image_name, path)
            else:
                new_emission_image_path = predicted_texture_path

        if new_emission_image_path is not None:
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
                            image_texture = node.node_tree.name.replace("Animated; ", "") + ".png"
                        Current_node_tree = node.node_tree

                try:
                    emission_texture_node.location = (image_texture_node.location.x, image_texture_node.location.y - 850)
                except:
                    emission_texture_node.location = (ITexture_Animator.location.x, ITexture_Animator.location.y - 850)

                emission_texture_node.interpolation = "Closest"

            update_texture(new_emission_image_path, emission_image_name, emission_texture_node)

            material.node_tree.links.new(emission_texture_node.outputs["Color"], PBSDF.inputs[PBSDF_compability("Emission Color")])
            material.node_tree.links.new(emission_texture_node.outputs["Alpha"], PBSDF.inputs["Emission Strength"])

            animate_texture(emission_texture_node, new_emission_image_path, ETexture_Animator, Current_node_tree, image_path)
            return True
        return False

    for selected_object in bpy.context.selected_objects:
        slot = 0
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                slot += 1
                if material is not None and material.use_nodes:
                    PBSDF = None
                    image_texture_node = None
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

                    for node in material.node_tree.nodes:

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
                            
                            if node.node_tree.name == "LabPBR Specular":
                                LabPBR_s = node

                        if node.type == "TEX_IMAGE" and node.image:

                            if node.type == "TEX_IMAGE" and node.image:
                                image_name = node.image.name.replace(".png", "")
                                if re.search(r'_n$', image_name):
                                    normal_texture_node = node
                                elif re.search(r'_s$', image_name):
                                    specular_texture_node = node
                                elif re.search(r'_e$', image_name):
                                    emission_texture_node = node
                                else:
                                    image_texture_node = node
                                    original_name = image_texture_node.image.name
                                    new_name = original_name.replace("_y", "")
                                    image_texture_node.image.name = new_name
                                    image_texture = image_texture_node.image.name

                        if node.type == "NORMAL_MAP":
                            normal_map_node = node

                    if image_texture is not None:
                        
                        try:
                            relevant_node = image_texture_node or ITexture_Animator
                            if abs(relevant_node.location.x - PBSDF.location.x) < 500:
                                relevant_node.location.x = PBSDF.location.x - 500
                        except:
                            pass
                        
                        # Image Texture Update
                        if r_props.use_i and "MWO" not in image_texture:
                            for pack, pack_info in resource_packs.items():
                                path, Type, enabled = pack_info["path"], pack_info["type"], pack_info["enabled"]
                                if not enabled or "Texture" not in Type:
                                    continue
                                
                                new_image_path = find_image(image_texture, path)

                                if new_image_path is not None and os.path.isfile(new_image_path):
                                        
                                    update_texture(new_image_path, image_texture)
                                        
                                    animate_texture(image_texture_node, new_image_path, ITexture_Animator, Current_node_tree)
                                    image_path = new_image_path
                                    break

                        # Normal Texture Update
                        if r_props.use_n and r_props.use_additional_textures and "MWO" not in image_texture:
                            for pack, pack_info in resource_packs.items():
                                path, Type, enabled = pack_info["path"], pack_info["type"], pack_info["enabled"]
                                if not enabled or "PBR" not in Type:
                                    continue

                                if new_normal_image_path := normal_texture_change(path, normal_texture_node, normal_map_node, PBSDF, image_texture_node, image_texture, new_image_path, image_path):
                                    break
                        else:
                            if NTexture_Animator is not None:
                                material.node_tree.nodes.remove(NTexture_Animator)
                                NTexture_Animator = None

                            if normal_texture_node is not None:
                                material.node_tree.nodes.remove(normal_texture_node)
                                normal_texture_node = None
                            
                            if normal_map_node is not None:
                                material.node_tree.nodes.remove(normal_map_node)
                                normal_map_node = None

                        # Specular Texture Update
                        if r_props.use_s and r_props.use_additional_textures and "MWO" not in image_texture:
                            for pack, pack_info in resource_packs.items():
                                path, Type, enabled = pack_info["path"], pack_info["type"], pack_info["enabled"]
                                if not enabled or "PBR" not in Type:
                                    continue

                                if new_specular_image_path := specular_texture_change(path, specular_texture_node, LabPBR_s, new_normal_image_path, PBSDF, image_texture_node, image_texture, new_image_path, image_path):
                                    break
                        
                        else:
                            if STexture_Animator is not None:
                                material.node_tree.nodes.remove(STexture_Animator)
                                STexture_Animator = None

                            if specular_texture_node is not None:
                                material.node_tree.nodes.remove(specular_texture_node)
                                specular_texture_node = None
                            
                            if LabPBR_s is not None:
                                material.node_tree.nodes.remove(LabPBR_s)
                                LabPBR_s = None
                        
                        # Emission Texture Update
                        if r_props.use_e and r_props.use_additional_textures and "MWO" not in image_texture:
                            for pack, pack_info in resource_packs.items():
                                path, Type, enabled = pack_info["path"], pack_info["type"], pack_info["enabled"]
                                if not enabled or "PBR" not in Type:
                                    continue

                                if emission_texture_change(path, emission_texture_node, new_normal_image_path, new_specular_image_path, PBSDF, image_texture_node, image_texture, new_image_path, image_path):
                                    break

                        else:
                            if ETexture_Animator is not None:
                                material.node_tree.nodes.remove(ETexture_Animator)
                                ETexture_Animator = None

                            if emission_texture_node is not None:
                                material.node_tree.nodes.remove(emission_texture_node)
                                emission_texture_node = None

                else:
                    Absolute_Solver("m002", slot)
        else:
            Absolute_Solver("m003", selected_object)