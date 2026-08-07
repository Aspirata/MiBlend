import os
import json
import traceback
import bpy


_absolute_solver_queue = []
_absolute_solver_processing = False
_absolute_solver_timer_scheduled = False


def _process_absolute_solver_queue():
    from ...mib_utils import get_preferences
    global _absolute_solver_processing, _absolute_solver_timer_scheduled

    if _absolute_solver_processing:
        return 0.1

    _absolute_solver_processing = True
    queued_calls = list(_absolute_solver_queue)
    _absolute_solver_queue.clear()
    try:
        preferences = get_preferences()
        use_ru_text: str = "_ru" if bpy.app.translations.locale == "ru_RU" else ""
        call_data = {}
        try:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "absolute_solver_list.json"), "r", encoding="utf-8") as file:
                data_json = json.load(file)
                critical_error_name = data_json.get("errors", {}).get("00", {}).get("Name" + use_ru_text, "Critical Error")
                critical_error_description = data_json.get("errors", {}).get("00", {}).get("Description" + use_ru_text, "Unknown error occurred: {Data}")

                for code, Data, tech_things in queued_calls:
                    if code in call_data or code in bpy.context.scene.miblend_properties.absolute_solver_properties.ignored_codes.split():
                        continue
                    
                    trigger_type = code[0]
                    trigger_number = code[1:]
                    
                    if trigger_type == "w":
                        if not preferences.show_warnings:
                            continue
                        name = data_json.get("warnings", {}).get(trigger_number, {}).get("Name" + use_ru_text, "")
                        description = data_json.get("warnings", {}).get(trigger_number, {}).get("Description" + use_ru_text, "")
                        solutions = data_json.get("warnings", {}).get(trigger_number, {}).get("Solutions", "")
                    elif trigger_type == "e":
                        name = data_json.get("errors", {}).get(trigger_number, {}).get("Name" + use_ru_text, "")
                        description = data_json.get("errors", {}).get(trigger_number, {}).get("Description" + use_ru_text, "")
                        solutions = data_json.get("errors", {}).get(trigger_number, {}).get("Solutions", "")
                    elif trigger_type == "n":
                        name = data_json.get("null", {}).get(trigger_number, {}).get("Name" + use_ru_text, "")
                        description = data_json.get("null", {}).get(trigger_number, {}).get("Description" + use_ru_text, "")
                        solutions = ""

                    if name and description:
                        call_data[code] = f"{code}:::{name}:::{description.format(Data=Data)}:::{solutions}:::{tech_things}"
                    else:
                        call_data[code] = f"e00:::{critical_error_name}:::{critical_error_description.format(Data=code)}::::Code not found: {code}"
        
        except Exception:
            call_data["e00"] = f"e00:::Critical Error:::Failed to load error data::::{traceback.format_exc()}"
        
        if call_data:
            result = bpy.ops.miblend.absolute_solver('INVOKE_DEFAULT', call_data="|||".join(call_data.values()))
            if 'CANCELLED' in result:
                raise RuntimeError("Absolute Solver popup was cancelled")
    except Exception:
        print(f"Absolute Solver processing failed:\n{traceback.format_exc()}")
    finally:
        _absolute_solver_processing = False
        _absolute_solver_timer_scheduled = bool(_absolute_solver_queue)

    return 0.1 if _absolute_solver_timer_scheduled else None


def trigger_absolute_solver(code: str, tech_things: str = "", data: object = ""):
    global _absolute_solver_timer_scheduled

    _absolute_solver_queue.append((code, data, tech_things))
    if _absolute_solver_timer_scheduled:
        return

    _absolute_solver_timer_scheduled = True
    try:
        bpy.app.timers.register(_process_absolute_solver_queue, first_interval=0.1)
    except Exception:
        _absolute_solver_timer_scheduled = False
        _process_absolute_solver_queue()


def cancel_absolute_solver_queue():
    global _absolute_solver_processing, _absolute_solver_timer_scheduled

    if bpy.app.timers.is_registered(_process_absolute_solver_queue):
        bpy.app.timers.unregister(_process_absolute_solver_queue)

    _absolute_solver_queue.clear()
    _absolute_solver_processing = False
    _absolute_solver_timer_scheduled = False
