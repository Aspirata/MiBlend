import os
import json
import time
import re
import traceback
import bpy
from .resources.data import main_directory, nodes_file, EMISSIVE_MATERIALS, GRAY_BLOCKS


def get_preferences() -> bpy.types.AddonPreferences:
    return bpy.context.preferences.addons[__package__].preferences


def clamp(min_value: float, value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def draw_toggle_button(layout, property_path, property_name: str, is_small: bool = True):
    is_expanded = getattr(property_path, property_name)
    collapsed_arrow_icon = 'TRIA_LEFT' if is_small else 'TRIA_RIGHT'
    arrow_icon = 'TRIA_DOWN' if is_expanded else collapsed_arrow_icon

    layout.prop(property_path, property_name, icon_only=is_small, icon=arrow_icon, toggle=True)


def wrap_texture_node_in_closures(texture_node: bpy.types.Node, material: bpy.types.Material):
    return NotImplementedError("This function is currently not working properly because the closure zone api is hard")
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    color_targets = get_connected_socket_from("Color", texture_node)
    alpha_targets = get_connected_socket_from("Alpha", texture_node)
    x, y = texture_node.location

    for node in nodes:
        node.select = False

    node_editor = next(
        (area for area in bpy.context.screen.areas if area.type == "NODE_EDITOR"), None
    )
    space  = node_editor.spaces.active
    region = next((r for r in node_editor.regions if r.type == "WINDOW"), None)

    prev_tree = space.node_tree
    space.node_tree = material.node_tree

    with bpy.context.temp_override(area=node_editor, region=region, space_data=space):
        bpy.ops.node.add_closure_zone()

    new_nodes   = [n for n in nodes if n.select]
    closure_in  = next((n for n in new_nodes if "Input"  in n.bl_idname), None)
    closure_out = next((n for n in new_nodes if "Output" in n.bl_idname), None)

    with bpy.context.temp_override(area=node_editor, region=region, space_data=space):
        bpy.ops.node.closure_input_item_add(node_identifier=closure_in.identifier)

    item = closure_in.zone_items[-1]
    item.socket_type = "NodeSocketVector"
    item.name = "Vector"

    with bpy.context.temp_override(area=node_editor, region=region, space_data=space):
        bpy.ops.node.closure_output_item_add(node_identifier=closure_out.identifier)
        bpy.ops.node.closure_output_item_add(node_identifier=closure_out.identifier)

    closure_out.zone_items[-2].socket_type = "NodeSocketColor"
    closure_out.zone_items[-2].name = "Color"
    closure_out.zone_items[-1].socket_type = "NodeSocketFloat"
    closure_out.zone_items[-1].name = "Alpha"

    space.node_tree = prev_tree

    closure_in.location  = (x - 500, y)
    closure_out.location = (x + 250, y)

    less_than = nodes.new("ShaderNodeMath")
    less_than.operation = "LESS_THAN"
    less_than.inputs[1].default_value = 0.001
    less_than.location = (x - 350, y + 60)

    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (x - 350, y - 80)

    mix = nodes.new("ShaderNodeMix")
    mix.data_type = "VECTOR"
    mix.clamp_factor = True
    mix.location = (x - 180, y)

    links.new(closure_in.outputs["Vector"], less_than.inputs[0])
    links.new(less_than.outputs["Value"],   mix.inputs["Factor"])
    links.new(closure_in.outputs["Vector"], mix.inputs[4])
    links.new(tex_coord.outputs["UV"],      mix.inputs[5])
    links.new(mix.outputs[1],               texture_node.inputs["Vector"])

    links.new(texture_node.outputs["Color"], closure_out.inputs["Color"])
    links.new(texture_node.outputs["Alpha"], closure_out.inputs["Alpha"])

    evaluate = nodes.new("NodeEvaluateClosure")
    evaluate.location = (x + 450, y)

    links.new(closure_out.outputs["Closure"], evaluate.inputs["Closure"])

    if color_targets:
        for socket in color_targets:
            links.new(evaluate.outputs["Color"], socket)

    if alpha_targets:
        for socket in alpha_targets:
            links.new(evaluate.outputs["Alpha"], socket)


def dissolve_node(material, node_to_dissolve, node_to_dissolve_input: int | str | None = 0):
    if not node_to_dissolve:
        return
    
    node_tree = material.node_tree
    
    if node_to_dissolve_input is not None:
        all_output_links = []
        for output_socket in node_to_dissolve.outputs:
            all_output_links.extend(list(output_socket.links))
        
        source_socket = None
        if node_to_dissolve.inputs[node_to_dissolve_input].is_linked:
            source_socket = node_to_dissolve.inputs[node_to_dissolve_input].links[0].from_socket
        
        if source_socket:
            for link in all_output_links:
                node_tree.links.new(source_socket, link.to_socket)
    
    node_tree.nodes.remove(node_to_dissolve)


def inject_node(material: str, node_to_inject: object, target_node: object, target_node_input: int | str = 0, node_to_inject_input: int | str = 0, node_to_inject_output: int | str = 0):
    target_node_input_connection = get_connected_socket_to(target_node_input, target_node)
    if target_node_input_connection:
        if target_node_input_connection.node == node_to_inject:
            return
        material.node_tree.links.new(target_node_input_connection, node_to_inject.inputs[node_to_inject_input])

    material.node_tree.links.new(node_to_inject.outputs[node_to_inject_output], target_node.inputs[target_node_input])


def get_selected_asset() -> dict | None:
    from .panels.absolute_solver.absolute_solver_logic import trigger_absolute_solver

    current_index = bpy.context.scene.miblend_properties.assets_properties.asset_index
    items = bpy.context.scene.miblend_properties.assets_properties.asset_items

    if current_index < 0 or current_index >= len(items):
        return None

    try:
        return items[current_index]
    except Exception:
        trigger_absolute_solver("n00", tech_things=traceback.format_exc())
        return None


# Checks if the version_name is a valid version number and returns the formatted version number else returns None
def mc_version_formatter(version_name: str) -> str:
    from .panels.absolute_solver.absolute_solver_logic import trigger_absolute_solver

    try:
        version_parts = re.split(r'[ -]', version_name)
        if "snapshot" in version_parts:
            return ""

        for part in version_parts:
            if not any(char.isalpha() for char in part) and re.match(r'^\d{1,2}\.\d{1,2}(?:\.\d{1,2})?$', part):
                return part
        return ""
    except Exception:
        trigger_absolute_solver("n00", traceback.format_exc())


# Checks if material_or_texture_name in Array return (True, item in the list) else (False, None)
# Array filters: " ; " - not, " " - and
def name_in(Array: list, material_or_texture_name: str, is_texture=False, mode="in") -> tuple[bool, str | None]:
    if is_texture:
        name = format_texture_name(material_or_texture_name)
    else:
        name = format_material_name(material_or_texture_name)

    for item in Array:
        old_item = item
        if ";" in item:
            anti_keywords = item.split(" ; ")[1].split()
            if any(anti_keyword in name for anti_keyword in anti_keywords):
                dprint(f"Anti-Keyword: {anti_keywords} in {name}", is_deep=True)
                continue
            item = item.split(" ; ")[0]
        
        if " " in item:
            if all(keyword in name for keyword in item.split()):
                dprint(f"Keyword: {item} in {name}", is_deep=True)
                return (True, old_item)
        elif mode == "==":
            if any(item == name_part for name_part in name):
                dprint(f"Keyword: {item} in {name}", is_deep=True)
                return (True, old_item)
        else:
            if any(item in name_part for name_part in name):
                dprint(f"Keyword: {item} in {name}", is_deep=True)
                return (True, old_item)
            else:
                dprint(f"Keyword: {item} not in {name}", is_deep=True)

    dprint(f"Keyword: None in {name}", is_deep=True)
    return (False, None)


def get_resource_path() -> str:
    Preferences = get_preferences()
    if Preferences.dev_tools and os.path.exists(Preferences.dev_packs_path) and Preferences.enable_custom_packs_path:
        resource_packs_directory = Preferences.dev_packs_path
    else:
        resource_packs_directory = os.path.join(main_directory, "Resource Packs")
    
    return resource_packs_directory


def get_pack_info_properties(pack_name: str = "") -> dict:
    from .panels.absolute_solver.absolute_solver_logic import trigger_absolute_solver

    resource_packs_directory = get_resource_path()
    if not os.path.exists(resource_packs_directory):
        return {}
    
    packs_info_path = os.path.join(resource_packs_directory, "packs_info.json")
    try:
        with open(packs_info_path, "r") as file:
            data = json.load(file)
            
            if not pack_name:
                return data.keys()
            
            return data.get(pack_name, {})
    except FileNotFoundError:
        with open(packs_info_path, "w") as file:
            json.dump({}, file)
        return {}
    except Exception:
        trigger_absolute_solver("n00", traceback.format_exc())
        return {}


def is_code_ignored(code: str) -> bool:
    return code in bpy.context.scene.miblend_properties.absolute_solver_properties.ignored_codes.split()


def is_emissive(PBSDF: object, texture_name: str) -> bool:
    return PBSDF.inputs["Emission Strength"].default_value != 0 or name_in(EMISSIVE_MATERIALS.keys(), texture_name, True)[0]


def add_modifier(object: object, modifier_type_or_node_group: str, modifier_name: str ="", file: str = nodes_file) -> object:
    from .panels.absolute_solver.absolute_solver_logic import trigger_absolute_solver

    # Check if modifier already exists
    if modifier_name:
        existing_modifier = object.modifiers.get(modifier_name)
        if existing_modifier:
            return existing_modifier

    # Handle built-in Blender modifiers
    if modifier_type_or_node_group.isupper():
        existing_modifier = next((mod for mod in object.modifiers if mod.type == modifier_type_or_node_group), None)
        if existing_modifier:
            return existing_modifier
        
        name = modifier_name if modifier_name else modifier_type_or_node_group
        modifier = object.modifiers.new(name, type=modifier_type_or_node_group)
    
    # Handle geometry node groups
    else:
        existing_modifier = next((mod for mod in object.modifiers if mod.type == "NODES" and mod.node_group.name == modifier_type_or_node_group), None)
        if existing_modifier:
            return existing_modifier
        
        if modifier_type_or_node_group not in bpy.data.node_groups:
            try:
                with bpy.data.libraries.load(file, link=False) as (data_from, data_to):
                    data_to.node_groups = [modifier_type_or_node_group]
            except Exception as error:
                trigger_absolute_solver("e03", tech_things=error, data=file)

        name = modifier_name if modifier_name else modifier_type_or_node_group
        modifier = object.modifiers.new(name, type='NODES')
        modifier.node_group = bpy.data.node_groups[modifier_type_or_node_group]
    
    return modifier


def get_collections(data: object = None) -> list:
    collections_list = []

    if not data:
        data = bpy.data

    def add_collection(collection, level=0):
        collections_list.append((collection.name, level))
        for child in collection.children:
            add_collection(child, level + 1)

    for collection in data.collections:
        add_collection(collection)

    return collections_list


def create_node_group(place: object, node_tree_name: str, location: tuple = (0, 0), file: str = nodes_file, exists_check: bool = False, name: str ="") -> object:
    from .panels.absolute_solver.absolute_solver_logic import trigger_absolute_solver

    # Check for existing node group if requested
    if exists_check:
        existing_node = next((node for node in place.node_tree.nodes if node.type == "GROUP" and node.node_tree.name == node_tree_name), None)
        if existing_node:
            return existing_node
    
    # Load node group if not already in data
    if node_tree_name not in bpy.data.node_groups:
        try:
            with bpy.data.libraries.load(file, link=False) as (data_from, data_to):
                data_to.node_groups = [node_tree_name]
        except Exception as error:
            trigger_absolute_solver("e03", tech_things=error, data=file)

    # Create and configure new node
    group_node = place.node_tree.nodes.new(type='ShaderNodeGroup')
    if name:
        group_node.name = name
    
    group_node.node_tree = bpy.data.node_groups[node_tree_name]
    group_node.location = location

    return group_node


def detect_obj_type(obj_name: str = "", mat_name: str = "") -> str:
    obj = bpy.data.objects.get(obj_name)
    if not obj or obj.type != "MESH":
        dprint(f"Object {obj_name} not found", is_deep=True, zone="rp")
        return "unknown"

    miblend_id = obj.get("MiBlend ID", "")
    obj_name_lower = obj_name.lower()
    mat_name_lower = mat_name.lower()
    exporter = detect_world_exporter(obj)

    if "entity" in obj_name_lower or "entity" in mat_name_lower or miblend_id == "entity":
        dprint(f"{obj_name}; {mat_name} is an entity", is_deep=True, zone="rp")
        return "entity"

    elif exporter != "unknown" or "block" in obj_name_lower or "block" in mat_name_lower or miblend_id == "block":
        dprint(f"{obj_name}; {mat_name} is a block", is_deep=True, zone="rp")
        return "block"

    elif "item" in obj_name_lower or "item" in mat_name_lower or miblend_id == "item":
        dprint(f"{obj_name}; {mat_name} is an item", is_deep=True, zone="rp")
        return "item"
    
    dprint(f"{obj_name}; {mat_name} is unknown", is_deep=True, zone="rp")
    return "unknown"


def format_texture_name(texture_name: str, split: bool =True) -> str:
    if split:
        return format_duplicate_name(texture_name).replace(".png", "").lower().replace("-", "_").split("_")
    else:
        return format_duplicate_name(texture_name).replace(".png", "").lower().replace("-", "_")


def format_material_name(material_name: str, split: bool =True) -> str:
    if split:
        return format_duplicate_name(material_name).lower().replace("-", "_").split("_")
    else:
        return format_duplicate_name(material_name).lower().replace("-", "_")


def find_node(place: object, type_or_node_group_name: str) -> object | None:
    nodes_list = place.node_tree.nodes
    if type_or_node_group_name.isupper():
        matching_node = next((node for node in nodes_list if node.type == type_or_node_group_name), None)
    else:
        matching_node = next((node for node in nodes_list if node.type == "GROUP" and node.node_tree.name == type_or_node_group_name), None)
    
    return matching_node


def dprint(*messages: str, is_deep: bool =False, zone: str =None, separate: bool =False):
    try:
        Preferences = bpy.context.preferences.addons[__package__].preferences
        zones_dict = {"uas": Preferences.uas_debug_mode, "rp": Preferences.rp_debug_mode, "fw": Preferences.fw_debug_mode, "fm": Preferences.fm_debug_mode, "ui": Preferences.ui_debug_mode}
        
        if not Preferences.dev_tools or not Preferences.dprint:
            return
        
        if zone and not zones_dict.get(zone, False):
            return
            
        if is_deep and not Preferences.deep_debug:
            return
        
        print(*messages, sep="\n" if separate else "")
            
    except Exception as e:
        print(f"Debug print error: {str(e)}")


def is_duplicate(text: str, original_text: str = "") -> bool:
    parts = text.split(".")
    if len(parts) > 1 and parts[-1].isdigit():
        base_text = text.replace(f".{parts[-1]}", "")
        if not original_text:
            return True
        
        return base_text == original_text
    return False


def format_duplicate_name(text: str, original_text: str=None) -> str:
    parts = text.split(".")
    if len(parts) > 1 and parts[-1].isdigit():
        base_text = text.replace(f".{parts[-1]}", "")
        if not original_text:
            return base_text
        
        if base_text == original_text:
            return base_text
    return text


def is_gray(name: str, is_material: bool =False, mode: str ="all") -> bool:
    #dprint(f'{format_material_name(name)} vegetation: {name_in(GRAY_BLOCKS.get("vegetation"), name, not is_material)} \nrednstone: {name_in(GRAY_BLOCKS.get("redstone"), name, not is_material)} \nwater: {name_in(GRAY_BLOCKS.get("water"), name, not is_material)}', is_deep=True, zone="fw")
    result = False
    if mode == "all":
        result = name_in(GRAY_BLOCKS.get("vegetation"), name, not is_material)[0]
        result += name_in(GRAY_BLOCKS.get("redstone"), name, not is_material)[0]
        result += name_in(GRAY_BLOCKS.get("water"), name, not is_material)[0]
    elif mode == "vegetation":
        result = name_in(GRAY_BLOCKS.get("vegetation"), name, not is_material)[0]
    elif mode == "redstone":
        result = name_in(GRAY_BLOCKS.get("redstone"), name, not is_material)[0]
    elif mode == "water":
        result = name_in(GRAY_BLOCKS.get("water"), name, not is_material)[0]
    
    return bool(result)


def detect_texture_node(PBSDF: object) -> object | None:
    def get_all_linked_nodes(PBSDF):
        linked_nodes = []
        for input_name, input_socket in PBSDF.inputs.items():
            if input_socket.is_linked:
                for link in input_socket.links:
                    linked_nodes.append(link.from_node)
                    linked_nodes.extend(get_all_linked_nodes(link.from_node))
        return linked_nodes

    def get_linked_nodes(PBSDF, input_name):
        linked_nodes = []
        if input_name in PBSDF.inputs and PBSDF.inputs[input_name].is_linked:
            for link in PBSDF.inputs[input_name].links:
                linked_nodes.append(link.from_node)
                linked_nodes.extend(get_all_linked_nodes(link.from_node))
        return linked_nodes

    def traverse_nodes(PBSDF, input_name, visited=None):
        if visited is None:
            visited = set()
        
        if PBSDF in visited:
            return visited
        
        visited.add(PBSDF)
        
        linked_nodes = get_linked_nodes(PBSDF, input_name)
        for linked_node in linked_nodes:
            traverse_nodes(linked_node, input_name, visited)
        
        return visited
    
    connected_nodes = traverse_nodes(PBSDF, "Base Color")
    for n in connected_nodes:
        if (n.type == "GROUP" and "Animated;" in n.node_tree.name) or (n.type == "TEX_IMAGE" and n.image):
            return n
    
    return None


def get_nodes_list(material_or_node_group: object, is_recursive: bool =False) -> list:
    nodes_list = []
    
    if hasattr(material_or_node_group, 'use_nodes') and not material_or_node_group.use_nodes:
        return []

    for node in material_or_node_group.node_tree.nodes:
        nodes_list.append(node)
        if node.type == 'GROUP' and node.node_tree and is_recursive:
            nodes_list.extend(get_nodes_list(node))

    return nodes_list


def detect_image_texture(PBSDF: object) -> object | None:
    def get_all_linked_nodes(PBSDF):
        linked_nodes = []
        for input_name, input_socket in PBSDF.inputs.items():
            if input_socket.is_linked:
                for link in input_socket.links:
                    linked_nodes.append(link.from_node)
                    linked_nodes.extend(get_all_linked_nodes(link.from_node))
        return linked_nodes

    def get_linked_nodes(PBSDF, input_name):
        linked_nodes = []
        if input_name in PBSDF.inputs and PBSDF.inputs[input_name].is_linked:
            for link in PBSDF.inputs[input_name].links:
                linked_nodes.append(link.from_node)
                linked_nodes.extend(get_all_linked_nodes(link.from_node))
        return linked_nodes

    def traverse_nodes(PBSDF, input_name, visited=None):
        if visited is None:
            visited = set()
        
        if PBSDF in visited:
            return visited
        
        visited.add(PBSDF)
        
        linked_nodes = get_linked_nodes(PBSDF, input_name)
        for linked_node in linked_nodes:
            traverse_nodes(linked_node, input_name, visited)
        
        return visited
    
    connected_nodes = traverse_nodes(PBSDF, "Base Color")
    for n in connected_nodes:
        if n.type == "GROUP" and "Animated;" in n.node_tree.name:
            return bpy.data.images.get(n.node_tree.name.replace("Animated; ", "") + ".png")
                
        if n.type == "TEX_IMAGE" and n.image:
            return n.image

    return None


def detect_world_exporter(world_obj: object) -> str:
    exporter = "unknown"

    if not world_obj.data.materials:
        return exporter
        
    for mat in world_obj.data.materials:
        mat_name = mat.name
        if mat_name.startswith("MAT_"):
            exporter = "miex"
            break
        elif "MWO" in mat_name or mat_name.count('-') == 0:
            exporter = "mineways"
            break
        elif mat_name.count('-') == 1:
            exporter = "jmc2obj"
            break
    
    dprint(f"Detected {exporter} exporter for {world_obj.name}", is_deep=True)
    return exporter


def separate_mesh_by_material(obj: object, material: object = None) -> object:
    from .panels.absolute_solver.absolute_solver_logic import trigger_absolute_solver

    try:
        obj_name = obj.name if obj.name.split('__')[0] else "World" + obj.name
        new_obj = None

        bpy.ops.object.mode_set(mode='OBJECT')

        # Early return if separation not needed
        if len(obj.material_slots) <= 1 or not obj.material_slots:
            return obj

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Create collection if needed
        collection_name = obj_name.split('__')[0].replace("Main | ", "") or "World"
        collection = bpy.data.collections.get(collection_name)
        if not collection:
            collection = bpy.data.collections.new(collection_name)
            obj.users_collection[-1].children.link(collection)
            
            # Move object to new collection
            for col in obj.users_collection:
                col.objects.unlink(obj)
            collection.objects.link(obj)

        if material:
            for i, mat in enumerate(obj.data.materials):
                if mat == material:
                    bpy.context.object.active_material_index = i
                    break

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.object.material_slot_select()
            bpy.ops.mesh.separate(type="SELECTED")
            bpy.ops.object.mode_set(mode='OBJECT')

            # Find separated object
            new_obj = next((o for o in bpy.context.selected_objects if o != obj), None)
            if new_obj:
                # Clean up and rename original object
                bpy.context.view_layer.objects.active = obj
                if not obj.name.startswith("Main | "):
                    obj.name = f"Main | {obj_name}"
                bpy.ops.object.material_slot_remove()

                # Clean up and rename new object
                bpy.context.view_layer.objects.active = new_obj
                bpy.ops.object.material_slot_remove_unused()
                new_obj.name = f"{material.name} | {obj_name.replace('Main | ', '')}"

        else:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.separate(type="MATERIAL")
            bpy.ops.object.mode_set(mode='OBJECT')

            # Rename separated objects
            for new_obj in collection.objects:
                if new_obj in bpy.context.selected_objects and obj_name in new_obj.name:
                    mat_name = new_obj.material_slots[0].material.name if new_obj.material_slots else "Unknown"
                    new_obj.name = f"{mat_name} | {obj_name.replace('Main | ', '')}"

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.update()
        return new_obj

    except Exception:
        trigger_absolute_solver("n00", traceback.format_exc())
        return None


def perf_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time > 0.001 and bpy.context.preferences.addons[__package__].preferences.dev_tools and bpy.context.preferences.addons[__package__].preferences.perf_time:
            dprint(f"{func.__name__}() took {end_time - start_time:.4f} seconds to complete.")
    return wrapper


def get_connected_socket_from(output: str, node: object) -> list:
    from .panels.absolute_solver.absolute_solver_logic import trigger_absolute_solver

    try:
        output_socket = node.outputs.get(output)

        if not output_socket:
            return None
        
        if not output_socket.is_linked:
            return None
        
        return [link.to_socket for link in output_socket.links]
    except Exception as error:
        trigger_absolute_solver("n00", error)


def get_connected_socket_to(input: int | str, node: object) -> object | None:
    from .panels.absolute_solver.absolute_solver_logic import trigger_absolute_solver
    
    try:
        if isinstance(input, int):
            if input >= len(node.inputs):
                return None
            else:
                input_socket = node.inputs[input]
        else:
            input_socket = node.inputs.get(input, None)
        
        if not input_socket:
            return None
        
        if not input_socket.is_linked:
            return None
        
        link = input_socket.links[0]
        return link.from_socket
    except Exception as error:
        trigger_absolute_solver("n00", error)


def remove_links_from(sockets: object):
    try:
        for socket in sockets:
            for link in socket.links:
                socket.node.id_data.links.remove(link)
    except Exception:
        for link in sockets.links:
            sockets.node.id_data.links.remove(link)
