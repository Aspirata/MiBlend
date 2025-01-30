import bpy, json, os
from ..Data import utils_directory

def translate(untranslated_string):
    Current_Language = bpy.app.translations.locale

    with open(os.path.join(utils_directory, "languages", f"{Current_Language}.json"), "r") as file:
        Translations = json.load(file)

    return Translations.get(untranslated_string, untranslated_string)