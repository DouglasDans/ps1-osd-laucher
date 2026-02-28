import configparser
import os


def load_apps(ini_path: str) -> list[tuple[str, str]]:
    if not os.path.exists(ini_path):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {ini_path}")

    parser = configparser.ConfigParser()
    parser.optionxform = str  # preserva capitalização das chaves
    parser.read(ini_path)

    if "apps" not in parser:
        raise KeyError("Seção [apps] não encontrada no arquivo de configuração")

    return [(name, command) for name, command in parser["apps"].items()]
