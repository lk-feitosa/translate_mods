
import argparse
import os
from dotenv import load_dotenv
from modpack_translator import ModpackTranslator
from colorama import Fore, init

# Carregar variáveis de ambiente
load_dotenv()

init(autoreset=True)
def main():
    parser = argparse.ArgumentParser(
        description="🌍 Tradutor Automático de Modpacks Minecraft para PT_BR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Exemplos de uso:
  python main.py --mods ./mods --output ./traducoes
  python main.py --mods "C:\\Minecraft\\mods" --output "C:\\Minecraft\\traducoes"
        """
    )
    parser.add_argument('--mods', required=True, help="Pasta contendo os arquivos .jar dos mods")
    parser.add_argument('--output', required=True, help="Pasta de saída para os arquivos traduzidos (pt_br.json)")
    parser.add_argument('--api-key', default=None, help="API key do DeepL (ou use variável DEEPL_API_KEY)")
    parser.add_argument('--overwrite', action='store_true', help="Sobrescreve arquivos já existentes. Por padrão, continua de onde parou e ignora os já gerados.")
    args = parser.parse_args()

    # Validar caminhos
    if not os.path.exists(args.mods):
        print(f"{Fore.RED}❌ Erro: Pasta de mods '{args.mods}' não encontrada!")
        return
    
    print(f"{Fore.CYAN}📁 Pasta de mods: {args.mods}")
    print(f"{Fore.CYAN}📁 Pasta de saída: {args.output}\n")
    
    try:
        # Usar API key do argumento ou carregar do .env
        api_key = args.api_key or os.getenv('DEEPL_API_KEY')
        translator = ModpackTranslator(args.mods, args.output, deepl_api_key=api_key, overwrite=args.overwrite)
        translator.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Tradução cancelada pelo usuário.")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erro durante a tradução: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
