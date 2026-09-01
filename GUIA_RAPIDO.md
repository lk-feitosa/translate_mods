# 🚀 GUIA RÁPIDO - COMO USAR O TRADUTOR

## ✅ Status Atual

O projeto **translate_mods** está **100% pronto para usar**! ✨

### Últimas Melhorias Implementadas:
- ✅ **Barras de progresso** com cores (tqdm)
- ✅ **Terminal colorido** com emojis e formatação (colorama)
- ✅ **Tratamento de erros** robusto
- ✅ **Validação de caminhos** antes de executar
- ✅ **Resumo estatístico** ao final
- ✅ **Script de teste** incluído

---

## 🎯 Como Rodar

### 1️⃣ **Ativar Ambiente Virtual**

```bash
cd c:\Users\lukas\OneDrive\pessoal\Dev\projects\translate_mods
.\venv\Scripts\Activate
```

### 2️⃣ **Rodar o Tradutor**

```bash
# Usando uma pasta com mods reais
python main.py --mods ./COLE_SEUS_MODS_OU_MODPACKS_AQUI/mods --output ./traducoes

# Ou com qualquer outra pasta de mods
python main.py --mods "C:\Caminho\Para\Mods" --output "C:\Saída\Traducoes"
```

### 3️⃣ **Testar com JAR Fictício (recomendado)**

```bash
# Cria um teste com visualização completa
python test_translator.py
```

---

## 📊 O que Você Verá no Terminal

```
============================================================
🌍 TRADUTOR DE MODPACK MINECRAFT - PT_BR
============================================================

📂 Escaneando JARs...
✅ Encontrado: assets/minecraft/lang/en_us.json
✅ Encontrado: assets/cobblemon/lang/en_us.json
Escaneando JARs: 100%|█████████████████████████| 10/10

✅ 10 arquivo(s) de tradução encontrado(s)

🔄 Processando traduções...

✅ minecraft: 1250 chaves traduzidas
✅ cobblemon: 3400 chaves traduzidas
✅ forge: 250 chaves traduzidas
Mods: 100%|████████████████████████████████| 10/10

============================================================
🎉 TRADUÇÃO CONCLUÍDA COM SUCESSO!
============================================================
📊 Resumo:
   • Mods processados: 10
   • Total de chaves traduzidas: 12500
   • Saída: ./traducoes
```

---

## 📁 Estrutura de Saída

Após rodar, você terá:

```
traducoes/
├── assets/
│   ├── minecraft/lang/pt_br.json         ✅ 1250 chaves
│   ├── cobblemon/lang/pt_br.json         ✅ 3400 chaves
│   ├── forge/lang/pt_br.json             ✅ 250 chaves
│   └── [outros mods]/lang/pt_br.json
```

---

## 🎨 Recursos Visuais

### Cores Utilizadas:
- 🔵 **Cyan** - Títulos e cabeçalhos
- 🟢 **Verde** - Sucesso (✅)
- 🔴 **Vermelho** - Erros (❌)
- 🟣 **Magenta** - Barra de progresso de chaves
- 🟡 **Amarelo** - Avisos (⚠️)

### Emojis:
- 🌍 Tradutor
- 📂 Escaneando
- ✅ Sucesso
- ❌ Erro
- 🔄 Processando
- 🎉 Conclusão
- 📊 Estatísticas

---

## 💾 Dados Salvos

- **Cache de traduções**: `translation_cache.db` (SQLite)
- **Arquivos de tradução**: `assets/*/lang/pt_br.json`
- **Requisitos Python**: `requirements.txt`

---

## 🐛 Troubleshooting

### Erro: "Pasta de mods não encontrada"
```bash
# Verificar se o caminho está correto
ls "C:\Seu\Caminho\Mods"

# Usar caminho relativo
python main.py --mods ./mods --output ./out
```

### Erro: "Nenhum arquivo .jar encontrado"
```bash
# Verificar se há JARs na pasta
dir *.jar

# Os JARs devem estar em:
./COLE_SEUS_MODS_OU_MODPACKS_AQUI/mods/
```

### Dependências não instaladas
```bash
# Reinstalar dependências
pip install -r requirements.txt --upgrade
```

---

## 📝 Arquivos do Projeto

| Arquivo | Descrição |
|---------|-----------|
| `main.py` | Ponto de entrada (CLI) |
| `modpack_translator.py` | Orquestrador da tradução |
| `jar_scanner.py` | Extrai JSONs dos JARs |
| `translator_core.py` | Gerencia cache SQLite |
| `test_translator.py` | Script de teste com JAR fictício |
| `requirements.txt` | Dependências Python |
| `dump_pyc.py` | Utilitário para bytecode |

---

## 🚀 Próximos Passos

### Curto Prazo:
- [ ] Rodar com seus mods reais
- [ ] Ajustar cache de traduções
- [ ] Integrar com API de tradução (Google/DeepL)

### Médio Prazo:
- [ ] Adicionar testes unitários
- [ ] CI/CD com GitHub Actions
- [ ] Interface gráfica (Tkinter/Web)

### Longo Prazo:
- [ ] Suporte a múltiplos idiomas
- [ ] Validação de traduções
- [ ] Sistema de plugins

---

## 📞 Comandos Úteis

```bash
# Ver ajuda
python main.py --help

# Rodar teste rápido
python test_translator.py

# Ver histórico de commits
git log --oneline

# Ver arquivos não commitados
git status

# Atualizar repositório
git add .
git commit -m "Suas mudanças"
git push origin main
```

---

**Status:** ✅ **PRONTO PARA USAR!** 🎉

Divirta-se traduzindo! 🌍🇧🇷
