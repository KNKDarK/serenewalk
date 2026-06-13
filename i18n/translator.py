import json
import os
import streamlit as st
from typing import Optional, Dict, Any

@st.cache_data
def _load_translation_data() -> Dict[str, Any]:
    translation_file = os.path.join(os.path.dirname(__file__), "translations.json")
    if os.path.exists(translation_file):
        with open(translation_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

class Translator:
    def __init__(self):
        self._translations = _load_translation_data()
        self._current_lang = "en"

    def set_language(self, lang_code: str):
        if lang_code in ["en", "te", "hi", "ja"]:
            self._current_lang = lang_code

    def get_language(self) -> str:
        return self._current_lang

    def t(self, key: str, **kwargs) -> str:
        keys = key.split(".")
        value = self._translations

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return key

        if isinstance(value, dict):
            lang_value = value.get(self._current_lang, value.get("en", key))
        else:
            lang_value = value

        if kwargs:
            try:
                return lang_value.format(**kwargs)
            except (KeyError, IndexError):
                return lang_value
        return lang_value

    def get_available_languages(self) -> list:
        return [
            {"code": "en", "name": "English", "native": "English"},
            {"code": "te", "name": "Telugu", "native": "తెలుగు"},
            {"code": "hi", "name": "Hindi", "native": "हिन्दी"},
            {"code": "ja", "name": "Japanese", "native": "日本語"},
        ]

@st.cache_resource
def get_translator():
    return Translator()

# For biological compatibility with existing code
translator = get_translator()

def t(key: str, **kwargs) -> str:
    return translator.t(key, **kwargs)

def set_language(lang_code: str):
    translator.set_language(lang_code)

def get_current_language() -> str:
    return translator.get_language()
