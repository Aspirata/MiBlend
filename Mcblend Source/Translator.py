from .Data import *

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

    if Current_Language != "en_US":
        try:
            for Language, Translated_String in Translations[untranslated_string].items():
                if Language == Current_Language:
                    return Translated_String
            
            return untranslated_string
        
        except:
            return untranslated_string