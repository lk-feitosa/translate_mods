import json
import os
import zipfile

from colorama import Fore
from tqdm import tqdm


class JarScanner:
    def __init__(self, mods_path):
        self.mods_path = mods_path

    def _find_jar_files(self):
        """Busca recursiva por arquivos .jar dentro da pasta do modpack."""
        jar_files = []
        for root, _, files in os.walk(self.mods_path):
            for filename in files:
                if filename.lower().endswith(".jar"):
                    jar_files.append(os.path.join(root, filename))
        return sorted(jar_files)

    def _is_english_lang(self, file_path: str) -> bool:
        normalized = file_path.replace("\\", "/").lower()
        return normalized.startswith("assets/") and normalized.endswith("/lang/en_us.json")

    def scan(self):
        mod_data = {}

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
                with zipfile.ZipFile(mod_path, "r") as jar:
                    for file in jar.namelist():
                        if not self._is_english_lang(file):
                            continue
                        try:
                            with jar.open(file) as handle:
                                loaded = json.load(handle)
                            if not isinstance(loaded, dict):
                                pbar.write(f"{Fore.YELLOW}⚠️  Ignorado (não é objeto JSON): {file}")
                                continue
                            canonical = file.replace("\\", "/")
                            if canonical in mod_data:
                                mod_data[canonical].update(loaded)
                            else:
                                mod_data[canonical] = loaded
                            pbar.write(f"{Fore.GREEN}✅ Encontrado: {canonical}")
                        except json.JSONDecodeError as je:
                            pbar.write(f"{Fore.RED}❌ JSON inválido em {file}: {je}")
            except zipfile.BadZipFile:
                pbar.write(f"{Fore.RED}❌ JAR inválido: {filename}")
            except Exception as e:
                pbar.write(f"{Fore.RED}❌ Erro ao processar {filename}: {e}")

        pbar.close()
        return mod_data
