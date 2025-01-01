import bpy

def Translate(untranslated_string):
    Current_Language = bpy.app.translations.locale
    return Translations.get(untranslated_string, {}).get(Current_Language, untranslated_string)

Translations = {
    "Use Normals": {
        "ru_RU": "Использовать Нормали:"
    },

    "Normals Settings": {
        "ru_RU": "Настройки Нормалей:"
    },

    "Bump Settings:": {
        "ru_RU": "Настройки Bump(a):"
    },
    
}
