import os
import json
import time
import traceback
import bpy


def translate(untranslated_string: str) -> str:
    current_language = bpy.app.translations.locale

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "languages", f"{current_language}.json"), "r") as file:
        translations_dict: dict[str, str] = json.load(file)

    return translations_dict.get(untranslated_string, untranslated_string)


def trigger_absolute_solver(code: str, tech_things: str = "", data: str = ""):
    from ...mib_utils import get_preferences
    Preferences = get_preferences()
    
    if not hasattr(trigger_absolute_solver, 'call_queue'):
        trigger_absolute_solver.call_queue = []
        trigger_absolute_solver.last_call_time = 0
        trigger_absolute_solver.is_processing = False
    
    current_time = time.time()
    
    trigger_absolute_solver.call_queue.append((code, data))
    
    if (current_time - trigger_absolute_solver.last_call_time >= 0.1) and not trigger_absolute_solver.is_processing:
        trigger_absolute_solver.is_processing = True

        call_data = {}
        try:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "absolute_solver_list.json"), "r") as file:
                data_json = json.load(file)
                critical_error_name = data_json.get("errors", {}).get("00", {}).get("Name", "Critical Error")
                critical_error_description = translate(data_json.get("errors", {}).get("00", {}).get("Description", "Unknown error occurred: {Data}"))

                for code, Data in trigger_absolute_solver.call_queue:
                    if code in call_data or code in bpy.context.scene.miblend_properties.absolute_solver_properties.ignored_codes.split():
                        continue
                    
                    trigger_type = code[0]
                    trigger_number = code[1:]
                    
                    if trigger_type == "w":
                        if not Preferences.show_warnings:
                            continue
                        name = data_json.get("warnings", {}).get(trigger_number, {}).get("Name")
                        description = data_json.get("warnings", {}).get(trigger_number, {}).get("Description")
                        solutions = data_json.get("warnings", {}).get(trigger_number, {}).get("Solutions", "")
                    elif trigger_type == "e":
                        name = data_json.get("errors", {}).get(trigger_number, {}).get("Name")
                        description = data_json.get("errors", {}).get(trigger_number).get("Description")
                        solutions = data_json.get("errors", {}).get(trigger_number, {}).get("Solutions", "")
                    elif trigger_type == "n":
                        name = data_json.get("null", {}).get(trigger_number, {}).get("Name")
                        description = data_json.get("null", {}).get(trigger_number, {}).get("Description")
                        solutions = ""
                    
                    description = translate(description)

                    if name and description:
                        call_data[code] = f"{code}:::{name}:::{description.format(Data=Data)}:::{solutions}:::{tech_things}"
                    else:
                        call_data[code] = f"e00:::{critical_error_name}:::{critical_error_description.format(Data=code)}::::Code not found: {code}"
        
        except Exception:
            call_data["e00"] = f"e00:::Critical Error:::Failed to load error data::::{traceback.format_exc()}"
        
        if call_data:
            result = bpy.ops.miblend.absolute_solver('INVOKE_DEFAULT', call_data="|||".join(call_data.values()))
            if 'CANCELLED' in result:
                raise Exception("Cancelled by user")
        
        trigger_absolute_solver.call_queue.clear()
        trigger_absolute_solver.last_call_time = current_time
        trigger_absolute_solver.is_processing = False
