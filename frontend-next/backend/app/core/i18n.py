"""
Módulo para la gestión de internacionalización (i18n) de la aplicación.
"""

from pathlib import Path
from typing import Dict, Optional
import json
from fastapi import Request
from fastapi.responses import JSONResponse

class I18nManager:
    def __init__(self, translations_dir: str = "translations"):
        self.translations: Dict[str, Dict] = {}
        self.translations_dir = Path(translations_dir)
        self.default_language = "es"
        self.supported_languages = ["es", "en"]
        self._load_translations()

    def _load_translations(self):
        """Carga las traducciones desde los archivos JSON."""
        for lang in self.supported_languages:
            try:
                file_path = self.translations_dir / f"{lang}.json"
                with open(file_path, "r", encoding="utf-8") as f:
                    self.translations[lang] = json.load(f)
            except FileNotFoundError:
                print(f"Warning: Translation file for {lang} not found")
                self.translations[lang] = {}

    def get_text(self, key: str, lang: str = None) -> str:
        """
        Obtiene el texto traducido para una clave específica.
        
        Args:
            key (str): Clave de traducción
            lang (str, optional): Código de idioma. Defaults to None.
            
        Returns:
            str: Texto traducido
        """
        lang = lang or self.default_language
        if lang not in self.translations:
            lang = self.default_language
            
        # Navega a través de claves anidadas (e.g., "errors.not_found")
        keys = key.split(".")
        value = self.translations[lang]
        for k in keys:
            value = value.get(k, key)
            if not isinstance(value, dict):
                break
        return value if isinstance(value, str) else key

    async def get_language(self, request: Request) -> str:
        """
        Determina el idioma a usar basado en la solicitud HTTP.
        
        Args:
            request (Request): Solicitud FastAPI
            
        Returns:
            str: Código de idioma
        """
        # Intenta obtener el idioma de diferentes fuentes
        lang = None
        
        # 1. De los parámetros de consulta
        lang = request.query_params.get("lang")
        if lang in self.supported_languages:
            return lang
            
        # 2. Del encabezado Accept-Language
        accept_language = request.headers.get("accept-language")
        if accept_language:
            # Toma el primer idioma de la lista
            lang = accept_language.split(",")[0].split("-")[0]
            if lang in self.supported_languages:
                return lang
        
        # 3. Del idioma por defecto
        return self.default_language

    def translate_response(self, response_data: Dict, lang: str) -> Dict:
        """
        Traduce todas las cadenas en un diccionario de respuesta.
        
        Args:
            response_data (Dict): Datos de respuesta
            lang (str): Código de idioma
            
        Returns:
            Dict: Datos traducidos
        """
        if isinstance(response_data, dict):
            return {k: self.translate_response(v, lang) for k, v in response_data.items()}
        elif isinstance(response_data, list):
            return [self.translate_response(item, lang) for item in response_data]
        elif isinstance(response_data, str):
            return self.get_text(response_data, lang)
        return response_data

# Instancia global del gestor de i18n
i18n = I18nManager()

def translate_response_middleware(request: Request, call_next):
    """
    Middleware para traducir automáticamente las respuestas.
    """
    response = await call_next(request)
    
    if isinstance(response, JSONResponse):
        lang = await i18n.get_language(request)
        response.body = json.dumps(
            i18n.translate_response(response.body, lang)
        ).encode()
        
    return response
