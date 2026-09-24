# Tradutor de Modpacks Minecraft (LLM-first)

Procura `assets/*/lang/en_us.json` dentro dos JARs de cada modpack, traduz para PT-BR e gera **um resource pack por modpack**.

Provedores, nesta ordem:

1. Cache SQLite (`translation_cache.db`)
2. **Ollama (primário)** — local, sem cota
3. DeepL — fallback opcional
4. Google Translate (`deep-translator`) — fallback final, sem cartão

Este projeto **não traduz** `config/`, quests, NPCs nem FancyMenu. Resource pack só cobre arquivos `lang`.

---

## Estrutura esperada

```text
COLE_SEUS_MODS_OU_MODPACKS_AQUI/
├── deceasedcraft/          ← só os .jar desse modpack
├── cobleverse/
├── prominenceII/
└── superior/

mods_traduzidos/
├── deceasedcraft/          ← resource pack pronto
│   ├── assets/<modid>/lang/pt_br.json
│   ├── pack.mcmeta
│   └── README.md
└── cobleverse/
```

Uma pasta de entrada = um modpack = um resource pack de saída.

---

## Setup (Windows)

WSL2 **não é obrigatório**. Ollama nativo no Windows ou Docker Desktop bastam.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Crie o arquivo `.env` copiando o modelo de exemplo:

```powershell
cp .env.example .env
```

Abra o arquivo `.env` gerado e preencha a chave do DeepL (opcional) ou ajuste o modelo do Ollama:

```env
DEEPL_API_KEY=sua_chave_aqui_se_for_usar
OLLAMA_MODEL=llama3.2
OLLAMA_TIMEOUT=120
```

### Subir o Ollama (Docker)

```powershell
docker compose up -d
docker exec -it translate_mods-ollama ollama pull llama3.2
```

Sem Docker, instale o [Ollama](https://ollama.com) no Windows, rode `ollama pull llama3.2` e deixe `ollama serve` na porta `11434`.

Checagem:

```powershell
curl http://localhost:11434/api/tags
```

---

## Comandos

### Menu interativo (escolher um ou todos)

```powershell
.\venv\Scripts\python.exe main.py
```

O terminal lista as pastas de `COLE_SEUS_MODS_OU_MODPACKS_AQUI`:

```text
0. Traduzir TODOS os modpacks
1. cobleverse
2. deceasedcraft
3. prominenceII
4. superior
```

Digite o número.

### Continuar de onde parou (um modpack)

Arquivos `pt_br.json` já completos são pulados. Chaves `[NÃO TRADUZIDO]` são retraduzidas. Cache reaproveitado.

```powershell
.\venv\Scripts\python.exe main.py --modpack deceasedcraft
```

### Continuar todos

```powershell
.\venv\Scripts\python.exe main.py --modpack all
```

### Sobrescrever tudo (retraduz do zero)

Não apaga o cache. Só força reescrever os `pt_br.json` daquele pack.

```powershell
.\venv\Scripts\python.exe main.py --modpack deceasedcraft --overwrite
.\venv\Scripts\python.exe main.py --modpack all --overwrite
```

Interromper com `Ctrl+C` é seguro: o progresso já gravado permanece. Rode de novo **sem** `--overwrite` para retomar.

---

## Como usar o pack no Minecraft

Copie `mods_traduzidos/<nome-do-modpack>/` para `.minecraft/resourcepacks/` e ative no jogo.

---

## Observações

- Timeouts do Ollama: aumente `OLLAMA_TIMEOUT` no `.env` (padrão 120s).
- Google sem cartão: o fallback usa a interface web via `deep-translator`. Pode ser bloqueado por rate limit; o resume cobre isso.
- O cache `translation_cache.db` é compartilhado entre modpacks. A mesma string não é traduzida duas vezes.
