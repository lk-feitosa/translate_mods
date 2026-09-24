"""
Provedores de tradução.
Ordem: Cache -> Ollama (primário) -> DeepL -> Google Translate (deep-translator).
"""

from __future__ import annotations

import json
import logging
import os
import re
import sqlite3
import time
from typing import Optional

import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

QUOTA_MARKERS = (
    "quota",
    "quota exceeded",
    "quota_exceeded",
    "456",
    "too many requests",
    "too many chars",
    "character limit",
    "billing period",
)

PLACEHOLDER_RE = re.compile(
    r"(§[0-9a-fk-orA-FK-OR]|%(?:\d+\$)?[sdif]|\{[^}]+\}|\$\{[^}]+\})"
)


def _looks_like_quota(exc: Exception) -> bool:
    text = str(exc).lower()
    name = type(exc).__name__.lower()
    if "quota" in name:
        return True
    return any(marker in text for marker in QUOTA_MARKERS)


class TranslationProvider:
    def translate(self, text: str) -> Optional[str]:
        raise NotImplementedError


class DeepLProvider(TranslationProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPL_API_KEY")
        self.available = False
        self.quota_exceeded = False
        self.translator = None

        if not self.api_key:
            return

        try:
            import deepl

            self.translator = deepl.Translator(self.api_key)
            self.available = True
            logger.info("✅ DeepL: Configurado (Fallback)")
        except ImportError:
            logger.warning("❌ DeepL: biblioteca não instalada (pip install deepl)")
        except Exception as e:
            logger.warning("❌ DeepL: Erro ao inicializar: %s", e)

    def disable_quota(self, reason: str) -> None:
        if self.quota_exceeded:
            return
        self.quota_exceeded = True
        self.available = False
        logger.warning("⚠️  DeepL: cota esgotada. Motivo: %s", reason)

    def translate(self, text: str) -> Optional[str]:
        if not self.available or self.quota_exceeded or self.translator is None:
            return None

        try:
            result = self.translator.translate_text(text, target_lang="PT-BR")
            return result.text
        except Exception as e:
            if _looks_like_quota(e):
                self.disable_quota(str(e))
            else:
                logger.warning("❌ DeepL: Erro na tradução: %s", e)
            return None


class GoogleTranslateProvider(TranslationProvider):
    MAX_CHARS = 4500

    def __init__(self):
        self.available = False
        self.client = None

        try:
            from deep_translator import GoogleTranslator

            self.client = GoogleTranslator(source="en", target="pt")
            self.available = True
        except Exception as e:
            logger.warning("❌ Google Translate: não disponível (%s)", e)

    def translate(self, text: str) -> Optional[str]:
        if not self.available or self.client is None:
            return None
        if len(text) > self.MAX_CHARS:
            return None

        last_error = None
        for attempt in range(3):
            try:
                translated = self.client.translate(text)
                if translated:
                    time.sleep(0.25)
                    return translated
            except Exception as e:
                last_error = e
                wait = 2.0 * (attempt + 1)
                logger.warning(
                    "❌ Google Translate: tentativa %s/3 falhou: %s",
                    attempt + 1,
                    e,
                )
                time.sleep(wait)

        if last_error:
            logger.warning("❌ Google Translate: desistindo: %s", last_error)
        return None


class OllamaProvider(TranslationProvider):
    def __init__(self, model: Optional[str] = None, host: Optional[str] = None):
        self.host = (host or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))
        self.available = False
        self._check_availability()

    def _check_availability(self) -> None:
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=3)
            if response.status_code != 200:
                logger.warning("⚠️  Ollama: HTTP %s em %s", response.status_code, self.host)
                return

            models = [
                item.get("name", "")
                for item in response.json().get("models", [])
            ]
            self.available = True
            has_model = any(
                name == self.model or name.startswith(f"{self.model}:")
                for name in models
            )
            if has_model:
                logger.info("✅ Ollama: Ativo (modelo %s)", self.model)
            else:
                logger.warning(
                    "⚠️  Ollama está no ar, mas o modelo '%s' não foi encontrado. "
                    "Rode: docker exec -it translate_mods-ollama ollama pull %s",
                    self.model,
                    self.model,
                )
        except Exception:
            logger.warning("⚠️  Ollama: Offline (primário desativado, usando fallbacks)")

    def translate(self, text: str) -> Optional[str]:
        if not self.available:
            return None

        prompt = (
            "Você é um tradutor técnico de Minecraft. Traduza o texto abaixo para Português Brasileiro (PT-BR).\n"
            "REGRAS:\n"
            "1. Mantenha placeholders intactos (%s, %d, §a, {}, ${}).\n"
            "2. Não traduza IDs técnicos (ex: item.minecraft.apple).\n"
            "3. Retorne APENAS a tradução final, sem aspas, markdown ou comentários.\n\n"
            f"Texto: {text}"
        )
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_predict": 256,
            },
        }

        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            if response.status_code != 200:
                logger.warning("❌ Ollama: HTTP %s", response.status_code)
                return None

            result = (response.json().get("response") or "").strip()
            if result.startswith('"') and result.endswith('"') and len(result) >= 2:
                result = result[1:-1]
            return result or None
        except requests.Timeout:
            logger.warning(
                "❌ Ollama: timeout após %ss. Aumente OLLAMA_TIMEOUT se o modelo for lento.",
                self.timeout,
            )
            return None
        except Exception as e:
            logger.warning("❌ Ollama: Erro na tradução: %s", e)
            return None


