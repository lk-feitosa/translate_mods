"""
Módulo de tradução com suporte a múltiplas APIs
- DeepL (Premium - Requer API key)
- Google Translate (Gratuito - Fallback)
"""

import os
import sqlite3
import logging
from typing import Optional, Dict
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()


class TranslationProvider:
    """Interface base para provedores de tradução."""
    
    def translate(self, text: str) -> Optional[str]:
        """Traduz texto para PT_BR."""
        raise NotImplementedError


class DeepLProvider(TranslationProvider):
    """Provedor de tradução usando DeepL API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializar DeepL Provider.
        
        Args:
            api_key: Chave de API do DeepL (ou usar DEEPL_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('DEEPL_API_KEY')
        self.available = False
        
        if not self.api_key:
            logger.warning("❌ DeepL: API key não encontrada. Configure DEEPL_API_KEY")
            return
        
        try:
            import deepl
            self.translator = deepl.Translator(self.api_key)
            self.available = True
            logger.info("✅ DeepL: Inicializado com sucesso")
        except ImportError:
            logger.warning("❌ DeepL: Biblioteca não instalada (pip install deepl)")
        except Exception as e:
            logger.warning(f"❌ DeepL: Erro ao inicializar: {e}")
    
    def translate(self, text: str) -> Optional[str]:
        """Traduz usando DeepL."""
        if not self.available:
            return None
        
        try:
            result = self.translator.translate_text(text, target_lang="PT-BR")
            return result.text
        except Exception as e:
            logger.warning(f"❌ DeepL: Erro na tradução: {e}")
            return None


class GoogleTranslateProvider(TranslationProvider):
    """Provedor de tradução usando Google Translate (gratuito)."""
    
    def __init__(self):
        """Inicializar Google Translate Provider."""
        self.available = False
        
        try:
            # Tentar importar google.cloud (requer credenciais)
            from google.cloud import translate_v2
            self.client = translate_v2.Client()
            self.available = True
            self.provider = "google_cloud"
            logger.info("✅ Google Translate (Cloud): Inicializado")
        except ImportError:
            try:
                # Fallback para google-generativeai
                import google.generativeai as genai
                api_key = os.getenv('GOOGLE_API_KEY')
                if api_key:
                    genai.configure(api_key=api_key)
                    self.client = genai
                    self.available = True
                    self.provider = "google_generativeai"
                    logger.info("✅ Google Generative AI: Inicializado")
                else:
                    logger.warning("❌ Google API: GOOGLE_API_KEY não configurada")
            except ImportError:
                try:
                    # Fallback para googletrans (gratuito, sem API)
                    from googletrans import Translator
                    self.client = Translator()
                    self.available = True
                    self.provider = "googletrans"
                    logger.info("✅ GoogleTrans (Gratuito): Inicializado")
                except ImportError:
                    logger.warning("❌ Google Translate: Nenhum provedor disponível")
    
    def translate(self, text: str) -> Optional[str]:
        """Traduz usando Google Translate."""
        if not self.available:
            return None
        
        try:
            if self.provider == "google_cloud":
                result = self.client.translate_text(text, target_language="pt-BR")
                return result.get('translatedText')
            
            elif self.provider == "google_generativeai":
                prompt = f"Traduza para português brasileiro (PT-BR) sem explicações extras:\n{text}"
                response = self.client.generate_content(prompt)
                return response.text
            
            elif self.provider == "googletrans":
                result = self.client.translate(text, src_lang='en', dest_lang='pt')
                return result['text']
        
        except Exception as e:
            logger.warning(f"❌ Google Translate: Erro na tradução: {e}")
        
        return None


class TranslatorCore:
    """
    Núcleo de tradução com suporte a múltiplas APIs e cache.
    Usa DeepL como primário, Google Translate como fallback.
    """
    
    def __init__(self, db_path='translation_cache.db', deepl_api_key: Optional[str] = None):
        """
        Inicializar TranslatorCore.
        
        Args:
            db_path: Caminho para banco de dados SQLite
            deepl_api_key: API key do DeepL (ou usar DEEPL_API_KEY env var)
        """
        # Inicializar banco de dados
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_cache_table()
        
        # Inicializar provedores
        self.deepl_provider = DeepLProvider(deepl_api_key)
        self.google_provider = GoogleTranslateProvider()
        
        self.stats = {
            'cache_hits': 0,
            'deepl_hits': 0,
            'google_hits': 0,
            'failed': 0
        }
    
    def _create_cache_table(self):
        """Criar tabela de cache se não existir."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                translated_text TEXT,
                provider TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        
        # Migração: Adicionar coluna 'provider' se não existir (compatibilidade com DB antigos)
        try:
            self.cursor.execute('ALTER TABLE cache ADD COLUMN provider TEXT DEFAULT "manual"')
            self.conn.commit()
            logger.info("✅ Cache: Coluna 'provider' adicionada (migração)")
        except sqlite3.OperationalError:
            # Coluna já existe, ignorar erro
            pass
    
    def get_translation(self, text: str) -> Optional[str]:
        """
        Obter tradução do cache ou gerar nova.
        
        Estratégia:
        1. Verificar cache
        2. Tentar DeepL (premium)
        3. Fallback para Google Translate (gratuito)
        4. Se falhar, retornar None
        """
        # 1. Verificar cache
        self.cursor.execute(
            'SELECT translated_text FROM cache WHERE key = ?',
            (text,)
        )
        result = self.cursor.fetchone()
        
        if result:
            self.stats['cache_hits'] += 1
            return result[0]
        
        # 2. Tentar DeepL (premium)
        if self.deepl_provider.available:
            translated = self.deepl_provider.translate(text)
            if translated:
                self.save_translation(text, translated, 'deepl')
                self.stats['deepl_hits'] += 1
                return translated
        
        # 3. Fallback para Google Translate (gratuito)
        if self.google_provider.available:
            translated = self.google_provider.translate(text)
            if translated:
                self.save_translation(text, translated, 'google')
                self.stats['google_hits'] += 1
                return translated
        
        # 4. Se falhar
        self.stats['failed'] += 1
        logger.warning(f"⚠️  Falha na tradução: {text[:50]}...")
        return None
    
    def save_translation(self, text: str, translated_text: str, provider: str = 'manual'):
        """Salvar tradução no cache."""
        try:
            self.cursor.execute(
                'INSERT OR REPLACE INTO cache (key, translated_text, provider) VALUES (?, ?, ?)',
                (text, translated_text, provider)
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"❌ Erro ao salvar no cache: {e}")
    
    def translate_batch(self, texts: list) -> Dict[str, str]:
        """Traduzir lote de textos."""
        results = {}
        for text in texts:
            translated = self.get_translation(text)
            results[text] = translated or f"[NÃO TRADUZIDO] {text}"
        return results
    
    def get_stats(self) -> Dict:
        """Obter estatísticas de tradução."""
        total = sum(self.stats.values())
        return {
            **self.stats,
            'total': total,
            'cache_percent': (self.stats['cache_hits'] / total * 100) if total > 0 else 0,
            'deepl_percent': (self.stats['deepl_hits'] / total * 100) if total > 0 else 0,
            'google_percent': (self.stats['google_hits'] / total * 100) if total > 0 else 0,
        }
    
    def close(self):
        """Fechar conexão com banco de dados."""
        self.conn.close()
