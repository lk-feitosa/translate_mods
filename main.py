import argparse
import os
import traceback

from colorama import Fore, init
from dotenv import load_dotenv

from modpack_translator import ModpackTranslator

load_dotenv()
init(autoreset=True)

BASE_MODS_DIR = os.path.join(".", "COLE_SEUS_MODS_OU_MODPACKS_AQUI")
BASE_OUTPUT_DIR = os.path.join(".", "mods_traduzidos")
SKIP_DIR_NAMES = {".git", "__pycache__", "venv", "node_modules"}


def list_modpacks(base_dir=BASE_MODS_DIR):
    if not os.path.isdir(base_dir):
        return []
    names = []
    for entry in sorted(os.listdir(base_dir)):
        if entry in SKIP_DIR_NAMES or entry.startswith("."):
            continue
        full = os.path.join(base_dir, entry)
        if os.path.isdir(full):
            names.append(entry)
    return names


def select_modpack(modpacks):
    print(f"\n{Fore.CYAN}--- Seleção de Modpack ---")
    print(f"0. {Fore.YELLOW}Traduzir TODOS os modpacks")
    for index, name in enumerate(modpacks, start=1):
        print(f"{index}. {name}")

    while True:
        raw = input(f"\n{Fore.WHITE}Escolha o número (0-{len(modpacks)}): ").strip()
        try:
            choice = int(raw)
        except ValueError:
            print(f"{Fore.RED}Digite um número.")
            continue
        if choice == 0:
            return "ALL"
        if 1 <= choice <= len(modpacks):
            return modpacks[choice - 1]
        print(f"{Fore.RED}Número inválido.")


def run_translator(modpack_name, overwrite):
    input_path = os.path.join(BASE_MODS_DIR, modpack_name)
    output_path = os.path.join(BASE_OUTPUT_DIR, modpack_name)

    print(f"\n{Fore.CYAN}🚀 Modpack: {Fore.WHITE}{modpack_name}")
    print(f"{Fore.CYAN}📂 Entrada: {input_path}")
    print(f"{Fore.CYAN}📂 Saída:   {output_path}\n")

    translator = ModpackTranslator(
        input_path,
        output_path,
        deepl_api_key=os.getenv("DEEPL_API_KEY"),
        overwrite=overwrite,
        pack_name=modpack_name,
    )
    translator.run()


def main():
    parser = argparse.ArgumentParser(
        description="Tradutor de modpacks Minecraft para PT-BR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Exemplos:
  python main.py
  python main.py --modpack deceasedcraft
  python main.py --modpack all --overwrite
""",
    )
    parser.add_argument(
        "--modpack",
        help="Nome da pasta dentro de COLE_SEUS_MODS_OU_MODPACKS_AQUI, ou 'all'",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Sobrescreve traduções existentes. Sem esta flag, continua de onde parou.",
    )
    args = parser.parse_args()

    modpacks = list_modpacks()
    if not modpacks:
        print(f"{Fore.RED}❌ Nenhuma pasta de modpack em {BASE_MODS_DIR}")
        print(f"{Fore.YELLOW}   Crie uma subpasta por modpack e coloque os .jar nela.")
        return

    selected = args.modpack
    if selected:
        if selected.lower() == "all":
            selected = "ALL"
        elif selected not in modpacks:
            print(f"{Fore.RED}❌ Modpack '{selected}' não encontrado.")
            print(f"{Fore.YELLOW}   Disponíveis: {', '.join(modpacks)}")
            return
    else:
        selected = select_modpack(modpacks)

    targets = modpacks if selected == "ALL" else [selected]

    try:
        for name in targets:
            run_translator(name, args.overwrite)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Cancelado. O progresso já gravado foi mantido.")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erro: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
