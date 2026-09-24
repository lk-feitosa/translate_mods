# COLE_SEUS_MODS_OU_MODPACKS_AQUI

Uma **subpasta por modpack**. Dentro de cada uma, coloque só os `.jar` daquele pack.

```text
COLE_SEUS_MODS_OU_MODPACKS_AQUI/
├── deceasedcraft/     ← JARs do DeceasedCraft
├── cobleverse/
├── prominenceII/
└── superior/
```

Não coloque `config/`, quests, FancyMenu ou o Minecraft inteiro. O tradutor só lê `assets/*/lang/en_us.json` dentro dos JARs.

## Comandos

```powershell
# menu para escolher o pack
python main.py

# um pack específico (resume)
python main.py --modpack deceasedcraft

# todos
python main.py --modpack all

# retraduzir do zero
python main.py --modpack deceasedcraft --overwrite
```

A saída fica em `mods_traduzidos/<nome-do-modpack>/` (resource pack com `assets/`, `pack.mcmeta` e README).
