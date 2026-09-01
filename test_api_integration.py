#!/usr/bin/env python3
"""
Script de teste para validar integração DeepL + Google Translate
com cache SQLite.
"""

import os
import sys
import json
import tempfile
import zipfile
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def create_test_jar_with_translations():
    """Cria um JAR de teste para demonstrar a tradução."""
    
    temp_dir = tempfile.mkdtemp()
    
    # Textos de teste em inglês
    test_data = {
        "minecraft": {
            "item.minecraft.apple": "Apple",
            "item.minecraft.diamond": "Diamond",
            "block.minecraft.stone": "Stone",
            "block.minecraft.dirt": "Dirt",
            "block.minecraft.grass": "Grass Block",
        },
        "examplemod": {
            "item.example.custom_sword": "Custom Sword",
            "block.example.custom_ore": "Custom Ore",
        }
    }
    
    # Criar JAR de teste
    jar_path = os.path.join(temp_dir, "test_mod.jar")
    with zipfile.ZipFile(jar_path, 'w') as jar:
        for modid, translations in test_data.items():
            lang_data = json.dumps(translations, ensure_ascii=False, indent=2)
            jar.writestr(f"assets/{modid}/lang/en_us.json", lang_data)
    
    return temp_dir, jar_path


def test_translation_apis():
    """Testa os provedores de tradução."""
    
    from translation_provider import TranslatorCore
    
    print("\n" + "="*70)
    print("🧪 TESTE DE INTEGRAÇÃO: DeepL + Google Translate + Cache")
    print("="*70 + "\n")
    
    # Inicializar TranslatorCore
    print("🔧 Inicializando provedores de tradução...\n")
    translator = TranslatorCore()
    
    # Mostrar status dos provedores
    print("📡 Status dos Provedores:")
    print(f"   • DeepL: {'✅ Ativo' if translator.deepl_provider.available else '❌ Inativo'}")
    print(f"   • Google Translate: {'✅ Ativo' if translator.google_provider.available else '❌ Inativo'}\n")
    
    if not translator.deepl_provider.available and not translator.google_provider.available:
        print("⚠️  AVISO: Nenhum provedor de tradução está disponível!")
        print("   Configure a API key do DeepL ou Google em .env\n")
        return False
    
    # Textos de teste
    test_texts = [
        "Apple",
        "Diamond", 
        "Stone",
        "Grass Block",
        "Custom Sword",
        "Custom Ore"
    ]
    
    print("📝 Testando tradução de textos:\n")
    
    # Traduzir cada texto
    for text in test_texts:
        translated = translator.get_translation(text)
        provider_used = "Cache"
        
        if not translated:
            # Verificar qual provedor foi usado
            stats = translator.get_stats()
            if stats['deepl_hits'] > 0 and stats['deepl_hits'] > stats['google_hits']:
                provider_used = "DeepL"
            elif stats['google_hits'] > 0:
                provider_used = "Google"
            else:
                provider_used = "Nenhum"
        
        print(f"   {text:30} → {translated:30} ({provider_used})")
    
    # Mostrar estatísticas
    print()
    stats = translator.get_stats()
    print("📊 Estatísticas de Tradução:")
    print(f"   • Total de traduções: {stats['total']}")
    print(f"   • Cache hits: {stats['cache_hits']} ({stats['cache_percent']:.1f}%)")
    print(f"   • DeepL: {stats['deepl_hits']} ({stats['deepl_percent']:.1f}%)")
    print(f"   • Google: {stats['google_hits']} ({stats['google_percent']:.1f}%)")
    print(f"   • Falhas: {stats['failed']}\n")
    
    # Fechar translator
    translator.close()
    
    return True


def test_full_workflow():
    """Testa o fluxo completo com JAR de teste."""
    
    from modpack_translator import ModpackTranslator
    
    print("\n" + "="*70)
    print("🚀 TESTE DO FLUXO COMPLETO: Scan → Tradução → Saída")
    print("="*70 + "\n")
    
    # Criar JAR de teste
    print("📦 Criando JAR de teste...")
    temp_dir, jar_path = create_test_jar_with_translations()
    output_dir = os.path.join(temp_dir, "traducoes")
    print(f"✅ JAR criado: {jar_path}\n")
    
    # Executar tradutor
    print("🌍 Executando tradutor com APIs reais...\n")
    try:
        translator = ModpackTranslator(temp_dir, output_dir)
        translator.run()
        
        # Verificar saída
        print("\n✅ Verificando arquivos gerados:\n")
        success = False
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.json'):
                    success = True
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, output_dir)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    print(f"📄 {rel_path}")
                    print(f"   Chaves traduzidas: {len(data)}")
                    
                    # Mostrar algumas traduções
                    for key, value in list(data.items())[:3]:
                        print(f"      • {key}: {value}")
                    if len(data) > 3:
                        print(f"      ... e mais {len(data) - 3} chaves")
        
        if success:
            print("\n🎉 Fluxo completo executado com sucesso!")
        else:
            print("\n⚠️  Nenhum arquivo foi gerado!")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Erro durante o fluxo: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executar todos os testes."""
    
    print("\n🧪 INICIANDO SUITE DE TESTES\n")
    
    # Teste 1: APIs de Tradução
    test1_pass = test_translation_apis()
    
    # Teste 2: Fluxo Completo
    test2_pass = test_full_workflow()
    
    # Resumo
    print("\n" + "="*70)
    print("📋 RESUMO DOS TESTES")
    print("="*70)
    print(f"✅ APIs de Tradução: {'PASSOU' if test1_pass else 'FALHOU'}")
    print(f"✅ Fluxo Completo: {'PASSOU' if test2_pass else 'FALHOU'}")
    print("="*70 + "\n")
    
    if test1_pass and test2_pass:
        print("🎉 TODOS OS TESTES PASSARAM!\n")
        return 0
    else:
        print("❌ ALGUNS TESTES FALHARAM\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
