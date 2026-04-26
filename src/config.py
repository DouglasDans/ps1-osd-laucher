import configparser
import logging
import os

log = logging.getLogger("ps1.config")


def load_apps(ini_path: str) -> list[tuple[str, str]]:
    if not os.path.exists(ini_path):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {ini_path}")

    parser = configparser.ConfigParser()
    parser.optionxform = str  # preserva capitalização das chaves
    parser.read(ini_path)

    if "apps" not in parser:
        raise KeyError("Seção [apps] não encontrada no arquivo de configuração")

    apps = [(name, command) for name, command in parser["apps"].items()]
    log.info("apps.ini carregado: %d entradas", len(apps))
    return apps
