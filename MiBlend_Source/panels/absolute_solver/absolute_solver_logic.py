import os
import json
import traceback
from functools import wraps
import bpy


_absolute_solver_queue = []
_absolute_solver_processing = False
_absolute_solver_timer_scheduled = False
_reverse_all_changes_callback = None


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


def trigger_absolute_solver_on_error(operation_name: str):
    def decorator(execute):
        @wraps(execute)
        def wrapped_execute(operator, context):
            try:
                return execute(operator, context)
            except Exception:
                trigger_absolute_solver("e11", data=operation_name, tech_things=traceback.format_exc())
                return {'FINISHED'}

        return wrapped_execute

    return decorator


def _show_reverse_changes_failure():
    use_ru_text = bpy.app.translations.locale == "ru_RU"
    title = "Ошибка отката" if use_ru_text else "Rollback Failed"
    message = "MiBlend не удалось отменить изменения. Используйте Правка > Отменить." if use_ru_text else "MiBlend could not reverse the changes. Use Edit > Undo."

    def draw(self, _context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon='ERROR')


def schedule_reverse_all_changes(context) -> bool:
    global _reverse_all_changes_callback

    if _reverse_all_changes_callback:
        return False

    window = getattr(context, "window", None)
    if not window:
        return False

    areas = list(window.screen.areas)
    area = getattr(context, "area", None)
    if area not in areas:
        area = next((item for item in areas if item.type == 'VIEW_3D'), None)
    if not area and areas:
        area = areas[0]
    if not area:
        return False

    def reverse_all_changes():
        global _reverse_all_changes_callback

        try:
            if (not any(item == window for item in bpy.context.window_manager.windows)
                    or not any(item == area for item in window.screen.areas)):
                raise RuntimeError("The Blender window used by the failed operation is no longer available")

            with bpy.context.temp_override(window=window, area=area):
                if not bpy.ops.ed.undo.poll():
                    raise RuntimeError("Blender Undo is not available")

                result = bpy.ops.ed.undo()
                if 'FINISHED' not in result:
                    raise RuntimeError(f"Blender Undo returned {result}")
        except Exception:
            _show_reverse_changes_failure()
        finally:
            _reverse_all_changes_callback = None

        return None

    try:
        _reverse_all_changes_callback = reverse_all_changes
        bpy.app.timers.register(reverse_all_changes, first_interval=0.1)
    except Exception:
        _reverse_all_changes_callback = None
        _show_reverse_changes_failure()
        return False

    return True


def cancel_reverse_all_changes():
    global _reverse_all_changes_callback

    if _reverse_all_changes_callback and bpy.app.timers.is_registered(_reverse_all_changes_callback):
        bpy.app.timers.unregister(_reverse_all_changes_callback)

    _reverse_all_changes_callback = None
