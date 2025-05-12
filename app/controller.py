# app/controller.py

import importlib
from app.script_loader import load_available_scripts
from utils.logger import logger


class ScriptController:
    def __init__(self):
        self.available_scripts = load_available_scripts()

    def get_script_names(self):
        return [script["name"] for script in self.available_scripts]

    def load_script(self, script_name):
        for script in self.available_scripts:
            if script["name"] == script_name:
                return script
        raise ValueError(f"Script non trouvé : {script_name}")

    def execute_script(self, script_name, input_file, output_file, params):
        logger.info(f"Chargement du script : {script_name}")

        script_entry = self.load_script(script_name)
        module_path = script_entry["module"]
        class_name = script_entry["class"]

        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError as e:
            raise ImportError(f"Module introuvable : {module_path}") from e

        try:
            script_class = getattr(module, class_name)
        except AttributeError as e:
            raise ImportError(f"Classe '{class_name}' non trouvée dans {module_path}") from e

        script_instance = script_class()

        from scripts import ScriptInterface
        if not isinstance(script_instance, ScriptInterface):
            raise TypeError(f"{class_name} ne respecte pas l'interface ScriptInterface")

        try:
            script_instance.run(input_file=input_file, output_file=output_file, **params)
            logger.info(f"Script exécuté avec succès : {script_name}")
        except Exception as e:
            logger.error(f"Échec d'exécution [{script_name}] : {e}")
            raise RuntimeError(f"Erreur pendant l'exécution de {script_name} : {e}") from e
