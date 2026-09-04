

import os
import json
import logging
from jar_scanner import JarScanner
from translation_provider import TranslatorCore
from tqdm import tqdm
from colorama import Fore, Back, Style, init

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

init(autoreset=True)  # Inicializar colorama

class ModpackTranslator:
    def __init__(self, mods_path, output_path, deepl_api_key=None, overwrite=False):
        self.scanner = JarScanner(mods_path)
        self.translator = TranslatorCore(deepl_api_key=deepl_api_key)
        self.output_path = output_path
        self.overwrite = overwrite

    def _output_file_for_mod(self, modid):
        return os.path.join(self.output_path, f"assets/{modid}/lang/pt_br.json")

    def run(self):
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}🌍 TRADUTOR DE MODPACK MINECRAFT - PT_BR")
        print(f"{Fore.CYAN}{'='*60}\n")

        if self.overwrite:
            print(f"{Fore.YELLOW}⚠️  Modo: sobrescrever arquivos existentes")
        else:
            print(f"{Fore.YELLOW}ℹ️  Modo: continuar de onde parou (ignorar arquivos já gerados)")

        print(f"{Fore.YELLOW}📂 Escaneando JARs...")
        mod_data = self.scanner.scan()

        if not mod_data:
            print(f"{Fore.RED}❌ Nenhum arquivo de tradução encontrado nos JARs!")
            print(f"{Fore.RED}   Verifique se o caminho contém arquivos .jar válidos.\n")
            return

        print(f"{Fore.GREEN}✅ {len(mod_data)} arquivo(s) de tradução encontrado(s)\n")

        # Mostrar status dos provedores de tradução
        print(f"{Fore.CYAN}📡 Provedores de Tradução:")
        if self.translator.deepl_provider.available:
            print(f"{Fore.GREEN}   ✅ DeepL: Ativo")
        else:
            print(f"{Fore.YELLOW}   ⚠️  DeepL: Desativado")
        if self.translator.google_provider.available:
            print(f"{Fore.GREEN}   ✅ Google Translate: Ativo (Fallback)")
        else:
            print(f"{Fore.YELLOW}   ⚠️  Google Translate: Desativado")
        print()

        print(f"{Fore.YELLOW}🔄 Processando traduções...\n")

        pbar_mods = tqdm(mod_data.items(), desc=f"{Fore.CYAN}Mods", unit="mod", colour="cyan")

        processed_mods = 0
        skipped_mods = 0
        translated_keys = 0
        for file_path, data in pbar_mods:
            parts = file_path.split('/')
            modid = parts[1]
            output_file = self._output_file_for_mod(modid)

            if os.path.exists(output_file) and not self.overwrite:
                skipped_mods += 1
                pbar_mods.set_postfix({"mod": modid, "status": "skip"})
                pbar_mods.write(f"{Fore.YELLOW}↩️  Pulando {modid}: já existe em {output_file}")
                continue

            processed_mods += 1
            pbar_mods.set_postfix({"mod": modid, "status": "translate"})

            translated_data = {}
            pbar_keys = tqdm(data.items(), desc=f"  → {modid}", unit="key",
                           leave=False, colour="magenta")

            for key, value in pbar_keys:
                translated = self.translator.get_translation(value)
                if not translated:
                    translated = f"[NÃO TRADUZIDO] {value}"
                translated_data[key] = translated
                translated_keys += 1

            pbar_keys.close()

            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(translated_data, f, indent=2, ensure_ascii=False)

            pbar_mods.write(f"{Fore.GREEN}✅ {modid}: {len(translated_data)} chaves traduzidas")

        pbar_mods.close()

        stats = self.translator.get_stats()
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.GREEN}🎉 TRADUÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}📊 Resumo:")
        print(f"   • Mods processados: {processed_mods}")
        print(f"   • Mods ignorados (já existentes): {skipped_mods}")
        print(f"   • Total de chaves traduzidas: {translated_keys}")
        print(f"{Fore.YELLOW}📈 Fonte das Traduções:")
        print(f"   • Cache: {stats['cache_hits']} ({stats['cache_percent']:.1f}%)")
        print(f"   • DeepL: {stats['deepl_hits']} ({stats['deepl_percent']:.1f}%)")
        print(f"   • Google: {stats['google_hits']} ({stats['google_percent']:.1f}%)")
        print(f"   • Falhas: {stats['failed']}")
        print(f"   • Saída: {self.output_path}\n")
