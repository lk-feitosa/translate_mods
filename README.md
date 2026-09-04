# Tradutor de Modpacks Minecraft

Ferramenta que procura recursivamente arquivos `en_us.json` dentro dos JARs de um modpack, traduz o conteúdo para português brasileiro e cria um resource pack em `mods_traduzidos/`.

## Estrutura do projeto

```text
translate_mods/
├── COLE_SEUS_MODS_OU_MODPACKS_AQUI/  # Coloque aqui o modpack ou a pasta com os JARs
├── mods_traduzidos/                   # Resource pack gerado
├── main.py                            # Comando principal
├── jar_scanner.py                     # Busca recursiva dos JARs
├── modpack_translator.py              # Processamento e gravação
├── translation_provider.py            # DeepL, Google e cache
├── translation_cache.db               # Cache local das traduções
├── requirements.txt                   # Dependências Python
└── venv/                              # Ambiente virtual local
```

## Como iniciar no Windows

Abra o terminal na pasta do projeto e execute:

### 1. Criar o ambiente virtual

Execute apenas na primeira configuração:

```powershell
python -m venv venv
```

### 2. Ativar o ambiente virtual

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

Se o ambiente já estiver ativo, o terminal mostrará `(venv)` no início da linha.

### 3. Instalar as dependências

```powershell
python -m pip install -r requirements.txt
```

### 4. Configurar a chave do DeepL

Crie o arquivo `.env` na raiz do projeto, usando `.env.example` como modelo:

```env
DEEPL_API_KEY=sua_chave_do_deepl
```

A chave fica apenas no `.env`, que não deve ser enviado para o GitHub.

## Como traduzir

1. Coloque o modpack dentro de `COLE_SEUS_MODS_OU_MODPACKS_AQUI/`. A ferramenta percorre todas as subpastas automaticamente.
2. Execute o comando normal:

```powershell
python main.py --mods ".\COLE_SEUS_MODS_OU_MODPACKS_AQUI" --output ".\mods_traduzidos"
```

O modo normal continua de onde parou: arquivos `pt_br.json` já existentes são ignorados, e as traduções ficam disponíveis no cache local.

### Traduzir tudo novamente

Use `--overwrite` para reprocessar e sobrescrever todos os arquivos de saída:

```powershell
python main.py --mods ".\COLE_SEUS_MODS_OU_MODPACKS_AQUI" --output ".\mods_traduzidos" --overwrite
```

Para garantir que o Python da instalação do projeto seja usado, execute:

```powershell
& ".\venv\Scripts\python.exe" ".\main.py" --mods ".\COLE_SEUS_MODS_OU_MODPACKS_AQUI" --output ".\mods_traduzidos"
```

## Resultado

Os arquivos gerados seguem o formato de resource pack do Minecraft:

```text
mods_traduzidos/
└── assets/
	└── <modid>/
		└── lang/
			└── pt_br.json
```

Depois da tradução, copie ou use a pasta `mods_traduzidos/` como resource pack no Minecraft.

## Testes

Para validar a busca recursiva, o cache, a continuidade e os valores especiais dos JSONs:

```powershell
python test_translator.py
```

## Provedores de tradução

- **DeepL:** provedor principal, configurado com `DEEPL_API_KEY`.
- **Google Translate:** fallback opcional, conforme as dependências e chaves configuradas.
- **Cache SQLite:** evita solicitar novamente textos já traduzidos.

## Observações

- A entrada deve conter JARs válidos de mods ou modpacks.
- A busca por `en_us.json` é recursiva.
- A pasta `COLE_SEUS_MODS_OU_MODPACKS_AQUI/` é a entrada do usuário.
- A pasta `mods_traduzidos/` é a saída gerada.
- Não altere os arquivos originais do modpack durante a tradução.
