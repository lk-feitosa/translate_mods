# Tradução Modpack - COBBLEVERSE

Projeto de tradução para português brasileiro do modpack **COBBLEVERSE - Pokemon Adventure [Cobblemon]**.

## 📋 Estrutura do Projeto

```
translate_mods/
├── COLE_SEUS_MODS_OU_MODPACKS_AQUI/    # Modpack original
├── traducao_modpack/                     # Arquivos de tradução
│   └── datapacks/
│       └── Modpack_Skilltree_PT_BR/     # Datapack com traduções
├── mods/                                 # Pasta para mods adicionais
└── venv/                                 # Ambiente virtual Python
```

## 🚀 Como Iniciar

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/translate_mods.git
cd translate_mods
```

### 2. Criar ambiente virtual
```bash
python -m venv venv
```

### 3. Ativar ambiente virtual

**Windows:**
```bash
.\venv\Scripts\Activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Instalar dependências (se houver)
```bash
pip install -r requirements.txt
```

## 📝 Arquivos de Tradução

Os arquivos de tradução estão localizados em:
- `traducao_modpack/datapacks/Modpack_Skilltree_PT_BR/`

### Estrutura de um Datapack
- `pack.mcmeta` - Metadados do datapack
- `data/` - Contém as definições de skills em JSON

## 🛠️ Tecnologias

- **Python 3.13+**
- **Minecraft Datapacks**
- **JSON para configurações**

## 📌 Notas

- Este é um projeto de tradução para o modpack COBBLEVERSE
- Todas as traduções devem estar em português brasileiro
- Respeitar a estrutura dos JSONs originais

## 📄 Licença

Verifique os arquivos de licença individuais em `COLE_SEUS_MODS_OU_MODPACKS_AQUI/licenses/`

## 👨‍💻 Contribuindo

Para contribuir com traduções ou melhorias:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

**Status:** Em desenvolvimento 🚧
