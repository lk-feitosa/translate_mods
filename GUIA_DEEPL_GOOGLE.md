#!/usr/bin/env python3
"""
📖 Guia de Uso - Tradutor de Modpacks Minecraft PT-BR
"""

import sys

def print_guide():
    guide = """
╔════════════════════════════════════════════════════════════════════════╗
║                  🌍 TRADUTOR MODPACK MINECRAFT - PT_BR                ║
║                        Com DeepL + Google Translate                    ║
╚════════════════════════════════════════════════════════════════════════╝

🚀 INÍCIO RÁPIDO
═══════════════════════════════════════════════════════════════════════════

1️⃣ Instalar dependências:
   $ pip install -r requirements.txt

2️⃣ Configurar API keys em .env:
   Copie .env.example → .env e preencha:
   
   DEEPL_API_KEY=df1b4654-b9af-4f6d-a95b-486fd197dd19:fx
   GOOGLE_API_KEY=sua-chave-do-google (opcional)

3️⃣ Executar tradução:
   $ python main.py --mods ./mods --output ./traducoes
   
   Ou com API key via linha de comando:
   $ python main.py --mods ./mods --output ./traducoes --api-key sua-chave

4️⃣ Verificar resultados:
   Os arquivos serão salvos em: ./traducoes/assets/*/lang/pt_br.json


📊 ARQUITETURA
═══════════════════════════════════════════════════════════════════════════

main.py
  └─ modpack_translator.py (Orquestração)
     ├─ jar_scanner.py (Extrai en_us.json de JARs)
     └─ translation_provider.py (APIs de tradução com cache)
        ├─ DeepL (Premium - Rápido & Preciso)
        ├─ Google Translate (Gratuito - Fallback)
        └─ SQLite Cache (Evita re-tradução)


🔑 CONFIGURAÇÃO DE APIs
═══════════════════════════════════════════════════════════════════════════

DeepL (PRIMÁRIO - Recomendado)
───────────────────────────────
• Site: https://www.deepl.com/pro#developer
• Free Tier: 500.000 caracteres/mês
• Velocidade: ⚡ Muito rápido
• Qualidade: ⭐⭐⭐⭐⭐ Excelente
• Setup: Apenas 1 linha no .env

DEEPL_API_KEY=df1b4654-b9af-4f6d-a95b-486fd197dd19:fx


Google Translate (FALLBACK - Opcional)
──────────────────────────────────────
Opção 1: Google Cloud Translation (Requer credenciais)
  • Site: https://cloud.google.com/translate
  • Setup: Arquivo JSON com credenciais

Opção 2: Google Generative AI (Com API key)
  • Site: https://makersuite.google.com/app/apikey
  • Setup: GOOGLE_API_KEY no .env

Opção 3: googletrans (Gratuito, sem API key)
  • Automático se as opções 1-2 não funcionarem
  • Velocidade: Mais lenta (rate limiting)


🔄 FLUXO DE TRADUÇÃO
═══════════════════════════════════════════════════════════════════════════

Para cada texto a traduzir:

1. ✅ Verificar cache SQLite
2. ✅ Se não encontrado → Tentar DeepL
3. ✅ Se DeepL falhar → Fallback Google Translate
4. ✅ Se ambos falharem → Marcar como "[NÃO TRADUZIDO]"
5. ✅ Salvar resultado no cache para próxima vez


📈 EXEMPLO DE EXECUÇÃO
═══════════════════════════════════════════════════════════════════════════

$ python main.py --mods ./COLE_SEUS_MODS_OU_MODPACKS_AQUI --output ./textura_traducao

============================================================
🌍 TRADUTOR DE MODPACK MINECRAFT - PT_BR
============================================================

📂 Escaneando JARs...
✅ Encontrado: assets/minecraft/lang/en_us.json
✅ Encontrado: assets/cobblemon/lang/en_us.json
✅ 25 arquivo(s) de tradução encontrado(s)

📡 Provedores de Tradução:
   ✅ DeepL: Ativo
   ✅ Google Translate: Ativo (Fallback)

🔄 Processando traduções...

Mods: 100%|████████████████| 25/25 [02:45<00:00, 6.6s/mod]

============================================================
🎉 TRADUÇÃO CONCLUÍDA COM SUCESSO!
============================================================
📊 Resumo:
   • Mods processados: 25
   • Total de chaves traduzidas: 5,847
📈 Fonte das Traduções:
   • Cache: 4,200 (71.9%)
   • DeepL: 1,500 (25.7%)
   • Google: 147 (2.5%)
   • Falhas: 0
   • Saída: ./textura_traducao


📁 ESTRUTURA DE SAÍDA
═══════════════════════════════════════════════════════════════════════════

textura_traducao/
├── assets/
│   ├── minecraft/
│   │   └── lang/
│   │       └── pt_br.json (Traduções do Minecraft vanilla)
│   ├── cobblemon/
│   │   └── lang/
│   │       └── pt_br.json (Traduções do Cobblemon)
│   ├── modname1/
│   │   └── lang/
│   │       └── pt_br.json
│   └── modname2/
│       └── lang/
│           └── pt_br.json


🧪 TESTES
═══════════════════════════════════════════════════════════════════════════

Executar suite completa de testes:
  $ python test_api_integration.py

Teste com visualização (usando JAR de teste):
  $ python test_translator.py


🐛 TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════

❌ "DEEPL_API_KEY não encontrada"
  → Configure em .env: DEEPL_API_KEY=sua-chave

❌ "Nenhum arquivo de tradução encontrado"
  → Verifique se pasta contém arquivos .jar válidos
  → JAR deve ter estrutura: assets/*/lang/en_us.json

❌ "Rate limit do DeepL excedido"
  → Aguarde 1 hora, cache vai usar traduções salvas
  → Google Translate fará fallback automaticamente

❌ "Erro ao conectar com API"
  → Verifique conexão com internet
  → Valide API key em https://www.deepl.com/account

❌ "Translation_cache.db corrompido"
  → Delete o arquivo: rm translation_cache.db
  → Cache será recriado automaticamente


💡 DICAS DE USO
═══════════════════════════════════════════════════════════════════════════

✅ Use cache: Primeira execução é mais lenta, as próximas são rápidas
✅ Economize API: Cache evita re-tradução (71% do tempo)
✅ Batch translation: Traduza múltiplos modpacks para aproveitar cache
✅ Teste antes: Use test_api_integration.py para validar setup
✅ Log completo: Verifique logs em stdout para erros detalhados


📞 SUPORTE
═══════════════════════════════════════════════════════════════════════════

Erro persistente? Colete informações:
  1. Saída completa do comando (com --verbose se disponível)
  2. Versão do Python: python --version
  3. Versão do DeepL: pip show deepl
  4. Sistema operacional: uname -a (Linux/Mac) ou ver (Windows)
  5. Arquivo .env (sem chaves sensíveis)


✅ Você está pronto para começar! Execute:
   python main.py --mods ./COLE_SEUS_MODS_OU_MODPACKS_AQUI --output ./textura_traducao
"""
    print(guide)


if __name__ == "__main__":
    print_guide()
