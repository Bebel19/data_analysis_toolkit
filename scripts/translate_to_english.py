import pandas as pd
from langdetect import detect
from deep_translator import GoogleTranslator
from scripts import ScriptInterface
from utils.logger import logger

class TranslateToEnglish(ScriptInterface):
    def run(self, input_file=None, output_file=None, **kwargs):
        df = pd.read_csv(input_file, sep=",", encoding="utf-8")
        df.columns = df.columns.str.strip()  # Nettoyage des noms de colonnes

        df["TEXT_ENGLISH"] = df["TEXT"].astype(str).apply(self.translate_if_needed)
        df.to_csv(output_file, sep=",", encoding="utf-8", index=False)
        logger.info(f"Traduction terminée. Fichier écrit : {output_file}")

    def translate_if_needed(self, text):
        try:
            lang = detect(text)
            if lang == 'en':
                return text
            return GoogleTranslator(source=lang, target='en').translate(text)
        except Exception as e:
            logger.warning(f"Erreur de traduction : {e}")
            return ""

    def get_metadata(self):
        return {
            "name": "Traduction vers l'anglais",
            "input_required": True,
            "parameters": {}  # Aucun paramètre utilisateur pour l'instant
        }
