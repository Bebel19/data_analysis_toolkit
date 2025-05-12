# scripts/script_addition.py

import csv
from scripts import ScriptInterface


class AdditionScript(ScriptInterface):
    def run(self, input_file=None, output_file=None, **kwargs):
        a = float(kwargs.get("a", 0))
        b = float(kwargs.get("b", 0))
        result = a + b

        with open(output_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["nombre1", "nombre2", "résultat"])
            writer.writerow([a, b, result])

    def get_metadata(self):
        return {
            "name": "Addition de deux nombres",
            "input_required": False,
            "parameters": {
                "a": {
                    "type": "float",
                    "default": 0.0,
                    "help": "Premier nombre"
                },
                "b": {
                    "type": "float",
                    "default": 0.0,
                    "help": "Deuxième nombre"
                }
            }
        }
