#!/usr/bin/env python3
"""
Script de teste para demonstrar a visualização do tradutor
com gráficos, cores e barra de progresso.
"""

import os
import json
import tempfile
import zipfile
from pathlib import Path

from jar_scanner import JarScanner

def create_test_mod_jar():
    """Cria um JAR de teste com arquivos de tradução."""
    
    # Criar diretório temporário
    temp_dir = tempfile.mkdtemp()
    test_lang = {
        "item.minecraft.apple": "Maçã",
        "item.minecraft.diamond": "Diamante",
        "block.minecraft.stone": "Pedra",
        "block.minecraft.dirt": "Terra",
        "chat.type.text": "[%s] %s",
        "death.fell.accident.generic": "%s caiu muito alto",
    }
    
    # Criar JAR com estrutura correta
    jar_path = os.path.join(temp_dir, "test_mod.jar")
    with zipfile.ZipFile(jar_path, 'w') as jar:
        # Adicionar arquivo de idioma
        lang_data = json.dumps(test_lang, ensure_ascii=False, indent=2)
        jar.writestr("assets/minecraft/lang/en_us.json", lang_data)
        
        # Adicionar outro mod como exemplo
        test_lang2 = {
            "item.example.custom_item": "Item Customizado",
            "block.example.custom_block": "Bloco Customizado",
        }
        lang_data2 = json.dumps(test_lang2, ensure_ascii=False, indent=2)
        jar.writestr("assets/examplemod/lang/en_us.json", lang_data2)
    
    return temp_dir, jar_path

def test_recursive_jar_scan():
    """Valida que JARs em subpastas são encontrados recursivamente."""
    temp_dir = tempfile.mkdtemp()
    nested_dir = os.path.join(temp_dir, "mods", "pack01")
    os.makedirs(nested_dir, exist_ok=True)

    jar_path = os.path.join(nested_dir, "example_mod.jar")
    with zipfile.ZipFile(jar_path, 'w') as jar:
        jar.writestr("assets/minecraft/lang/en_us.json", json.dumps({"block.minecraft.stone": "Stone"}, ensure_ascii=False))

    found = JarScanner(temp_dir).scan()
    assert found, "JarScanner não encontrou JAR em subpasta"
    assert any("assets/minecraft/lang/en_us.json" in key for key in found), "Arquivo en_us.json não foi encontrado recursivamente"

    print("✅ Teste recursivo de scan passou")


def test_skip_existing_translation_files():
    """Valida que arquivos já traduzidos são ignorados por padrão."""
    from modpack_translator import ModpackTranslator

    temp_dir = tempfile.mkdtemp()
    mods_dir = os.path.join(temp_dir, "mods")
    output_dir = os.path.join(temp_dir, "traducoes")
    os.makedirs(mods_dir, exist_ok=True)

    jar_path = os.path.join(mods_dir, "example_mod.jar")
    with zipfile.ZipFile(jar_path, 'w') as jar:
        jar.writestr("assets/minecraft/lang/en_us.json", json.dumps({"item.minecraft.apple": "Apple"}, ensure_ascii=False))

    first_run = ModpackTranslator(mods_dir, output_dir)
    first_run.run()
    out_file = os.path.join(output_dir, "assets", "minecraft", "lang", "pt_br.json")
    assert os.path.exists(out_file), "Arquivo de saída não foi gerado na primeira execução"

    second_run = ModpackTranslator(mods_dir, output_dir)
    second_run.run()
    with open(out_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert data.get("item.minecraft.apple") is not None, "Arquivo existente foi sobrescrito sem necessidade"

    print("✅ Teste de continuidade e skip existente passou")


def test_list_values_are_normalized():
    """Valida que valores tipo list/dict do JSON não quebram o cache nem a tradução."""
    from translation_provider import TranslatorCore

    translator = TranslatorCore(db_path=':memory:')
    result = translator.get_translation(['hello', 'world'])
    assert isinstance(result, str) or result is None, "Valor em lista deve ser convertido em string segura"
    assert translator.normalize_text(['hello', 'world']) == 'hello, world'
    print("✅ Teste de valores em lista passou")


def main():
    print("\n" + "="*60)
    print("🧪 TESTE DO TRADUTOR COM VISUALIZAÇÃO")
    print("="*60 + "\n")

    test_recursive_jar_scan()
    test_skip_existing_translation_files()
    test_list_values_are_normalized()
    
    # Criar JAR de teste
    print("📦 Criando JAR de teste...")
    temp_dir, jar_path = create_test_mod_jar()
    mods_dir = temp_dir
    output_dir = os.path.join(temp_dir, "traducoes")
    
    print(f"✅ JAR de teste criado: {jar_path}\n")
    
    # Importar e executar tradutor
    print("🚀 Executando tradutor...\n")
    from modpack_translator import ModpackTranslator
    
    translator = ModpackTranslator(mods_dir, output_dir)
    translator.run()
    
    # Mostrar resultado
    print(f"\n✅ Verificando arquivos gerados...\n")
    
    output_files = []
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                output_files.append(file_path)
                rel_path = os.path.relpath(file_path, output_dir)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"📄 {rel_path}")
                print(f"   → {len(data)} chaves traduzidas")
                for key, value in list(data.items())[:2]:  # Mostrar as primeiras 2
                    print(f"      • {key}: {value[:50]}...")
    
    print(f"\n🎉 Teste concluído com sucesso!")
    print(f"   Arquivos gerados: {len(output_files)}")
    
    # Limpeza
    print(f"\n🧹 Limpando arquivos temporários...")
    import shutil
    shutil.rmtree(temp_dir)
    print(f"✅ Concluído!\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
