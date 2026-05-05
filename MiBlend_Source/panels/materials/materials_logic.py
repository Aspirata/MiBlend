import os
import zipfile
import bpy
from ..absolute_solver.absolute_solver_logic import trigger_absolute_solver
from ...mib_utils import get_preferences, is_code_ignored, perf_time
from ...resources.data import main_directory


@perf_time
def fix_materials():
    for selected_object in bpy.context.selected_objects:
        if selected_object.type != "MESH" and not is_code_ignored("w01") and get_preferences().show_warnings:
            trigger_absolute_solver("w01", data=selected_object)
            continue
        
        elif selected_object.type != "MESH":
            continue

        for slot, material in enumerate(selected_object.data.materials):
            if material is None or not material.use_nodes:
                continue

            image_texture_node = None
            PBSDF = None

            material.blend_method = 'HASHED'

            for node in material.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    image_texture_node = node
                    node.interpolation = "Closest"

                if node.type == "BSDF_PRINCIPLED":
                    PBSDF = node

            if image_texture_node and PBSDF:
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], PBSDF.inputs["Alpha"])


@perf_time
def swap_textures(folder_path):
    def find_image(image_name, root_folder):
        for dirpath, _, files in os.walk(root_folder):
            for file in files:
                if file == image_name:
                    return os.path.join(dirpath, file)

                if file.endswith(('.zip', '.jar')):
                    archive_path = os.path.join(dirpath, file)
                    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                        file_list = zip_ref.namelist()
                        if image_name in file_list:
                            extract_path = os.path.join(main_directory, 'Resource Packs', os.path.splitext(file)[0])
                            extracted_file_path = zip_ref.extract(image_name, extract_path)
                            return extracted_file_path
                
                format_fixed = os.path.join(dirpath, "short_" + image_name)
                if os.path.isfile(format_fixed):
                    return format_fixed

                format_fixed = os.path.join(dirpath, image_name.replace("short_", ""))
                if os.path.isfile(format_fixed):
                    return format_fixed
            
        return None
    
    for selected_object in bpy.context.selected_objects:
        if selected_object.type != "MESH" and not is_code_ignored("w01") and get_preferences().show_warnings:
            trigger_absolute_solver("w01", selected_object)
            continue
        elif selected_object.type != "MESH":
            continue

        for slot, material in enumerate(selected_object.data.materials):
            if material is None or not material.use_nodes:
                continue

            for node in material.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image is not None:
                    new_image_path = find_image(node.image.name, folder_path)
                    if new_image_path is not None:
                        if node.image.name in bpy.data.images:
                            bpy.data.images.remove(bpy.data.images[node.image.name], do_unlink=True)

                        node.image = bpy.data.images.load(new_image_path)
