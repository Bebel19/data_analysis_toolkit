# app/script_loader.py

import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'scripts_config.yaml')

def load_available_scripts():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        scripts = yaml.safe_load(f)
        for script in scripts:
            validate_script_config(script)
        return scripts


def validate_script_config(script):
    required_keys = ["name", "module", "class", "input_required", "parameters"]
    for key in required_keys:
        if key not in script:
            raise ValueError(f"Champ '{key}' manquant dans un script.")

    if not isinstance(script["parameters"], dict):
        raise TypeError(f"'parameters' doit être un dictionnaire.")

    for param_name, param_meta in script["parameters"].items():
        for required in ["type", "default", "help"]:
            if required not in param_meta:
                raise ValueError(f"Le paramètre '{param_name}' est invalide (champ '{required}' manquant).")

        if param_meta["type"] not in ["int", "float", "string", "bool"]:
            raise ValueError(f"Type non supporté pour '{param_name}' : {param_meta['type']}")
