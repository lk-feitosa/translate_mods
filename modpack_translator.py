import json
import logging
import os
import tempfile

from colorama import Fore, init
from tqdm import tqdm

from jar_scanner import JarScanner
from translation_provider import TranslatorCore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

init(autoreset=True)

UNTRANSLATED_PREFIX = "[NÃO TRADUZIDO] "


class ModpackTranslator:
    def __init__(self, mods_path, output_path, deepl_api_key=None, overwrite=False, pack_name=None):
        self.scanner = JarScanner(mods_path)
        self.translator = TranslatorCore(deepl_api_key=deepl_api_key)
        self.output_path = output_path
        self.overwrite = overwrite
        self.pack_name = pack_name or os.path.basename(os.path.normpath(output_path))

    def _output_file_for_mod(self, modid):
        return os.path.join(self.output_path, "assets", modid, "lang", "pt_br.json")

    def _load_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _is_untranslated(self, value) -> bool:
        return isinstance(value, str) and value.startswith(UNTRANSLATED_PREFIX)

    def _file_needs_work(self, existing: dict, source: dict) -> bool:
        if self.overwrite or not existing:
            return True
        for key in source:
            if key not in existing or self._is_untranslated(existing.get(key)):
                return True
        return False

    def _atomic_write_json(self, path: str, data: dict) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        directory = os.path.dirname(path)
        fd, tmp_path = tempfile.mkstemp(prefix=".pt_br_", suffix=".json", dir=directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
            
            # Tenta substituir o arquivo com retentativas (para contornar bloqueios do OneDrive/Antivírus no Windows)
            import time
            for i in range(5):
                try:
                    os.replace(tmp_path, path)
                    break
                except PermissionError:
                    if i == 4:
                        raise
                    time.sleep(0.5)
        except Exception:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise

    def _write_pack_files(self) -> None:
        os.makedirs(self.output_path, exist_ok=True)
        pack_path = os.path.join(self.output_path, "pack.mcmeta")
        payload = {
            "pack": {
                "pack_format": 15,
                "supported_formats": {"min_inclusive": 9, "max_inclusive": 48},
                "description": f"Traduções PT-BR — {self.pack_name}",
            }
        }
        with open(pack_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")

        readme = f"""# Resource Pack: {self.pack_name}

Este pack foi gerado automaticamente a partir dos arquivos `assets/*/lang/en_us.json` dos JARs.

## Como usar
1. Copie esta pasta inteira para `.minecraft/resourcepacks/`
2. Ative o resource pack no Minecraft
3. Defina o idioma do jogo para Português (Brasil)

## O que este pack traduz
- Nomes de itens, blocos, entidades e a maior parte da UI dos mods (`lang`)

## O que NÃO é traduzido por resource pack
- Quests (FTBQuests `.snbt`)
- Diálogos de NPCs (CustomNPCs)
- Menus do FancyMenu
- Arquivos em `config/`, `kubejs/`, `.toml` e `.json5`

Esses arquivos são lógica do modpack. Traduzi-los fora do jogo pode quebrar IDs.
"""
        with open(os.path.join(self.output_path, "README.md"), "w", encoding="utf-8") as handle:
            handle.write(readme)

    def _print_summary(self, processed_mods, resumed_mods, skipped_mods, translated_keys, reused_keys):
        stats = self.translator.get_stats()
        print(f"\n{Fore.GREEN}📁 Resource pack gerado em {self.output_path}")
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.GREEN}🎉 TRADUÇÃO CONCLUÍDA — {self.pack_name}")
        print(f"{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.YELLOW}📊 Resumo:")
        print(f"   • Mods processados: {processed_mods}")
        print(f"   • Mods retomados (incompletos): {resumed_mods}")
        print(f"   • Mods ignorados (já completos): {skipped_mods}")
        print(f"   • Chaves novas/retomadas: {translated_keys}")
        print(f"   • Chaves reaproveitadas: {reused_keys}")
        print(f"{Fore.YELLOW}📈 Fonte das traduções:")
        print(f"   • Cache: {stats['cache_hits']} ({stats['cache_percent']:.1f}%)")
        print(f"   • Ollama (LLM): {stats['ollama_hits']} ({stats['ollama_percent']:.1f}%)")
        print(f"   • DeepL: {stats['deepl_hits']} ({stats['deepl_percent']:.1f}%)")
        print(f"   • Google: {stats['google_hits']} ({stats['google_percent']:.1f}%)")
        print(f"   • Falhas: {stats['failed']}")
        if stats.get("deepl_quota_exceeded"):
            print(f"{Fore.YELLOW}   • DeepL ficou sem cota; o resto foi para os fallbacks")
        print(f"   • Saída: {self.output_path}\n")

    def run(self):
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.CYAN}🌍 TRADUTOR DE MODPACK MINECRAFT - PT_BR")
        print(f"{Fore.CYAN}   Pack: {self.pack_name}")
        print(f"{Fore.CYAN}{'=' * 60}\n")

        if self.overwrite:
            print(f"{Fore.YELLOW}⚠️  Modo: sobrescrever arquivos existentes")
        else:
            print(
                f"{Fore.YELLOW}ℹ️  Modo: continuar de onde parou "
                "(completa arquivos com [NÃO TRADUZIDO])"
            )

        print(f"{Fore.YELLOW}📂 Escaneando JARs em {self.scanner.mods_path}...")
        mod_data = self.scanner.scan()

        if not mod_data:
            print(f"{Fore.RED}❌ Nenhum arquivo de tradução encontrado nos JARs!")
            print(f"{Fore.RED}   Coloque os .jar do modpack nessa pasta (não configs/quests).\n")
            return

        print(f"{Fore.GREEN}✅ {len(mod_data)} arquivo(s) de tradução encontrado(s)\n")

        print(f"{Fore.CYAN}📡 Provedores de Tradução:")
        if self.translator.ollama_provider.available:
            print(
                f"{Fore.GREEN}   ✅ Ollama (LLM): Ativo "
                f"({self.translator.ollama_provider.model})"
            )
        else:
            print(f"{Fore.YELLOW}   ⚠️  Ollama (LLM): Offline")
        if self.translator.deepl_provider.available:
            print(f"{Fore.GREEN}   ✅ DeepL: Ativo (Fallback)")
        else:
            status = "Cota esgotada" if self.translator.deepl_provider.quota_exceeded else "Desativado"
            print(f"{Fore.YELLOW}   ⚠️  DeepL: {status}")
        if self.translator.google_provider.available:
            print(f"{Fore.GREEN}   ✅ Google Translate: Ativo (Fallback final)")
        else:
            print(f"{Fore.YELLOW}   ⚠️  Google Translate: Desativado")
        print()

        print(f"{Fore.YELLOW}🔄 Processando traduções...\n")

        grouped = {}
        for file_path, data in mod_data.items():
            parts = file_path.replace("\\", "/").split("/")
            modid = parts[1] if len(parts) > 1 else "unknown"
            grouped.setdefault(modid, {}).update(data if isinstance(data, dict) else {})

        pbar_mods = tqdm(grouped.items(), desc=f"{Fore.CYAN}Mods", unit="mod", colour="cyan")

        processed_mods = 0
        skipped_mods = 0
        resumed_mods = 0
        translated_keys = 0
        reused_keys = 0

        try:
            for modid, data in pbar_mods:
                output_file = self._output_file_for_mod(modid)
                existing = {} if self.overwrite else self._load_json(output_file)

                if not self._file_needs_work(existing, data):
                    skipped_mods += 1
                    pbar_mods.set_postfix({"mod": modid, "status": "skip"})
                    pbar_mods.write(f"{Fore.YELLOW}↩️  Pulando {modid}: já completo")
                    continue

                is_resume = bool(existing) and not self.overwrite
                if is_resume:
                    resumed_mods += 1
                    pbar_mods.set_postfix({"mod": modid, "status": "resume"})
                else:
                    processed_mods += 1
                    pbar_mods.set_postfix({"mod": modid, "status": "translate"})

                translated_data = dict(existing) if is_resume else {}
                pending_items = []
                for key, value in data.items():
                    current = translated_data.get(key)
                    if current is not None and not self._is_untranslated(current) and not self.overwrite:
                        reused_keys += 1
                        continue
                    pending_items.append((key, value))

                pbar_keys = tqdm(
                    pending_items,
                    desc=f"  → {modid}",
                    unit="key",
                    leave=False,
                    colour="magenta",
                )

                for key, value in pbar_keys:
                    translated = self.translator.get_translation(value)
                    if not translated:
                        original = value if isinstance(value, str) else str(value)
                        translated = f"{UNTRANSLATED_PREFIX}{original}"
                    translated_data[key] = translated
                    translated_keys += 1

                    if translated_keys % 25 == 0:
                        self._atomic_write_json(output_file, translated_data)

                pbar_keys.close()
                self._atomic_write_json(output_file, translated_data)

                pending_left = sum(1 for v in translated_data.values() if self._is_untranslated(v))
                if pending_left:
                    pbar_mods.write(
                        f"{Fore.YELLOW}⚠️  {modid}: {len(translated_data)} chaves, "
                        f"{pending_left} ainda sem tradução"
                    )
                else:
                    pbar_mods.write(f"{Fore.GREEN}✅ {modid}: {len(translated_data)} chaves traduzidas")
        finally:
            pbar_mods.close()
            self._write_pack_files()
            self._print_summary(
                processed_mods,
                resumed_mods,
                skipped_mods,
                translated_keys,
                reused_keys,
            )
            self.translator.close()
