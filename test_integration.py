import os
from translation_provider import TranslatorCore

# Criar um tradutor de teste
core = TranslatorCore(db_path="test_cache.db")

print("Testando hierarquia de tradução...")

# 1. Testar Cache (precisa popular primeiro)
text = "Hello, world!"
core.save_translation(text, "Olá, mundo!", "manual")
print(f"Cache: {core.get_translation(text)}")

# 2. Testar LLM (se rodando)
if core.ollama_provider.available:
    print(f"Ollama: {core.get_translation('Chest')}")
else:
    print("Ollama: Não disponível (pulei)")

print("\nEstatísticas:")
print(core.get_stats())
core.close()
