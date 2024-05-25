from .Data import *

Translations = {
    "Warning !": {
        "ru_RU": "Внимание !"
    },

    "This option should be turned on only if you didn't add any extra textures to the materials": {
        "ru_RU": "Эта настройка должна быть включена только если вы не добавляли доп. текстур в материалы"
    },

    "This option can delete your custom textures !": {
        "ru_RU": "Эта настройка может удалить ваши текстуры"
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