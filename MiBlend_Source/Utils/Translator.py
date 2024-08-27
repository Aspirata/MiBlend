import bpy

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

Availible_Translations = {
    "Russian": "ru_RU",
}

def Translate(untranslated_string):
    Current_Language = bpy.app.translations.locale

    try:
        return Translations[untranslated_string][Current_Language]
    except:
        return untranslated_string