class TranslatorCore:
    """Ordem: Cache -> Ollama -> DeepL -> Google."""

    def __init__(self, db_path: Optional[str] = None, deepl_api_key: Optional[str] = None):
        self.conn = sqlite3.connect(db_path or os.getenv("CACHE_DB_PATH", "translation_cache.db"))
        self.cursor = self.conn.cursor()
        self._create_cache_table()

        self.ollama_provider = OllamaProvider()
        self.deepl_provider = DeepLProvider(deepl_api_key)
        self.google_provider = GoogleTranslateProvider()

        self.stats = {
            "cache_hits": 0,
            "ollama_hits": 0,
            "deepl_hits": 0,
            "google_hits": 0,
            "failed": 0,
        }

    def _create_cache_table(self) -> None:
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                translated_text TEXT,
                provider TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()
        try:
            self.cursor.execute('ALTER TABLE cache ADD COLUMN provider TEXT DEFAULT "manual"')
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

    def normalize_text(self, text):
        if text is None:
            return None
        if isinstance(text, str):
            return text
        if isinstance(text, (list, tuple)):
            parts = [self.normalize_text(item) for item in text]
            return ", ".join(part for part in parts if part)
        if isinstance(text, dict):
            return json.dumps(text, ensure_ascii=False)
        return str(text)

    def should_skip_translation(self, text: str) -> bool:
        stripped = text.strip()
        if not stripped:
            return True
        if stripped.startswith("[NÃO TRADUZIDO]"):
            return False
        if stripped.startswith(("http://", "https://")):
            return True
        without_codes = PLACEHOLDER_RE.sub("", stripped)
        letters = [c for c in without_codes if c.isalpha()]
        return len(letters) == 0

    def _protect_placeholders(self, text: str):
        mapping = {}

        def repl(match):
            token = f"[[PH{len(mapping)}]]"
            mapping[token] = match.group(0)
            return token

        return PLACEHOLDER_RE.sub(repl, text), mapping

    def _restore_placeholders(self, text: str, mapping: dict) -> str:
        restored = text
        for token, original in mapping.items():
            restored = restored.replace(token, original)
            restored = restored.replace(token.lower(), original)
        return restored

    def get_translation(self, text: str) -> Optional[str]:
        normalized_text = self.normalize_text(text)
        if not normalized_text:
            return None
        if self.should_skip_translation(normalized_text):
            return normalized_text

        self.cursor.execute(
            "SELECT translated_text FROM cache WHERE key = ?",
            (normalized_text,),
        )
        result = self.cursor.fetchone()
        if result and result[0] and not str(result[0]).startswith("[NÃO TRADUZIDO]"):
            self.stats["cache_hits"] += 1
            return result[0]

        protected, mapping = self._protect_placeholders(normalized_text)

        providers = (
            ("ollama", self.ollama_provider),
            ("deepl", self.deepl_provider),
            ("google", self.google_provider),
        )
        for name, provider in providers:
            if not getattr(provider, "available", False):
                continue
            translated = provider.translate(protected)
            if not translated:
                continue
            translated = self._restore_placeholders(translated, mapping)
            self.save_translation(normalized_text, translated, name)
            self.stats[f"{name}_hits"] += 1
            return translated

        self.stats["failed"] += 1
        preview = normalized_text[:50] + ("..." if len(normalized_text) > 50 else "")
        logger.warning("⚠️  Falha na tradução: %s", preview)
        return None

    def save_translation(self, text: str, translated_text: str, provider: str = "manual"):
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO cache (key, translated_text, provider) VALUES (?, ?, ?)",
                (text, translated_text, provider),
            )
            self.conn.commit()
        except Exception as e:
            logger.error("❌ Erro ao salvar no cache: %s", e)

    def get_stats(self) -> dict:
        total = sum(self.stats.values())
        return {
            **self.stats,
            "total": total,
            "cache_percent": (self.stats["cache_hits"] / total * 100) if total else 0,
            "ollama_percent": (self.stats["ollama_hits"] / total * 100) if total else 0,
            "deepl_percent": (self.stats["deepl_hits"] / total * 100) if total else 0,
            "google_percent": (self.stats["google_hits"] / total * 100) if total else 0,
            "deepl_quota_exceeded": self.deepl_provider.quota_exceeded,
            "google_available": self.google_provider.available,
            "ollama_available": self.ollama_provider.available,
        }

    def close(self):
        self.conn.close()
