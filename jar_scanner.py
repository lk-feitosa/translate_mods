import zipfile
import os
import json
from colorama import Fore, Style
from tqdm import tqdm

class JarScanner:
    def __init__(self, mods_path):
        self.mods_path = mods_path

    def _find_jar_files(self):
        """Busca recursiva por arquivos .jar dentro da pasta do modpack."""
        jar_files = []
        for root, _, files in os.walk(self.mods_path):
            for filename in files:
                if filename.endswith('.jar'):
                    jar_files.append(os.path.join(root, filename))
        return sorted(jar_files)

    def scan(self):
        mod_data = {}
        
        # Verificar se diretório existe
        if not os.path.exists(self.mods_path):
            print(f"{Fore.RED}❌ Erro: Diretório '{self.mods_path}' não encontrado!")
            return mod_data
        
        jar_files = self._find_jar_files()
        
        if not jar_files:
            print(f"{Fore.YELLOW}⚠️  Aviso: Nenhum arquivo .jar encontrado em '{self.mods_path}'")
            return mod_data
        
        pbar = tqdm(jar_files, desc=f"{Fore.CYAN}Escaneando JARs", unit="jar", colour="cyan")
        
        for mod_path in pbar:
            filename = os.path.basename(mod_path)
            pbar.set_postfix({"arquivo": filename[:30]})
            try:
                with zipfile.ZipFile(mod_path, 'r') as jar:
                    for file in jar.namelist():
                        if file.startswith('assets/') and file.endswith('/lang/en_us.json'):
                            try:
                                with jar.open(file) as f:
                                    mod_data[file] = json.load(f)
                                    pbar.write(f"{Fore.GREEN}✅ Encontrado: {file}")
                            except json.JSONDecodeError as je:
                                pbar.write(f"{Fore.RED}❌ JSON inválido em {file}: {je}")
            except Exception as e:
                pbar.write(f"{Fore.RED}❌ Erro ao processar {filename}: {e}")
        
        pbar.close()
        return mod_data
