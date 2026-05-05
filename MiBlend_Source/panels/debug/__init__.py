from .debug_ui import MIBLEND_PT_debug
from .debug_operators import (MIBLEND_OT_clear_ignored_codes, MIBLEND_OT_trigger_absolute_solver_error,
                             MIBLEND_OT_open_miblend_folder, MIBLEND_OT_remove_attribute)

classes = [
    MIBLEND_PT_debug,
    MIBLEND_OT_clear_ignored_codes,
    MIBLEND_OT_trigger_absolute_solver_error,
    MIBLEND_OT_open_miblend_folder,
    MIBLEND_OT_remove_attribute
]