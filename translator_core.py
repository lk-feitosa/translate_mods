import sqlite3
import json

class TranslatorCore:
    def __init__(self, db_path='translation_cache.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                translated_text TEXT
            )
        ''')
        self.conn.commit()

    def get_translation(self, text):
        self.cursor.execute('SELECT translated_text FROM cache WHERE key = ?', (text,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def save_translation(self, text, translated_text):
        self.cursor.execute('INSERT OR REPLACE INTO cache (key, translated_text) VALUES (?, ?)', (text, translated_text))
        self.conn.commit()

    def translate_batch(self, texts, engine='google'):
        # Placeholder para integração com API (DeepL/Gemini/Google)
        # Por enquanto, retorna o próprio texto simulando um "não traduzido"
        return {text: f"[Traduzido] {text}" for text in texts}
