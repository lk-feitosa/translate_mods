import os
import json
from jar_scanner import JarScanner
from translator_core import TranslatorCore
from tqdm import tqdm
from colorama import Fore, Back, Style, init

init(autoreset=True)  # Inicializar colorama

class ModpackTranslator:
    def __init__(self, mods_path, output_path):
        self.scanner = JarScanner(mods_path)
        self.translator = TranslatorCore()
        self.output_path = output_path

    def run(self):
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}🌍 TRADUTOR DE MODPACK MINECRAFT - PT_BR")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        print(f"{Fore.YELLOW}📂 Escaneando JARs...")
        mod_data = self.scanner.scan()
        
        if not mod_data:
            print(f"{Fore.RED}❌ Nenhum arquivo de tradução encontrado nos JARs!")
            print(f"{Fore.RED}   Verifique se o caminho contém arquivos .jar válidos.\n")
            return
        
        print(f"{Fore.GREEN}✅ {len(mod_data)} arquivo(s) de tradução encontrado(s)\n")
        print(f"{Fore.YELLOW}🔄 Processando traduções...\n")
        
        total_keys = sum(len(data) for data in mod_data.values())
        pbar_mods = tqdm(mod_data.items(), desc=f"{Fore.CYAN}Mods", unit="mod", colour="cyan")
        
        translated_keys = 0
        for file_path, data in pbar_mods:
            # Estrutura: assets/<modid>/lang/en_us.json
            parts = file_path.split('/')
            modid = parts[1]
            
            pbar_mods.set_postfix({"mod": modid})
            
            # Prepara tradução (simplificada para exemplo)
            translated_data = {}
            pbar_keys = tqdm(data.items(), desc=f"  → {modid}", unit="key", 
                           leave=False, colour="magenta")
            
            for key, value in pbar_keys:
                # Tenta buscar do cache, se não tiver, traduz
                translated = self.translator.get_translation(value)
                if not translated:
                    translated = f"[PT_BR] {value}"  # Simulação
                    self.translator.save_translation(value, translated)
                translated_data[key] = translated
                translated_keys += 1
            
            pbar_keys.close()
            
            # Salva o arquivo de tradução
            output_file = os.path.join(self.output_path, f"assets/{modid}/lang/pt_br.json")
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(translated_data, f, indent=2, ensure_ascii=False)
            
            pbar_mods.write(f"{Fore.GREEN}✅ {modid}: {len(translated_data)} chaves traduzidas")
        
        pbar_mods.close()
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.GREEN}🎉 TRADUÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}📊 Resumo:")
        print(f"   • Mods processados: {len(mod_data)}")
        print(f"   • Total de chaves traduzidas: {translated_keys}")
        print(f"   • Saída: {self.output_path}\n")
